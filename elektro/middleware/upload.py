"""Upload middleware for the funcs API.

This middleware intercepts serialized operation variables and uploads
uploadable types (ArrayLike, TraceLike, ParquetLike, FileLike, etc.) to the
datalayer *before* the operation reaches the rath link chain.

It provides both sync and async paths:
    - Sync (process_variables): Uses obstore for S3 uploads, called from execute().
    - Async (aprocess_variables): Uses obstore, called from aexecute().

Credential acquisition always goes through rath.query/aquery directly
(bypassing the middleware itself) to avoid infinite recursion.
"""

import asyncio
import logging
from functools import partial
from typing import Any, Dict, Tuple, Type, Union, TYPE_CHECKING

from concurrent.futures import ThreadPoolExecutor
from koil import unkoil
from pydantic import ConfigDict, Field

from elektro.middleware.base import FuncsMiddleware
from elektro.scalars import (
    ArrayLike,
    BigFileLike,
    FileLike,
    MeshLike,
    ParquetLike,
    TraceLike,
)
from elektro.io.upload import (
    # Async paths (obstore)
    aupload_bigfile,
    aupload_xarray,
    aupload_parquet,
    astore_mesh_file,
    # Sync paths (obstore)
    upload_xarray,
    upload_parquet,
    upload_bigfile,
    store_mesh_file,
)

from elektro.datalayer import DataLayer

if TYPE_CHECKING:
    from elektro.api.schema import (
        BigFileUploadGrant,
        ParquetUploadGrant,
        ZarrUploadGrant,
    )
    from elektro.rath import ElektroRath

from rath.turms.funcs import TOperation


logger = logging.getLogger(__name__)


# ========================================================================
# Recursive applicators (async and sync)
# ========================================================================


async def _apply_recursive_async(
    func,  # noqa: ANN001
    obj: Any,  # noqa: ANN401
    typeguard: Union[Type[Any], Tuple[Type[Any], ...]],
) -> Any:  # noqa: ANN401
    """Recursively applies an async function to matching elements in a nested structure."""
    if isinstance(obj, dict):
        return {k: await _apply_recursive_async(func, v, typeguard) for k, v in obj.items()}
    elif isinstance(obj, list):
        return await asyncio.gather(
            *[_apply_recursive_async(func, elem, typeguard) for elem in obj]
        )
    elif isinstance(obj, tuple):
        return tuple(
            await asyncio.gather(*[_apply_recursive_async(func, elem, typeguard) for elem in obj])
        )
    elif isinstance(obj, typeguard):
        return await func(obj)
    else:
        return obj


def _apply_recursive_sync(
    func,  # noqa: ANN001
    obj: Any,  # noqa: ANN401
    typeguard: Union[Type[Any], Tuple[Type[Any], ...]],
) -> Any:  # noqa: ANN401
    """Recursively applies a sync function to matching elements in a nested structure."""
    if isinstance(obj, dict):
        return {k: _apply_recursive_sync(func, v, typeguard) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_apply_recursive_sync(func, elem, typeguard) for elem in obj]
    elif isinstance(obj, tuple):
        return tuple(_apply_recursive_sync(func, elem, typeguard) for elem in obj)
    elif isinstance(obj, typeguard):
        return func(obj)
    else:
        return obj


class UploadMiddleware(FuncsMiddleware):
    """Middleware that uploads supported data types to the datalayer.

    This middleware walks the serialized variables dict, finds instances of
    uploadable scalar types (ArrayLike, TraceLike, ParquetLike, FileLike,
    BigFileLike, MeshLike), uploads them to S3, and replaces them with their
    store IDs.

    Provides two paths:
        - **Sync** (``process_variables``): Uses obstore for S3 operations.
          Called when the user invokes ``execute()`` / ``subscribe()``.
        - **Async** (``aprocess_variables``): Uses obstore.
          Called when the user invokes ``aexecute()`` / ``asubscribe()``.

    Args:
        datalayer: The DataLayer instance for S3 connectivity.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    datalayer: DataLayer

    executor: ThreadPoolExecutor = Field(
        default_factory=lambda: ThreadPoolExecutor(max_workers=4), exclude=True
    )
    _executor_session: Any = None
    _cached_datalayer_url: str | None = None

    async def aenter(self) -> None:
        """Enter the middleware context, initializing the thread pool."""
        self._executor_session = self.executor.__enter__()

    async def aexit(self) -> None:
        """Exit the middleware context, shutting down the thread pool."""
        self.executor.__exit__(None, None, None)

    # ====================================================================
    # Credential acquisition helpers (sync)
    # ====================================================================

    def _get_zarr_credentials(
        self, key: str, datalayer: str, rath: "ElektroRath"
    ) -> "ZarrUploadGrant":
        """Get zarr upload credentials synchronously."""
        from elektro.api.schema import (
            RequestZarrUploadInput,
            RequestZarrUploadMutation,
        )

        x = rath.query(
            RequestZarrUploadMutation.Meta.document,
            RequestZarrUploadMutation.Arguments(input=RequestZarrUploadInput()).model_dump(
                by_alias=True, exclude_unset=True
            ),
        )
        return RequestZarrUploadMutation(**x.data).request_zarr_upload

    def _finish_zarr_upload(self, store_id: str, rath: "ElektroRath") -> None:
        """Finish zarr upload synchronously."""
        from elektro.api.schema import (
            FinishZarrUploadInput,
            FinishZarrUploadMutation,
        )

        rath.query(
            FinishZarrUploadMutation.Meta.document,
            FinishZarrUploadMutation.Arguments(
                input=FinishZarrUploadInput(storeId=store_id, valid=True)
            ).model_dump(by_alias=True, exclude_unset=True),
        )

    def _get_table_credentials(
        self, key: str, datalayer: str, rath: "ElektroRath"
    ) -> "ParquetUploadGrant":
        """Get table upload credentials synchronously."""
        from elektro.api.schema import (
            RequestParquetUploadInput,
            RequestParquetUploadMutation,
        )

        x = rath.query(
            RequestParquetUploadMutation.Meta.document,
            RequestParquetUploadMutation.Arguments(input=RequestParquetUploadInput()).model_dump(
                by_alias=True, exclude_unset=True
            ),
        )
        return RequestParquetUploadMutation(**x.data).request_parquet_upload

    def _get_bigfile_credentials(
        self, file: Union[FileLike, BigFileLike, MeshLike], datalayer: str, rath: "ElektroRath"
    ) -> "BigFileUploadGrant":
        """Get big file upload credentials synchronously."""
        from elektro.api.schema import (
            RequestBigFileUploadInput,
            RequestBigfileUploadMutation,
        )

        original_file_name = getattr(file, "file_name", getattr(file, "key", "upload"))

        x = rath.query(
            RequestBigfileUploadMutation.Meta.document,
            RequestBigfileUploadMutation.Arguments(
                input=RequestBigFileUploadInput(originalFileName=original_file_name)
            ).model_dump(by_alias=True, exclude_unset=True),
        )
        return RequestBigfileUploadMutation(**x.data).request_bigfile_upload

    # ====================================================================
    # Credential acquisition helpers (async)
    # ====================================================================

    async def _aget_zarr_credentials(
        self, key: str, datalayer: str, rath: "ElektroRath"
    ) -> "ZarrUploadGrant":
        """Get zarr upload credentials asynchronously."""
        from elektro.api.schema import (
            RequestZarrUploadInput,
            RequestZarrUploadMutation,
        )

        x = await rath.aquery(
            RequestZarrUploadMutation.Meta.document,
            RequestZarrUploadMutation.Arguments(input=RequestZarrUploadInput()).model_dump(
                by_alias=True, exclude_unset=True
            ),
        )
        return RequestZarrUploadMutation(**x.data).request_zarr_upload

    async def _afinish_zarr_upload(self, store_id: str, rath: "ElektroRath") -> None:
        """Finish zarr upload asynchronously."""
        from elektro.api.schema import (
            FinishZarrUploadInput,
            FinishZarrUploadMutation,
        )

        await rath.aquery(
            FinishZarrUploadMutation.Meta.document,
            FinishZarrUploadMutation.Arguments(
                input=FinishZarrUploadInput(storeId=store_id, valid=True)
            ).model_dump(by_alias=True, exclude_unset=True),
        )

    async def _aget_table_credentials(
        self, key: str, datalayer: str, rath: "ElektroRath"
    ) -> "ParquetUploadGrant":
        """Get table upload credentials asynchronously."""
        from elektro.api.schema import (
            RequestParquetUploadInput,
            RequestParquetUploadMutation,
        )

        x = await rath.aquery(
            RequestParquetUploadMutation.Meta.document,
            RequestParquetUploadMutation.Arguments(input=RequestParquetUploadInput()).model_dump(
                by_alias=True, exclude_unset=True
            ),
        )
        return RequestParquetUploadMutation(**x.data).request_parquet_upload

    async def _aget_bigfile_credentials(
        self, file: Union[FileLike, BigFileLike, MeshLike], datalayer: str, rath: "ElektroRath"
    ) -> "BigFileUploadGrant":
        """Get big file upload credentials asynchronously."""
        from elektro.api.schema import (
            RequestBigFileUploadInput,
            RequestBigfileUploadMutation,
        )

        original_file_name = getattr(file, "file_name", getattr(file, "key", "upload"))

        x = await rath.aquery(
            RequestBigfileUploadMutation.Meta.document,
            RequestBigfileUploadMutation.Arguments(
                input=RequestBigFileUploadInput(originalFileName=original_file_name)
            ).model_dump(by_alias=True, exclude_unset=True),
        )
        return RequestBigfileUploadMutation(**x.data).request_bigfile_upload

    # ====================================================================
    # Sync upload methods (obstore path)
    # ====================================================================

    def get_datalayer_url(self) -> str:
        """Helper to get the datalayer endpoint URL."""
        if self._cached_datalayer_url is None:
            self._cached_datalayer_url = unkoil(self.datalayer.get_endpoint_url)
        return self._cached_datalayer_url

    def _upload_xarray(
        self, datalayer: "DataLayer", rath: "ElektroRath", xarray: Union[ArrayLike, TraceLike]
    ) -> str:
        """Upload an xarray synchronously via obstore."""
        endpoint_url = self.get_datalayer_url()

        credentials = self._get_zarr_credentials(xarray.key, endpoint_url, rath)
        store_id = upload_xarray(xarray, credentials, datalayer)
        self._finish_zarr_upload(store_id, rath)
        return store_id

    def _upload_parquet(
        self,
        datalayer: "DataLayer",
        rath: "ElektroRath",
        parquet_input: ParquetLike,
    ) -> str:
        """Upload a Parquet file synchronously."""
        endpoint_url = self.get_datalayer_url()

        credentials = self._get_table_credentials(parquet_input.key, endpoint_url, rath)
        return upload_parquet(parquet_input, credentials, datalayer)

    def _upload_bigfile(
        self, datalayer: "DataLayer", rath: "ElektroRath", file: Union[FileLike, BigFileLike]
    ) -> str:
        """Upload a big file synchronously via obstore."""
        endpoint_url = self.get_datalayer_url()

        credentials = self._get_bigfile_credentials(file, endpoint_url, rath)
        return upload_bigfile(file, credentials, datalayer)

    def _store_mesh(self, datalayer: "DataLayer", rath: "ElektroRath", mesh: MeshLike) -> str:
        """Store a mesh file synchronously via obstore."""
        endpoint_url = self.get_datalayer_url()

        credentials = self._get_bigfile_credentials(mesh, endpoint_url, rath)
        return store_mesh_file(mesh, credentials, datalayer)

    # ====================================================================
    # Async upload methods (obstore path)
    # ====================================================================

    async def _aupload_xarray(
        self, datalayer: "DataLayer", rath: "ElektroRath", xarray: Union[ArrayLike, TraceLike]
    ) -> str:
        """Upload an xarray asynchronously."""
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self._aget_zarr_credentials(xarray.key, endpoint_url, rath)
        store_id = await aupload_xarray(xarray, credentials, datalayer)
        await self._afinish_zarr_upload(store_id, rath)
        return store_id

    async def _aupload_parquet(
        self,
        datalayer: "DataLayer",
        rath: "ElektroRath",
        parquet_input: ParquetLike,
    ) -> str:
        """Upload a Parquet file asynchronously."""
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self._aget_table_credentials(parquet_input.key, endpoint_url, rath)
        return await aupload_parquet(parquet_input, credentials, datalayer, self._executor_session)

    async def _aupload_bigfile(
        self, datalayer: "DataLayer", rath: "ElektroRath", file: Union[FileLike, BigFileLike]
    ) -> str:
        """Upload a big file asynchronously."""
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self._aget_bigfile_credentials(file, endpoint_url, rath)
        return await aupload_bigfile(file, credentials, datalayer)

    async def _astore_mesh(
        self, datalayer: "DataLayer", rath: "ElektroRath", mesh: MeshLike
    ) -> str:
        """Store a mesh file asynchronously."""
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self._aget_bigfile_credentials(mesh, endpoint_url, rath)
        return await astore_mesh_file(mesh, credentials, datalayer)

    # ====================================================================
    # Core middleware methods
    # ====================================================================

    def process_variables(
        self,
        variables: Dict[str, Any],
        operation: Type[TOperation],
        rath: "ElektroRath",
    ) -> Dict[str, Any]:
        """Process serialized variables synchronously (obstore path).

        Called from ``execute()`` and ``subscribe()``. Uses sync I/O
        for all S3 uploads.

        Args:
            variables: The serialized variables dict.
            operation: The operation type being executed.
            rath: The rath client instance.

        Returns:
            The variables dict with uploadable types replaced by store IDs.
        """
        datalayer = self.datalayer

        variables = _apply_recursive_sync(
            partial(self._upload_xarray, datalayer, rath),
            variables,
            (ArrayLike, TraceLike),
        )
        variables = _apply_recursive_sync(
            partial(self._upload_parquet, datalayer, rath),
            variables,
            (ParquetLike,),
        )
        variables = _apply_recursive_sync(
            partial(self._upload_bigfile, datalayer, rath),
            variables,
            (FileLike, BigFileLike),
        )
        variables = _apply_recursive_sync(
            partial(self._store_mesh, datalayer, rath),
            variables,
            MeshLike,
        )

        return variables

    async def aprocess_variables(
        self,
        variables: Dict[str, Any],
        operation: Type[TOperation],
        rath: "ElektroRath",
    ) -> Dict[str, Any]:
        """Process serialized variables asynchronously (obstore path).

        Called from ``aexecute()`` and ``asubscribe()``. Uses async I/O
        for all S3 uploads.

        Args:
            variables: The serialized variables dict.
            operation: The operation type being executed.
            rath: The rath client instance.

        Returns:
            The variables dict with uploadable types replaced by store IDs.
        """
        datalayer = self.datalayer

        variables = await _apply_recursive_async(
            partial(self._aupload_xarray, datalayer, rath),
            variables,
            (ArrayLike, TraceLike),
        )
        variables = await _apply_recursive_async(
            partial(self._aupload_parquet, datalayer, rath),
            variables,
            (ParquetLike,),
        )
        variables = await _apply_recursive_async(
            partial(self._aupload_bigfile, datalayer, rath),
            variables,
            (FileLike, BigFileLike),
        )
        variables = await _apply_recursive_async(
            partial(self._astore_mesh, datalayer, rath),
            variables,
            MeshLike,
        )

        return variables

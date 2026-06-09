"""Helpers for reading and writing Elektro S3 objects via obstore."""

import asyncio
from io import BytesIO
from typing import TYPE_CHECKING, Protocol

import numpy as np
import obstore
import xarray as xr
import zarr
from obstore.store import ObjectStore as ObstoreObjectStore, S3Store
from zarr.storage import ObjectStore as ZarrObjectStore, StorePath

from elektro.scalars import is_dask_array
from elektro.utils import rechunk


if TYPE_CHECKING:
    from pyarrow import Table  # type: ignore
    from obstore.store import ClientConfig, RetryConfig
    from elektro.datalayer import DataLayer


class S3UploadGrantLike(Protocol):
    """Protocol for grants that carry S3 credentials and object coordinates."""

    @property
    def access_key(self) -> str: ...  # noqa: D102

    @property
    def secret_key(self) -> str: ...  # noqa: D102

    @property
    def session_token(self) -> str: ...  # noqa: D102

    @property
    def bucket(self) -> str: ...  # noqa: D102

    @property
    def key(self) -> str: ...  # noqa: D102


def create_s3_store(
    endpoint_url: str,
    grant: "S3UploadGrantLike",
    client_options: "ClientConfig | None" = None,
    retry_config: "RetryConfig | None" = None,
) -> S3Store:
    """Create an obstore S3 client from an Elektro grant and endpoint."""
    normalized_client_options: dict[str, object] = dict(client_options or {})
    if endpoint_url.startswith("http://"):
        normalized_client_options.setdefault("allow_http", True)

    store_kwargs: dict[str, object] = {
        "access_key_id": grant.access_key,
        "secret_access_key": grant.secret_key,
        "endpoint": endpoint_url,
        "virtual_hosted_style_request": False,
        "client_options": normalized_client_options or None,
        "retry_config": retry_config,
    }
    if grant.session_token:
        store_kwargs["session_token"] = grant.session_token

    return S3Store(
        grant.bucket,
        **store_kwargs,
    )


def create_zarr_store_path(endpoint_url: str, grant: "S3UploadGrantLike") -> StorePath:
    """Create a Zarr store path rooted at the granted S3 prefix."""
    zarr_store = ZarrObjectStore(create_s3_store(endpoint_url, grant))
    return StorePath(zarr_store, grant.key)


async def acreate_s3_store(
    grant: "S3UploadGrantLike",
    datalayer: "DataLayer",
    client_options: "ClientConfig | None" = None,
    retry_config: "RetryConfig | None" = None,
) -> S3Store:
    """Create an obstore S3 client asynchronously using the active datalayer."""
    endpoint_url = await datalayer.get_endpoint_url()

    return create_s3_store(
        endpoint_url,
        grant,
        client_options=client_options,
        retry_config=retry_config,
    )


_CTZYX_DIMS = {"c", "t", "z", "y", "x"}


def _generic_chunk_shape(array: xr.DataArray, chunksize_in_bytes: int = 20_000_000) -> tuple[int, ...]:
    """Compute a ~20MB zarr chunk shape for an arbitrarily-labelled DataArray.

    Used for the generic dataset path where dims are not the canonical ``ctzyx``
    set and their semantics are unknown. Walks dimensions inner→outer (C-order),
    keeping the innermost dims whole while they fit the byte budget, chunking the
    first dimension that overflows, and leaving the outer dims at 1. The result is
    always valid (``chunk[i] <= shape[i]``) regardless of dimension order/meaning.
    """
    shape = array.shape
    chunk = [1] * len(shape)
    bytes_per_chunk = array.dtype.itemsize
    for i in reversed(range(len(shape))):
        if bytes_per_chunk * shape[i] <= chunksize_in_bytes:
            chunk[i] = shape[i]
            bytes_per_chunk *= shape[i]
        else:
            chunk[i] = max(1, chunksize_in_bytes // bytes_per_chunk)
            break
    return tuple(int(c) for c in chunk)


def _zarr_chunk_shape(array: xr.DataArray) -> tuple[int, ...]:
    """Compute an on-disk zarr chunk shape (~20MB) aligned to the array dims.

    Canonical 5D ``ctzyx`` arrays use the ``ctzyx``-aware :func:`rechunk` heuristic.
    Arbitrarily-labelled arrays (the generic ``ArrayLike``/``TraceLike`` path) fall
    back to a semantics-agnostic chunker. Returns a chunk tuple in the array's own
    dimension order so it can be passed straight to zarr.
    """
    if set(array.dims) == _CTZYX_DIMS:
        chunks = rechunk(
            dict(array.sizes), itemsize=array.dtype.itemsize, chunksize_in_bytes=20_000_000
        )
        return tuple(int(chunks[dim]) for dim in array.dims)
    return _generic_chunk_shape(array)


def write_dataarray_to_zarr(store_path: StorePath, array: xr.DataArray) -> None:
    """Write a DataArray to a zarr v3 array synchronously with explicit chunks.

    Dask-backed arrays are streamed chunk-by-chunk via ``dask.array.store`` so the
    full array is never materialised in memory; numpy arrays are written directly.
    """
    chunk_shape = _zarr_chunk_shape(array)
    zarr_array = zarr.create_array(
        store_path,
        shape=array.shape,
        chunks=chunk_shape,
        dtype=array.dtype,
        dimension_names=[str(dim) for dim in array.dims],
        zarr_format=3,
        overwrite=True,
    )
    data = array.data
    if is_dask_array(data):
        from dask.array.core import store as dask_store

        # Align dask blocks to the zarr chunk grid so concurrent, lock-free writes
        # never target the same chunk from two blocks (which would race/corrupt).
        data = data.rechunk(chunk_shape)
        dask_store(data, zarr_array, lock=False)
    else:
        zarr_array[...] = np.asarray(data)


async def awrite_dataarray_to_zarr(store_path: StorePath, array: xr.DataArray) -> None:
    """Write a DataArray to a zarr v3 array without blocking the event loop.

    Delegates to the synchronous streaming writer in a worker thread so that
    dask-backed arrays are streamed to zarr chunk-by-chunk (via ``dask.array.store``)
    and are never fully materialised in memory. ``dask.array.store`` runs the dask
    scheduler synchronously, so it must not be awaited directly on the event loop.
    """
    await asyncio.to_thread(write_dataarray_to_zarr, store_path, array)


async def awrite_xarray_to_obstore(
    da: xr.DataArray,
    grant: "S3UploadGrantLike",
    datalayer: "DataLayer",
) -> None:
    """
    Asynchronously write an xarray dataset to S3 via obstore and Zarr.
    """
    store_path = create_zarr_store_path(await datalayer.get_endpoint_url(), grant)
    await awrite_dataarray_to_zarr(store_path, da)


def get_bytes(store: ObstoreObjectStore, path: str) -> bytes:
    """Read an object fully into memory."""
    return bytes(obstore.get(store, path).bytes())


async def aget_bytes(store: ObstoreObjectStore, path: str) -> bytes:
    """Read an object fully into memory asynchronously."""
    return bytes((await obstore.get_async(store, path)).bytes())


class ParquetDatasetViaObstore:
    """Minimal parquet dataset adapter backed by obstore."""

    def __init__(self, store: ObstoreObjectStore, path: str) -> None:
        """Bind a parquet object path to a concrete obstore-backed S3 client."""
        self.store = store
        self.path = path

    def read_pandas(self) -> "Table":
        """Read the parquet object into a pyarrow table."""
        import pyarrow.parquet as pq  # type: ignore

        return pq.read_table(BytesIO(get_bytes(self.store, self.path)))

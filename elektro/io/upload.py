"""Module for uploading various data types to a DataLayer.

Provides both async and sync upload paths via obstore:
    - Async: aupload_xarray, aupload_parquet, aupload_bigfile, astore_mesh_file
    - Sync: upload_xarray, upload_parquet, upload_bigfile, store_mesh_file
"""

from io import BytesIO
import logging
from typing import TYPE_CHECKING, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor

import obstore
from elektro.scalars import (
    ArrayLike,
    BigFileLike,
    FileLike,
    MeshLike,
    ParquetLike,
    TraceLike,
)

from .errors import UploadError


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from elektro.api.schema import (
        ZarrUploadGrant,
        ParquetUploadGrant,
        BigFileUploadGrant,
    )
    from elektro.datalayer import DataLayer


# ========================================================================
# Async upload functions (obstore)
# ========================================================================


async def astore_xarray_input(
    xarray: Union[ArrayLike, TraceLike],
    credentials: "ZarrUploadGrant",
    endpoint_url: str,
) -> str:
    """Stores an xarray in the DataLayer"""
    from elektro.io.obstore import awrite_dataarray_to_zarr, create_zarr_store_path

    array = xarray.value
    store_path = create_zarr_store_path(endpoint_url, credentials)

    try:
        logger.debug(
            f"Uploading zarr t to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        await awrite_dataarray_to_zarr(store_path, array)
        logger.info(
            f"Successfully uploaded zarr to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}"
        )

        return credentials.store
    except Exception as e:
        raise UploadError(
            f"Error while uploading to s3://{credentials.bucket}/{credentials.key} on {endpoint_url}"
        ) from e


def _store_parquet_input(
    parquet_input: ParquetLike,
    credentials: "ParquetUploadGrant",
    endpoint_url: str,
) -> str:
    """Store a parquet table in the DataLayer via obstore."""
    import pyarrow.parquet as pq  # type: ignore
    from pyarrow import Table  # type: ignore
    from elektro.io.obstore import create_s3_store

    store = create_s3_store(endpoint_url, credentials)

    table: Table = Table.from_pandas(parquet_input.value)  # type: ignore
    buffer = BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)

    s3_path = f"s3://{credentials.bucket}/{credentials.key}"
    try:
        logger.debug(
            f"Uploading parquet to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        obstore.put(store, credentials.key, buffer)
        logger.info(
            f"Successfully uploaded parquet to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}"
        )
        return credentials.store
    except Exception as e:
        raise UploadError(f"Error while uploading to {s3_path}") from e


async def astore_mesh_file(
    mesh: MeshLike,
    credentials: "BigFileUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Store a mesh file in the DataLayer asynchronously via obstore."""
    from elektro.io.obstore import create_s3_store

    endpoint_url = await datalayer.get_endpoint_url()
    store = create_s3_store(endpoint_url, credentials)

    try:
        logger.debug(
            f"Uploading mesh to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        await obstore.put_async(store, credentials.key, mesh.value)
        logger.info(
            f"Successfully uploaded mesh to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}"
        )
        return credentials.store
    except Exception as e:
        raise UploadError(
            f"Error while uploading to s3://{credentials.bucket}/{credentials.key} on {endpoint_url}"
        ) from e


async def aupload_bigfile(
    file: Union[FileLike, BigFileLike],
    credentials: "BigFileUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload a big file to the DataLayer asynchronously via obstore."""
    from elektro.io.obstore import create_s3_store

    endpoint_url = await datalayer.get_endpoint_url()
    store = create_s3_store(endpoint_url, credentials)

    try:
        logger.debug(
            f"Uploading file to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        await obstore.put_async(store, credentials.key, file.value)
        logger.info(
            f"Successfully uploaded file to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}"
        )
        return credentials.store
    except Exception as e:
        raise UploadError(
            f"Error while uploading to s3://{credentials.bucket}/{credentials.key} on {endpoint_url}"
        ) from e


async def aupload_xarray(
    array: Union[ArrayLike, TraceLike],
    credentials: "ZarrUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload an xarray to the DataLayer asynchronously via obstore."""
    return await astore_xarray_input(array, credentials, await datalayer.get_endpoint_url())


async def aupload_parquet(
    parquet: ParquetLike,
    credentials: "ParquetUploadGrant",
    datalayer: "DataLayer",
    executor: ThreadPoolExecutor,
) -> str:
    """Upload a parquet table to the DataLayer asynchronously via a thread executor."""
    co_future = executor.submit(
        _store_parquet_input, parquet, credentials, await datalayer.get_endpoint_url()
    )
    return await asyncio.wrap_future(co_future)


# ========================================================================
# Sync upload functions (obstore)
# ========================================================================


def _store_xarray_via_obstore(
    xarray: Union[ArrayLike, TraceLike],
    credentials: "ZarrUploadGrant",
    endpoint_url: str,
) -> str:
    """Stores an xarray in the DataLayer synchronously via obstore/zarr."""
    from elektro.io.obstore import create_zarr_store_path, write_dataarray_to_zarr

    store_path = create_zarr_store_path(endpoint_url, credentials)

    try:
        logger.debug(
            f"Uploading zarr (sync/obstore) to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        write_dataarray_to_zarr(store_path, xarray.value)
        logger.info(
            f"Successfully uploaded zarr (sync/obstore) to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}"
        )
        return credentials.store
    except Exception as e:
        raise UploadError(
            f"Error while uploading to s3://{credentials.bucket}/{credentials.key} on {endpoint_url}"
        ) from e


def _store_bigfile_via_obstore(
    file: Union[FileLike, BigFileLike],
    credentials: "BigFileUploadGrant",
    endpoint_url: str,
) -> str:
    """Store a big file in the DataLayer synchronously via obstore."""
    from elektro.io.obstore import create_s3_store

    store = create_s3_store(endpoint_url, credentials)

    try:
        logger.debug(
            f"Uploading file (sync/obstore) to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        obstore.put(store, credentials.key, file.value)
        logger.info(
            f"Successfully uploaded file (sync/obstore) to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}"
        )
        return credentials.store
    except Exception as e:
        raise UploadError(
            f"Error while uploading to s3://{credentials.bucket}/{credentials.key} on {endpoint_url}"
        ) from e


def _store_mesh_via_obstore(
    mesh: MeshLike,
    credentials: "BigFileUploadGrant",
    endpoint_url: str,
) -> str:
    """Store a mesh file in the DataLayer synchronously via obstore."""
    from elektro.io.obstore import create_s3_store

    store = create_s3_store(endpoint_url, credentials)

    try:
        logger.debug(
            f"Uploading mesh (sync/obstore) to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        obstore.put(store, credentials.key, mesh.value)
        logger.info(
            f"Successfully uploaded mesh (sync/obstore) to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}"
        )
        return credentials.store
    except Exception as e:
        raise UploadError(
            f"Error while uploading to s3://{credentials.bucket}/{credentials.key} on {endpoint_url}"
        ) from e


def upload_xarray(
    array: Union[ArrayLike, TraceLike],
    credentials: "ZarrUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload an xarray synchronously via obstore."""
    return _store_xarray_via_obstore(array, credentials, datalayer.endpoint_url)


def upload_parquet(
    parquet: ParquetLike,
    credentials: "ParquetUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload a parquet file synchronously."""
    return _store_parquet_input(parquet, credentials, datalayer.endpoint_url)


def upload_bigfile(
    file: Union[FileLike, BigFileLike],
    credentials: "BigFileUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload a big file synchronously via obstore."""
    return _store_bigfile_via_obstore(file, credentials, datalayer.endpoint_url)


def store_mesh_file(
    mesh: MeshLike,
    credentials: "BigFileUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Store a mesh file synchronously via obstore."""
    return _store_mesh_via_obstore(mesh, credentials, datalayer.endpoint_url)

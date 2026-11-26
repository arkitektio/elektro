"""Module for uploading various data types to a DataLayer.

Provides both async and sync upload paths via obstore:
    - Async: aupload_xarray, aupload_parquet, aupload_bigfile, astore_mesh_file,
      astore_sparse_matrix
    - Sync: upload_xarray, upload_parquet, upload_bigfile, store_mesh_file,
      store_sparse_matrix
"""

import asyncio
import io
import logging
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, cast

import obstore

from elektro.io.obstore import (
    awrite_dataarray_to_zarr,
    create_s3_store,
    create_zarr_store_path,
    write_dataarray_to_zarr,
)
from elektro.scalars import (
    ArrayLike,
    BigFileLike,
    FileLike,
    MeshLike,
    ParquetLike,
    SporadikLike,
    _sporadik,
)

from .errors import UploadError

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from elektro.api.schema import (
        BigFileUploadGrant,
        ParquetUploadGrant,
        SparseUploadGrant,
        ZarrUploadGrant,
    )
    from elektro.datalayer import DataLayer


# ========================================================================
# Async upload functions (obstore)
# ========================================================================


async def astore_xarray_input(
    xarray: ArrayLike,
    credentials: "ZarrUploadGrant",
    endpoint_url: str,
    proxy: str | None = None,
    certificates: list[str] | None = None,
) -> str:
    """Stores an xarray in the DataLayer"""
    array = xarray.value
    store_path = create_zarr_store_path(
        endpoint_url, credentials, proxy=proxy, certificates=certificates
    )

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


def _parquet_payload(value: object) -> "tuple[object, Path | None]":
    """What to hand ``obstore.put``, and the scratch file to delete afterwards.

    Vendored from mikro. A ``Path`` is streamed as-is; a ``Table`` or ``RecordBatchReader`` is
    written to a scratch file (a second in-memory copy of the largest object in the process is
    the thing worth avoiding); a ``DataFrame`` is serialized in memory, the small case.
    """
    import pyarrow.parquet as pq  # type: ignore
    from pyarrow import RecordBatchReader, Table  # type: ignore

    if isinstance(value, Path):
        return value, None

    if isinstance(value, (Table, RecordBatchReader)):
        handle, name = tempfile.mkstemp(suffix=".parquet", prefix="elektro-parquet-")
        os.close(handle)
        scratch = Path(name)
        try:
            if isinstance(value, Table):
                pq.write_table(value, scratch)
            else:
                with pq.ParquetWriter(scratch, value.schema) as writer:
                    for batch in value:
                        writer.write_batch(batch)
        except BaseException:
            scratch.unlink(missing_ok=True)
            raise
        return scratch, scratch

    table = Table.from_pandas(value)  # type: ignore
    buffer = BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    return buffer, None


def _store_parquet_input(
    parquet_input: ParquetLike,
    credentials: "ParquetUploadGrant",
    endpoint_url: str,
    proxy: str | None = None,
    certificates: list[str] | None = None,
) -> str:
    """Store a parquet table in the DataLayer via obstore."""
    store = create_s3_store(
        endpoint_url, credentials, proxy=proxy, certificates=certificates
    )
    payload, scratch = _parquet_payload(parquet_input.value)

    s3_path = f"s3://{credentials.bucket}/{credentials.key}"
    try:
        logger.debug(f"Uploading parquet to {s3_path} at {endpoint_url}...")
        obstore.put(store, credentials.key, payload)
        logger.info(f"Successfully uploaded parquet to {s3_path} at {endpoint_url}")
        return credentials.store
    except Exception as e:
        raise UploadError(f"Error while uploading to {s3_path}") from e
    finally:
        if scratch is not None:
            scratch.unlink(missing_ok=True)


async def astore_sparse_matrix(
    sparse: SporadikLike,
    credentials: "SparseUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Write a sparse matrix into the granted prefix as one store, and return its store id.

    Rooted at ``grant.key`` with the group at the store's root: zarr walks a node's parents to
    create intermediate groups, and a prefix-scoped grant denies the bucket root with a 403.
    """
    # In a thread: the writer is synchronous, and a matrix takes long enough that the event
    # loop (the agent's socket, every other upload) must not wait for it.
    endpoint_url = await datalayer.get_endpoint_url()
    return await asyncio.to_thread(
        _store_sparse_into_grant,
        sparse,
        credentials,
        endpoint_url,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )


def store_sparse_matrix(
    sparse: SporadikLike,
    credentials: "SparseUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Write a sparse matrix into the granted prefix synchronously."""
    return _store_sparse_into_grant(
        sparse,
        credentials,
        datalayer.endpoint_url,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )


def _store_sparse_into_grant(
    sparse: SporadikLike,
    credentials: "SparseUploadGrant",
    endpoint_url: str,
    proxy: str | None = None,
    certificates: list[str] | None = None,
) -> str:
    """The write itself, shared by both paths.

    ``sporadik.write_store_into`` lands its block last, which is what turns an interrupted
    upload (zarr metadata written, chunks missing, read back as zeros) into a refusal at
    ``finishSparseUpload``.
    """
    import zarr

    layouts = sparse.layouts
    store_path = create_zarr_store_path(
        endpoint_url, credentials, proxy=proxy, certificates=certificates
    )
    s3_path = f"s3://{credentials.bucket}/{credentials.key}"
    try:
        logger.debug(f"Uploading sparse matrix to {s3_path} at {endpoint_url}...")
        group = zarr.open_group(store=store_path, mode="w")
        _sporadik().write_store_into(group, list(layouts.values()))
        logger.info(
            f"Successfully uploaded a sparse matrix ({len(layouts)} layout(s)) to {s3_path}"
        )
        return credentials.store
    except Exception as e:
        raise UploadError(
            f"Error while uploading to {s3_path} on {endpoint_url}"
        ) from e


async def astore_mesh_file(
    mesh: MeshLike,
    credentials: "BigFileUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Store a mesh file in the DataLayer asynchronously via obstore."""
    endpoint_url = await datalayer.get_endpoint_url()
    store = create_s3_store(
        endpoint_url,
        credentials,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )

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


#: Sent with every request and part of a big-file upload, so the object store verifies it.
BIGFILE_CHECKSUM = "SHA256"


def part_size_for(size: int) -> int:
    """The part size the server's digest of a ``size``-byte file is cut at (``arkitekt_datalayer.digest``).

    8 MiB, doubled until the parts fit S3's 10,000. Computed here, not read off the grant, so
    an upload to a hub that does not advertise it still has its digest verified on arrival.
    """
    part = 8 * 1024 * 1024
    while size > part * 10_000:
        part *= 2
    return part


def _remaining_bytes(value: object) -> int:
    """How many bytes a write will send: a buffer's length, a path's size, or a file object's rest, left where it was."""
    if isinstance(value, (bytes, bytearray, memoryview)):
        return len(value)
    if isinstance(value, (str, os.PathLike)):
        return os.path.getsize(value)
    stream = cast("io.IOBase", value)
    position = stream.tell()
    end = stream.seek(0, io.SEEK_END)
    stream.seek(position)
    return end - position


async def aupload_bigfile(
    file: FileLike | BigFileLike,
    credentials: "BigFileUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload a big file to the DataLayer asynchronously via obstore."""
    endpoint_url = await datalayer.get_endpoint_url()
    store = create_s3_store(
        endpoint_url,
        credentials,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
        checksum_algorithm=BIGFILE_CHECKSUM,
    )

    try:
        logger.debug(
            f"Uploading file to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        await obstore.put_async(
            store,
            credentials.key,
            file.value,
            chunk_size=part_size_for(_remaining_bytes(file.value)),
        )
        logger.info(
            f"Successfully uploaded file to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}"
        )
        return credentials.store
    except Exception as e:
        raise UploadError(
            f"Error while uploading to s3://{credentials.bucket}/{credentials.key} on {endpoint_url}"
        ) from e


async def aupload_xarray(
    array: ArrayLike,
    credentials: "ZarrUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload an xarray to the DataLayer asynchronously via obstore."""
    return await astore_xarray_input(
        array,
        credentials,
        await datalayer.get_endpoint_url(),
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )


async def aupload_parquet(
    parquet: ParquetLike,
    credentials: "ParquetUploadGrant",
    datalayer: "DataLayer",
    executor: ThreadPoolExecutor,
) -> str:
    """Upload a parquet table to the DataLayer asynchronously via a thread executor."""
    co_future = executor.submit(
        _store_parquet_input,
        parquet,
        credentials,
        await datalayer.get_endpoint_url(),
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )
    return await asyncio.wrap_future(co_future)


# ========================================================================
# Sync upload functions (obstore)
# ========================================================================


def _store_xarray_via_obstore(
    xarray: ArrayLike,
    credentials: "ZarrUploadGrant",
    endpoint_url: str,
    proxy: str | None = None,
    certificates: list[str] | None = None,
) -> str:
    """Stores an xarray in the DataLayer synchronously via obstore/zarr."""
    store_path = create_zarr_store_path(
        endpoint_url, credentials, proxy=proxy, certificates=certificates
    )

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
    file: FileLike | BigFileLike,
    credentials: "BigFileUploadGrant",
    endpoint_url: str,
    proxy: str | None = None,
    certificates: list[str] | None = None,
) -> str:
    """Store a big file in the DataLayer synchronously via obstore."""
    store = create_s3_store(
        endpoint_url,
        credentials,
        proxy=proxy,
        certificates=certificates,
        checksum_algorithm=BIGFILE_CHECKSUM,
    )

    try:
        logger.debug(
            f"Uploading file (sync/obstore) to s3://{credentials.bucket}/{credentials.key} at {endpoint_url}..."
        )
        obstore.put(
            store,
            credentials.key,
            file.value,
            chunk_size=part_size_for(_remaining_bytes(file.value)),
        )
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
    proxy: str | None = None,
    certificates: list[str] | None = None,
) -> str:
    """Store a mesh file in the DataLayer synchronously via obstore."""
    store = create_s3_store(
        endpoint_url, credentials, proxy=proxy, certificates=certificates
    )

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
    array: ArrayLike,
    credentials: "ZarrUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload an xarray synchronously via obstore."""
    return _store_xarray_via_obstore(
        array,
        credentials,
        datalayer.endpoint_url,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )


def upload_parquet(
    parquet: ParquetLike,
    credentials: "ParquetUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload a parquet file synchronously."""
    return _store_parquet_input(
        parquet,
        credentials,
        datalayer.endpoint_url,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )


def upload_bigfile(
    file: FileLike | BigFileLike,
    credentials: "BigFileUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Upload a big file synchronously via obstore."""
    return _store_bigfile_via_obstore(
        file,
        credentials,
        datalayer.endpoint_url,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )


def store_mesh_file(
    mesh: MeshLike,
    credentials: "BigFileUploadGrant",
    datalayer: "DataLayer",
) -> str:
    """Store a mesh file synchronously via obstore."""
    return _store_mesh_via_obstore(
        mesh,
        credentials,
        datalayer.endpoint_url,
        proxy=datalayer.proxy,
        certificates=datalayer.certificates,
    )

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
    prefix: str | None = None,
) -> S3Store:
    """Create an obstore S3 client from an Elektro grant and endpoint.

    ``prefix`` roots the store inside the bucket, so every key the caller passes is
    relative to it. Zarr needs this (see :func:`create_zarr_store_path`); the
    single-object paths address their key directly and leave it unset.
    """
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
    if prefix:
        store_kwargs["prefix"] = prefix

    return S3Store(
        grant.bucket,
        **store_kwargs,
    )


def create_zarr_store_path(endpoint_url: str, grant: "S3UploadGrantLike") -> StorePath:
    """Create a Zarr store path rooted at the granted S3 prefix.

    The store is rooted at ``grant.key`` and the node sits at the store's root, rather
    than the store being rooted at the bucket with the node at ``grant.key``. The two
    write identical objects, but only this one stays inside the grant: zarr's
    ``init_array`` walks a node's parents to create intermediate groups, and the parent
    of ``grant.key`` in a bucket-rooted store is the *bucket root* -- so that shape
    reads and writes ``<bucket>/zarr.json``, which a prefix-scoped STS grant denies with
    a 403. A node at the root has no parents to walk.
    """
    zarr_store = ZarrObjectStore(create_s3_store(endpoint_url, grant, prefix=grant.key))
    return StorePath(zarr_store, "")


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


def _generic_chunk_shape(
    array: xr.DataArray, chunksize_in_bytes: int = 20_000_000
) -> tuple[int, ...]:
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


#: The inner chunk: the unit a reader decodes. For a ``(t, c)`` float32 trace with four
#: channels that is 65,536 samples of every channel, 1 MiB -- a screenful of a zoomed-in
#: trace, where the old 20 MB chunk made the viewer decode 1.25M samples to draw one.
INNER_CHUNK_BYTES = 1 * 1024**2

#: The shard: the unit of storage, grouping inner chunks so a long recording is not tens of
#: thousands of objects. 16 inner chunks -- 16 MiB, one object-store request's worth;
#: mikro's 128 MiB suits image volumes, not traces read a window at a time.
SHARD_BYTES = 16 * 1024**2

#: Arrays below one shard are written plain-chunked: a single shard would be the whole
#: array, so its index and read-modify-write buy nothing. This keeps small pyramid levels
#: (and most stimuli, tables-as-arrays and times vectors) unsharded.
SHARD_MIN_ARRAY_BYTES = SHARD_BYTES


def _generic_shard_shape(
    shape: tuple[int, ...], inner: tuple[int, ...], itemsize: int, shard_bytes: int = SHARD_BYTES
) -> tuple[int, ...]:
    """Grow an inner chunk shape into a shard shape for arbitrarily-labelled dims.

    Vendored from mikro. Walks dimensions inner->outer (C-order), multiplying each
    axis's chunk count by the largest integer factor that keeps the shard within the
    byte budget, clamped so a shard overhangs the array by less than one inner chunk
    per axis. Every result axis is an exact multiple of the inner chunk axis -- the
    server's ``validate_sharding`` and the frontend's reader reject anything else.
    """
    shard = list(inner)
    bytes_so_far = itemsize
    for size in inner:
        bytes_so_far *= size
    for i in reversed(range(len(shape))):
        budget = max(1, shard_bytes // bytes_so_far)
        factor = min(budget, max(1, -(-shape[i] // inner[i])))
        shard[i] = inner[i] * factor
        bytes_so_far *= factor
        if budget == 1:
            break
    return tuple(int(s) for s in shard)


def _zarr_chunk_layout(array: xr.DataArray) -> tuple[tuple[int, ...], tuple[int, ...] | None]:
    """The on-disk zarr (inner chunk, shard) layout, in the array's own dimension order.

    Canonical 5D ``ctzyx`` arrays keep the ``ctzyx``-aware ~20 MB :func:`rechunk`, unsharded
    (elektro stores no images). Everything else -- every trace, which is ``(t)`` or
    ``(t, c)`` -- gets inner chunks of at most :data:`INNER_CHUNK_BYTES`, the innermost
    dims kept whole while they fit; from :data:`SHARD_MIN_ARRAY_BYTES` up, those are
    grouped into shards of about :data:`SHARD_BYTES`. The shard is None when unsharded.
    """
    if set(array.dims) == _CTZYX_DIMS:
        chunks = rechunk(
            dict(array.sizes), itemsize=array.dtype.itemsize, chunksize_in_bytes=20_000_000
        )
        return tuple(int(chunks[dim]) for dim in array.dims), None

    chunk_shape = _generic_chunk_shape(array, chunksize_in_bytes=INNER_CHUNK_BYTES)
    if array.dtype.itemsize * array.size < SHARD_MIN_ARRAY_BYTES:
        return chunk_shape, None
    shard_shape = _generic_shard_shape(array.shape, chunk_shape, array.dtype.itemsize)
    if shard_shape == chunk_shape:
        return chunk_shape, None
    return chunk_shape, shard_shape


def _dimension_names(array: xr.DataArray) -> list[str | None] | None:
    """The dimension names to write into the store, or None when there are none.

    Only names the caller gave are written. xarray's placeholders (``dim_0``,
    ...) state nothing, and the server checks a store's names against the
    declared axes: a placeholder would be refused as a disagreement, where a
    null is the store declining to name the dimension.
    """
    names: list[str | None] = [
        None if str(dim) == f"dim_{index}" else str(dim) for index, dim in enumerate(array.dims)
    ]
    return names if any(name is not None for name in names) else None


def write_dataarray_to_zarr(
    store_path: StorePath,
    array: xr.DataArray,
    *,
    chunks: tuple[int, ...] | None = None,
    shards: tuple[int, ...] | None = None,
) -> None:
    """Write a DataArray to a zarr v3 array synchronously with explicit chunks.

    Large arrays are sharded by default (see :func:`_zarr_chunk_layout`); pass explicit
    ``chunks`` without ``shards`` to force an unsharded layout. The default codecs are
    kept deliberately: zarr's stock sharded layout (sole top-level ``sharding_indexed``,
    declared crc32c index codecs) is exactly what the server and the frontend accept.

    Dask-backed arrays are streamed via ``dask.array.store`` so the full array is never
    materialised in memory; numpy arrays are written directly.
    """
    if chunks is None and shards is None:
        chunks, shards = _zarr_chunk_layout(array)
    elif chunks is None:
        raise ValueError("shards cannot be given without the inner chunks they group.")
    zarr_array = zarr.create_array(
        store_path,
        shape=array.shape,
        chunks=chunks,
        shards=shards,
        dtype=array.dtype,
        dimension_names=_dimension_names(array),
        zarr_format=3,
        overwrite=True,
    )
    data = array.data
    if is_dask_array(data):
        from dask.array.core import store as dask_store

        # Align dask blocks to the *storage object* grid -- the shard when sharding, else
        # the chunk -- so concurrent, lock-free writes never target one object from two
        # blocks. A sub-shard write is a read-modify-write of the whole shard, so two
        # blocks in one shard would silently drop inner chunks.
        data = data.rechunk(shards or chunks)
        dask_store(data, zarr_array, lock=False)
    else:
        zarr_array[...] = np.asarray(data)


async def awrite_dataarray_to_zarr(
    store_path: StorePath,
    array: xr.DataArray,
    *,
    chunks: tuple[int, ...] | None = None,
    shards: tuple[int, ...] | None = None,
) -> None:
    """Write a DataArray to a zarr v3 array without blocking the event loop.

    Delegates to the synchronous streaming writer in a worker thread: ``dask.array.store``
    runs the dask scheduler synchronously, so it must not be awaited on the event loop.
    """
    await asyncio.to_thread(write_dataarray_to_zarr, store_path, array, chunks=chunks, shards=shards)


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

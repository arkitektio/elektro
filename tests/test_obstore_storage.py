from io import BytesIO
from types import SimpleNamespace

import dask.array as da
import numpy as np
import obstore
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import xarray as xr
import zarr
from obstore.store import MemoryStore
from zarr.storage import ObjectStore as ZarrObjectStore, StorePath

from elektro.io.download import download_file
from elektro.io.obstore import (
    ParquetDatasetViaObstore,
    awrite_dataarray_to_zarr,
    write_dataarray_to_zarr,
)
from elektro.scalars import ArrayLike, TraceLike


def test_parquet_dataset_via_obstore_reads_dataframe() -> None:
    store = MemoryStore()
    dataframe = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    buffer = BytesIO()

    pq.write_table(pa.Table.from_pandas(dataframe), buffer)
    obstore.put(store, "tables/example.parquet", buffer.getvalue())

    dataset = ParquetDatasetViaObstore(store, "tables/example.parquet")

    assert dataset.read_pandas().to_pandas().equals(dataframe)


def test_download_file_reads_bytes_via_obstore(tmp_path, monkeypatch) -> None:
    store = MemoryStore()
    payload = b"hello via obstore"
    target = tmp_path / "download.bin"
    credentials = SimpleNamespace(
        access_key="access",
        secret_key="secret",
        session_token="token",
        bucket="bucket",
        key="files/download.bin",
        path="bucket/files/download.bin",
    )

    obstore.put(store, credentials.key, payload)

    monkeypatch.setattr(
        "elektro.io.download.unkoil",
        lambda function, store_id: (credentials, "http://example.invalid"),
    )
    monkeypatch.setattr("elektro.io.download.create_s3_store", lambda *_args: store)

    result = download_file("store-id", str(target))

    assert result == str(target)
    assert target.read_bytes() == payload


def _store_path(key: str = "arr") -> StorePath:
    return StorePath(ZarrObjectStore(MemoryStore()), key)


def test_write_dataarray_to_zarr_numpy_roundtrips_with_chunks() -> None:
    # A 1-D trace, the canonical elektro payload, written and read back via obstore.
    array = xr.DataArray(np.arange(1000, dtype="float32"), dims=["c"])
    sp = _store_path()

    write_dataarray_to_zarr(sp, array)

    back = zarr.open_array(sp, mode="r")
    assert back.shape == (1000,)
    assert back.metadata.dimension_names == ("c",)
    assert np.array_equal(back[:], array.to_numpy())


def test_write_dataarray_to_zarr_streams_dask_arrays() -> None:
    # A large 1-D trace so the generic chunker actually splits it into multiple
    # on-disk chunks rather than writing the whole array at once.
    source = np.arange(40_000_000, dtype="uint16")
    array = xr.DataArray(da.from_array(source, chunks=(5_000_000,)), dims=["c"])
    sp = _store_path("big")

    write_dataarray_to_zarr(sp, array)

    back = zarr.open_array(sp, mode="r")
    # ~20MB target splits the trace rather than writing all 40M samples in one chunk.
    assert back.chunks[0] < source.shape[0]
    assert np.array_equal(back[:], source)


@pytest.mark.asyncio
async def test_awrite_dataarray_to_zarr_roundtrips() -> None:
    array = xr.DataArray(np.arange(2048, dtype="float32"), dims=["c"])
    sp = _store_path("async")

    await awrite_dataarray_to_zarr(sp, array)

    back = zarr.open_array(sp, mode="r")
    assert np.array_equal(back[:], array.to_numpy())


@pytest.mark.asyncio
async def test_awrite_dataarray_to_zarr_streams_dask_arrays(monkeypatch) -> None:
    # A large 1-D trace so the generic chunker splits it into multiple chunks.
    source = np.arange(40_000_000, dtype="uint16")
    array = xr.DataArray(da.from_array(source, chunks=(5_000_000,)), dims=["c"])
    sp = _store_path("async-big")

    # Guard against out-of-core breakage: the whole array must never be pulled
    # into memory in one shot via Array.compute(). Streaming uses dask.array.store
    # (per-block stores), not a single compute of the full array.
    import dask.array.core as dac

    original_compute = dac.Array.compute

    def _fail_on_full_compute(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        raise AssertionError(
            "dask array was fully computed into memory; out-of-core streaming was broken"
        )

    monkeypatch.setattr(dac.Array, "compute", _fail_on_full_compute)
    try:
        await awrite_dataarray_to_zarr(sp, array)
    finally:
        monkeypatch.setattr(dac.Array, "compute", original_compute)

    back = zarr.open_array(sp, mode="r")
    assert back.chunks[0] < source.shape[0]
    assert np.array_equal(back[:], source)


def test_array_like_preserves_labels() -> None:
    # ArrayLike preserves the caller's labelled dims/order verbatim.
    labeled = xr.DataArray(np.zeros((4, 8), dtype="uint16"), dims=["sweep", "c"])
    arr = ArrayLike.validate(labeled)
    assert arr.value.dims == ("sweep", "c")
    assert arr.value.shape == (4, 8)

    # Bare arrays carry no labels, so xarray's default names are assigned.
    bare = ArrayLike.validate(np.zeros((1000,), dtype="uint16"))
    assert bare.value.dims == ("dim_0",)
    assert hasattr(bare, "key")


def test_trace_like_coerces_to_c() -> None:
    # TraceLike forces the canonical 1-D ``c`` layout.
    trace = TraceLike.validate(np.zeros((1000,), dtype="float32"))
    assert trace.value.dims == ("c",)
    assert trace.value.shape == (1000,)


def test_write_dataarray_to_zarr_streams_arbitrary_dims() -> None:
    # A large 2-D array must chunk and round-trip via the generic chunker.
    source = np.arange(50 * 2048, dtype="uint16").reshape(50, 2048)
    array = xr.DataArray(da.from_array(source, chunks=(10, 2048)), dims=["sweep", "c"])
    sp = _store_path("arbitrary")

    write_dataarray_to_zarr(sp, array)

    back = zarr.open_array(sp, mode="r")
    assert back.metadata.dimension_names == ("sweep", "c")
    assert np.array_equal(back[:], source)

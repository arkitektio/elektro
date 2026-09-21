"""Tests for obstore-backed zarr/parquet storage and the download helper."""

from io import BytesIO
from pathlib import Path
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
from elektro.scalars import ArrayLike


def test_parquet_dataset_via_obstore_reads_dataframe() -> None:
    """A parquet file written to an obstore store reads back as the original dataframe."""
    store = MemoryStore()
    dataframe = pd.DataFrame({"x": [1, 2], "y": [3, 4]})
    buffer = BytesIO()

    pq.write_table(pa.Table.from_pandas(dataframe), buffer)
    obstore.put(store, "tables/example.parquet", buffer.getvalue())

    dataset = ParquetDatasetViaObstore(store, "tables/example.parquet")

    assert dataset.read_pandas().to_pandas().equals(dataframe)


def test_download_file_reads_bytes_via_obstore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``download_file`` fetches bytes via obstore and writes them to the target path."""
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

    seen: dict[str, object] = {}

    def fake_unkoil(
        function: object, store_id: str, rath: object, datalayer: object
    ) -> tuple[SimpleNamespace, str]:
        seen.update(rath=rath, datalayer=datalayer)
        return credentials, "http://example.invalid"

    monkeypatch.setattr("elektro.io.download.unkoil", fake_unkoil)
    monkeypatch.setattr("elektro.io.download.create_s3_store", lambda *_args: store)

    # The clients are resolved before the hop into the event loop, so they are
    # handed over explicitly here; nothing ambient is involved.
    rath, datalayer = object(), object()
    result = download_file("store-id", str(target), datalayer, rath=rath)

    assert seen == {"rath": rath, "datalayer": datalayer}

    assert result == str(target)
    assert target.read_bytes() == payload


def _store_path(key: str = "arr") -> StorePath:
    return StorePath(ZarrObjectStore(MemoryStore()), key)


def test_write_dataarray_to_zarr_numpy_roundtrips_with_chunks() -> None:
    """A numpy-backed 1-D trace round-trips through zarr with its dim name and chunks."""
    # A 1-D trace, the canonical elektro payload, written and read back via obstore.
    array = xr.DataArray(np.arange(1000, dtype="float32"), dims=["c"])
    sp = _store_path()

    write_dataarray_to_zarr(sp, array)

    back = zarr.open_array(sp, mode="r")
    assert back.shape == (1000,)
    assert back.metadata.dimension_names == ("c",)
    assert np.array_equal(back[:], array.to_numpy())


def test_write_dataarray_to_zarr_streams_dask_arrays() -> None:
    """A large dask-backed trace is split into multiple on-disk chunks on write."""
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
    """The async writer round-trips a numpy-backed trace through zarr."""
    array = xr.DataArray(np.arange(2048, dtype="float32"), dims=["c"])
    sp = _store_path("async")

    await awrite_dataarray_to_zarr(sp, array)

    back = zarr.open_array(sp, mode="r")
    assert np.array_equal(back[:], array.to_numpy())


@pytest.mark.asyncio
async def test_awrite_dataarray_to_zarr_streams_dask_arrays(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The async writer streams a large dask trace without computing it fully in memory."""
    # A large 1-D trace so the generic chunker splits it into multiple chunks.
    source = np.arange(40_000_000, dtype="uint16")
    array = xr.DataArray(da.from_array(source, chunks=(5_000_000,)), dims=["c"])
    sp = _store_path("async-big")

    # Guard against out-of-core breakage: the whole array must never be pulled
    # into memory in one shot via Array.compute(). Streaming uses dask.array.store
    # (per-block stores), not a single compute of the full array.
    import dask.array.core as dac

    original_compute = dac.Array.compute

    def _fail_on_full_compute(self, *args, **kwargs) -> None:  # noqa: ANN001, ANN002, ANN003
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


def test_trace_like_preserves_labels() -> None:
    """``ArrayLike`` keeps labelled dims and leaves bare arrays unnamed."""
    labeled = xr.DataArray(np.zeros((4, 8), dtype="uint16"), dims=["sweep", "c"])
    arr = ArrayLike.validate(labeled)
    assert arr.value.dims == ("sweep", "c")
    assert arr.value.shape == (4, 8)

    # Bare arrays carry no labels: the placeholders stay until axes name them.
    bare = ArrayLike.validate(np.zeros((1000,), dtype="uint16"))
    assert bare.value.dims == ("dim_0",)
    assert hasattr(bare, "key")


def test_unnamed_dims_are_not_written_into_the_store() -> None:
    """A placeholder name would be refused by the server's axis check; a null is not."""
    from elektro.io.obstore import _dimension_names

    assert _dimension_names(xr.DataArray(np.zeros((4, 8)))) is None
    assert _dimension_names(xr.DataArray(np.zeros((4, 8)), dims=["t", "c"])) == ["t", "c"]
    assert _dimension_names(xr.DataArray(np.zeros((4, 8)), dims=["t", "dim_1"])) == ["t", None]


def test_write_dataarray_to_zarr_streams_arbitrary_dims() -> None:
    """A large 2-D array chunks and round-trips via the generic chunker preserving dims."""
    # A large 2-D array must chunk and round-trip via the generic chunker.
    source = np.arange(50 * 2048, dtype="uint16").reshape(50, 2048)
    array = xr.DataArray(da.from_array(source, chunks=(10, 2048)), dims=["sweep", "c"])
    sp = _store_path("arbitrary")

    write_dataarray_to_zarr(sp, array)

    back = zarr.open_array(sp, mode="r")
    assert back.metadata.dimension_names == ("sweep", "c")
    assert np.array_equal(back[:], source)


def test_trace_layout_is_small_chunks_in_bounded_shards() -> None:
    """A long (t, c) trace: 1 MiB inner chunks, 16 MiB shards; a small level stays unsharded."""
    from elektro.io.obstore import _zarr_chunk_layout

    def layout(shape: tuple[int, ...]) -> tuple:
        return _zarr_chunk_layout(xr.DataArray(np.empty(shape, np.float32), dims=["t", "c"][: len(shape)]))

    assert layout((25_000_000, 4)) == ((65_536, 4), (1_048_576, 4))
    assert layout((25_000_000,)) == ((262_144,), (4_194_304,))
    # Under one shard's worth: sharding would make the whole array one object anyway.
    assert layout((250_000, 4)) == ((65_536, 4), None)
    assert layout((1_000,)) == ((1_000,), None)


@pytest.mark.parametrize("dask_backed", [False, True])
def test_sharded_write_round_trips_in_a_layout_the_server_accepts(dask_backed: bool) -> None:
    """A sharded trace reads back exactly, with sharding_indexed as the sole top-level codec."""
    values = np.random.default_rng(0).standard_normal((1_500_000, 4)).astype(np.float32)  # 24 MB
    data = da.from_array(values, chunks=(100_000, 4)) if dask_backed else values
    sp = _store_path()

    write_dataarray_to_zarr(sp, xr.DataArray(data, dims=["t", "c"]))

    back = zarr.open_array(sp, mode="r")
    assert back.shards == (1_048_576, 4) and back.chunks == (65_536, 4)
    codecs = back.metadata.to_dict()["codecs"]
    assert [c["name"] for c in codecs] == ["sharding_indexed"]
    assert codecs[0]["configuration"]["index_location"] in ("start", "end")
    np.testing.assert_array_equal(back[:], values)

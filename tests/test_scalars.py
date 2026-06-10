"""Unit tests for the custom scalars in ``elektro.scalars``."""

import dask.array as da
import numpy as np
import pytest
import xarray as xr
from pydantic import BaseModel, ValidationError

from elektro.scalars import ArrayLike, Matrix, TraceLike, TwoDVector


class TraceModel(BaseModel):
    x: TraceLike


class ArrayModel(BaseModel):
    x: ArrayLike


class VectorModel(BaseModel):
    x: TwoDVector


class MatrixModel(BaseModel):
    x: Matrix


def test_tracelike_accepts_1d_numpy():
    m = TraceModel(x=np.zeros((100,)))
    assert m.x.value.ndim == 1


def test_tracelike_accepts_1d_dataarray():
    m = TraceModel(x=xr.DataArray(np.zeros((10,)), dims=["c"]))
    assert m.x.value.ndim == 1


def test_tracelike_rejects_2d():
    with pytest.raises(ValidationError):
        TraceModel(x=np.zeros((10, 10)))


def test_arraylike_preserves_multidim_numpy():
    m = ArrayModel(x=np.zeros((4, 5, 6)))
    assert m.x.value.shape == (4, 5, 6)


def test_arraylike_preserves_labelled_dims():
    arr = xr.DataArray(np.zeros((3, 2)), dims=["time", "channel"])
    m = ArrayModel(x=arr)
    assert list(m.x.value.dims) == ["time", "channel"]


def test_arraylike_accepts_dask():
    m = ArrayModel(x=da.zeros((8, 8), chunks=(4, 4)))
    assert m.x.value.shape == (8, 8)


def test_arraylike_rejects_unsupported_type():
    with pytest.raises(ValidationError):
        ArrayModel(x=[1, 2, 3])


def test_twodvector_validates_length():
    assert VectorModel(x=[1.0, 2.0]).x == [1.0, 2.0]
    with pytest.raises(ValidationError):
        VectorModel(x=[1.0, 2.0, 3.0])


def test_matrix_roundtrip():
    arr = np.arange(9).reshape(3, 3)
    m = MatrixModel(x=arr)
    np.testing.assert_array_equal(m.x.as_matrix(), arr)

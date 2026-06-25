"""Unit tests for the custom scalars in ``elektro.scalars``."""

import dask.array as da
import numpy as np
import pytest
import xarray as xr
from pydantic import BaseModel, ValidationError

from elektro.scalars import ArrayLike, Matrix, TraceLike, TwoDVector


class TraceModel(BaseModel):
    """Model with a single ``TraceLike`` field for validation tests."""

    x: TraceLike


class ArrayModel(BaseModel):
    """Model with a single ``ArrayLike`` field for validation tests."""

    x: ArrayLike


class VectorModel(BaseModel):
    """Model with a single ``TwoDVector`` field for validation tests."""

    x: TwoDVector


class MatrixModel(BaseModel):
    """Model with a single ``Matrix`` field for validation tests."""

    x: Matrix


def test_tracelike_accepts_1d_numpy() -> None:
    """TraceLike accepts a 1D numpy array and keeps it 1-dimensional."""
    m = TraceModel(x=np.zeros((100,)))
    assert m.x.value.ndim == 1


def test_tracelike_accepts_1d_dataarray() -> None:
    """TraceLike accepts a 1D xarray DataArray and keeps it 1-dimensional."""
    m = TraceModel(x=xr.DataArray(np.zeros((10,)), dims=["c"]))
    assert m.x.value.ndim == 1


def test_tracelike_rejects_2d() -> None:
    """TraceLike raises a ValidationError for a 2D array."""
    with pytest.raises(ValidationError):
        TraceModel(x=np.zeros((10, 10)))


def test_arraylike_preserves_multidim_numpy() -> None:
    """ArrayLike preserves the shape of a multidimensional numpy array."""
    m = ArrayModel(x=np.zeros((4, 5, 6)))
    assert m.x.value.shape == (4, 5, 6)


def test_arraylike_preserves_labelled_dims() -> None:
    """ArrayLike preserves the dimension labels of an xarray DataArray."""
    arr = xr.DataArray(np.zeros((3, 2)), dims=["time", "channel"])
    m = ArrayModel(x=arr)
    assert list(m.x.value.dims) == ["time", "channel"]


def test_arraylike_accepts_dask() -> None:
    """ArrayLike accepts a dask array and preserves its shape."""
    m = ArrayModel(x=da.zeros((8, 8), chunks=(4, 4)))
    assert m.x.value.shape == (8, 8)


def test_arraylike_rejects_unsupported_type() -> None:
    """ArrayLike raises a ValidationError for an unsupported plain list."""
    with pytest.raises(ValidationError):
        ArrayModel(x=[1, 2, 3])


def test_twodvector_validates_length() -> None:
    """TwoDVector accepts a length-2 vector and rejects other lengths."""
    assert VectorModel(x=[1.0, 2.0]).x == [1.0, 2.0]
    with pytest.raises(ValidationError):
        VectorModel(x=[1.0, 2.0, 3.0])


def test_matrix_roundtrip() -> None:
    """Matrix round-trips a 3x3 numpy array via ``as_matrix``."""
    arr = np.arange(9).reshape(3, 3)
    m = MatrixModel(x=arr)
    np.testing.assert_array_equal(m.x.as_matrix(), arr)

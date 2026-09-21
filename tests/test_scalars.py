"""Unit tests for the custom scalars in ``elektro.scalars``."""

import dask.array as da
import numpy as np
import pytest
import xarray as xr
from pydantic import BaseModel, ValidationError

from elektro.scalars import Matrix, ArrayLike, TwoDVector, is_unlabeled


class ArrayModel(BaseModel):
    """Model with a single ``ArrayLike`` field for validation tests."""

    x: ArrayLike


class VectorModel(BaseModel):
    """Model with a single ``TwoDVector`` field for validation tests."""

    x: TwoDVector


class MatrixModel(BaseModel):
    """Model with a single ``Matrix`` field for validation tests."""

    x: Matrix


def test_arraylike_accepts_1d_numpy() -> None:
    """ArrayLike accepts a 1D numpy array and keeps it 1-dimensional."""
    m = ArrayModel(x=np.zeros((100,)))
    assert m.x.value.ndim == 1


def test_arraylike_accepts_1d_dataarray() -> None:
    """ArrayLike accepts a 1D xarray DataArray and keeps it 1-dimensional."""
    m = ArrayModel(x=xr.DataArray(np.zeros((10,)), dims=["c"]))
    assert m.x.value.ndim == 1


def test_arraylike_accepts_multidim_numpy() -> None:
    """An analog signal is one (t, c) dataset: a bare 2D array is kept, unnamed."""
    m = ArrayModel(x=np.zeros((10, 4)))
    assert m.x.value.shape == (10, 4)
    assert is_unlabeled(m.x.value)


def test_arraylike_preserves_labelled_dims() -> None:
    """ArrayLike preserves the dimension labels of an xarray DataArray verbatim."""
    arr = xr.DataArray(np.zeros((3, 2)), dims=["time", "channel"])
    m = ArrayModel(x=arr)
    assert list(m.x.value.dims) == ["time", "channel"]
    assert not is_unlabeled(m.x.value)


def test_arraylike_accepts_dask() -> None:
    """ArrayLike accepts a dask array and keeps it lazy."""
    m = ArrayModel(x=da.zeros((8, 8), chunks=(4, 4)))
    assert m.x.value.shape == (8, 8)
    assert m.x.value.chunks is not None


def test_arraylike_accepts_list() -> None:
    """ArrayLike accepts a plain list of samples."""
    m = ArrayModel(x=[1.0, 2.0, 3.0])
    assert m.x.value.shape == (3,)


def test_arraylike_rejects_scalar_and_unsupported() -> None:
    """ArrayLike raises a ValidationError for a 0-d array and for non-arrays."""
    with pytest.raises(ValidationError):
        ArrayModel(x=np.float64(1.0) * np.ones(()))
    with pytest.raises(ValidationError):
        ArrayModel(x="not an array")


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

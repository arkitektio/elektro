from pydantic import BaseModel
import numpy as np
import xarray as xr
from elektro.scalars import ArrayLike


class Arguments(BaseModel):
    x: ArrayLike


def test_numpy_serialization():
    x = np.random.random((20, 1000, 1000))

    t = Arguments(x=x)
    assert t.x.value.ndim == 5, "Should be five dimensionsal"


def test_xarray_serialization():
    x = xr.DataArray(np.zeros((1000, 1000, 10)), dims=["x", "y", "z"])

    t = Arguments(x=x)
    assert t.x.value.ndim == 5, "Should be five dimensionsal"

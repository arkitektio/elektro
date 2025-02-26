from pydantic import BaseModel
import numpy as np
import xarray as xr
from elektro.scalars import TraceLike


class Arguments(BaseModel):
    x: TraceLike


def test_numpy_serialization():
    x = np.random.random((20, 1000))

    t = Arguments(x=x)
    assert t.x.value.ndim == 2, "Should be five dimensionsal"


def test_xarray_serialization():
    x = xr.DataArray(np.zeros((20, 1000)), dims=["c", "t"])

    t = Arguments(x=x)
    assert t.x.value.ndim == 2, "Should be five dimensionsal"

"""Tests that ``ArrayLike`` coerces numpy and xarray inputs."""

from pydantic import BaseModel
import numpy as np
import xarray as xr
from elektro.scalars import ArrayLike


class Arguments(BaseModel):
    """Pydantic model with a single ``ArrayLike`` field used to exercise validation."""

    x: ArrayLike


def test_numpy_serialization() -> None:
    """A 1-D numpy array validates into a 1-D ``ArrayLike`` value."""
    x = np.random.random((1000,))

    t = Arguments(x=x)
    assert t.x.value.ndim == 1, "Should be one dimensional"


def test_xarray_serialization() -> None:
    """A 1-D xarray DataArray validates into a 1-D ``ArrayLike`` value."""
    x = xr.DataArray(np.zeros((1000,)), dims=["c"])

    t = Arguments(x=x)
    assert t.x.value.ndim == 1, "Should be one dimensional"

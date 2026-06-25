"""Tests that ``TraceLike`` coerces numpy and xarray inputs to 1-D traces."""

from pydantic import BaseModel
import numpy as np
import xarray as xr
from elektro.scalars import TraceLike


class Arguments(BaseModel):
    """Pydantic model with a single ``TraceLike`` field used to exercise validation."""

    x: TraceLike


def test_numpy_serialization() -> None:
    """A 1-D numpy array validates into a 1-D ``TraceLike`` value."""
    x = np.random.random((1000,))

    t = Arguments(x=x)
    assert t.x.value.ndim == 1, "Should be one dimensional"


def test_xarray_serialization() -> None:
    """A 1-D xarray DataArray validates into a 1-D ``TraceLike`` value."""
    x = xr.DataArray(np.zeros((1000,)), dims=["c"])

    t = Arguments(x=x)
    assert t.x.value.ndim == 1, "Should be one dimensional"

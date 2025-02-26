import numpy as np
import pytest
from elektro.api.schema import create_dataset, from_trace_like, get_random_trace
import xarray as xr


@pytest.mark.integration
def test_write_random(deployed_app):
    x = from_trace_like(
        xr.DataArray(data=np.random.random((1000, 1000, 10)), dims=["x", "y", "z"]),
        name="test_random_write",
    )
    assert x.id, "Did not get a random rep"
    assert x.data.shape == (
        1,
        1,
        10,
        1000,
        1000,
    ), "Did not write data according to schema ( T, C, Z, Y, X )"


@pytest.mark.integration
def test_get_random(deployed_app):
    x = from_trace_like(
        xr.DataArray(data=np.random.random((1000, 1000, 10)), dims=["x", "y", "z"]),
        name="test_random_write",
    )
    x = get_random_trace()
    assert x.id, "Did not get a random rep even though one was written"


@pytest.mark.integration
def test_create_dataset(deployed_app):
    x = create_dataset(name="johannes")
    assert x.id, "Was not able to create a dataset"

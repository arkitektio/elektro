import numpy as np
import pytest
from elektro.api.schema import create_dataset, from_trace_like, get_random_trace
import xarray as xr


@pytest.mark.integration
def test_write_random(deployed_app):
    dataset = create_dataset(name="test_write_random")
    x = from_trace_like(
        np.random.random((1000,)),
        name="test_random_write",
        dataset=dataset.id,
    )
    assert x.id, "Did not get a random rep"
    assert x.data.shape == (1000,), "Did not write data according to schema ( T, C, Z, Y, X )"


@pytest.mark.integration
def test_get_random(deployed_app):
    dataset = create_dataset(name="test_get_random")
    x = from_trace_like(
        np.random.random((1000,)),
        name="test_random_write",
        dataset=dataset.id,
    )
    x = get_random_trace()
    assert x.id, "Did not get a random rep even though one was written"


@pytest.mark.integration
def test_create_dataset(deployed_app):
    x = create_dataset(name="johannes")
    assert x.id, "Was not able to create a dataset"

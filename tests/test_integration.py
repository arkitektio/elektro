"""Integration tests for writing, reading and creating datasets and traces."""

import numpy as np
import pytest
from elektro.api.schema import create_dataset, from_trace_like, get_random_trace

from tests.conftest import DeployedElektro


@pytest.mark.integration
def test_write_random(deployed_app: DeployedElektro) -> None:
    """Writing a random trace into a dataset returns an id and the expected shape."""
    dataset = create_dataset(name="test_write_random")
    x = from_trace_like(
        np.random.random((1000,)),
        name="test_random_write",
        dataset=dataset.id,
    )
    assert x.id, "Did not get a random rep"
    assert x.data.shape == (1000,), "Did not write data according to schema ( T, C, Z, Y, X )"


@pytest.mark.integration
def test_get_random(deployed_app: DeployedElektro) -> None:
    """After writing a trace, ``get_random_trace`` returns one with an id."""
    dataset = create_dataset(name="test_get_random")
    x = from_trace_like(
        np.random.random((1000,)),
        name="test_random_write",
        dataset=dataset.id,
    )
    x = get_random_trace()
    assert x.id, "Did not get a random rep even though one was written"


@pytest.mark.integration
def test_create_dataset(deployed_app: DeployedElektro) -> None:
    """``create_dataset`` returns a dataset with an id."""
    x = create_dataset(name="johannes")
    assert x.id, "Was not able to create a dataset"

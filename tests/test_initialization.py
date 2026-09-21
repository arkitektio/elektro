"""Integration test for building an array via ``create_array_dataset``."""

from elektro import Elektro
import numpy as np
import pytest


@pytest.mark.integration
def test_create_array(elektro: Elektro) -> None:
    """``create_array_dataset`` produces a dataset whose data has the input shape."""
    dataset = elektro.create_array_dataset(
        data=np.zeros((1000,)),
        scales=[],
        name="Farter 1",
        axes=["t"],
    )
    assert dataset.data.shape == (1000,), "Shape should be (1000,)"

from elektro.api.schema import from_trace_like
from elektro import Elektro
import numpy as np
import pytest


@pytest.mark.integration
def test_create_array(deployed_app: Elektro):
    l = from_trace_like(
        np.zeros((1000,)),
        name="Farter 1",
    )
    assert l.data.shape == (1000,), "Shape should be (1000,)"

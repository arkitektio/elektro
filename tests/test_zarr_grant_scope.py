"""Integration tests for zarr uploads under prefix-scoped STS grants.

The server hands out credentials whose session policy only covers the granted
key. Zarr writes that stray outside that prefix -- ``init_array`` probing the
bucket-root ``zarr.json`` for a parent group -- 403 against any real deployment,
so these run against the scoped grants the integration stack mints.
"""

import numpy as np
import obstore
import pytest
import zarr
from obstore.exceptions import PermissionDeniedError

from elektro.api.schema import create_dataset, from_trace_like, get_trace, request_zarr_upload
from elektro.io.obstore import create_s3_store

from tests.conftest import DeployedElektro


@pytest.mark.integration
def test_zarr_upload_grant_is_prefix_scoped(deployed_app: DeployedElektro) -> None:
    """A zarr upload grant cannot read outside its key.

    Guards the premise of the test below: if the stack hands out the root key
    again, out-of-prefix requests succeed and the upload test proves nothing.
    """
    grant = request_zarr_upload()
    endpoint_url = deployed_app.elektro.datalayer.endpoint_url
    store = create_s3_store(endpoint_url, grant)

    with pytest.raises(PermissionDeniedError):
        obstore.get(store, "zarr.json")


@pytest.mark.integration
def test_trace_upload_with_scoped_grant_roundtrips(deployed_app: DeployedElektro) -> None:
    """A trace uploads through a scoped grant and reads back unchanged."""
    dataset = create_dataset(name="test_trace_upload_with_scoped_grant")
    values = np.random.random((1000,))

    created = from_trace_like(values, name="scoped_trace", dataset=dataset.id)

    fetched = get_trace(created.id)
    stored = zarr.open_array(fetched.store.zarr_store, mode="r")
    np.testing.assert_array_equal(stored[...], values)

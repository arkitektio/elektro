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

from elektro.io.obstore import create_s3_store

from elektro.elektro import Elektro


@pytest.mark.integration
def test_zarr_upload_grant_is_prefix_scoped(elektro: Elektro) -> None:
    """A zarr upload grant cannot read outside its key.

    Guards the premise of the test below: if the stack hands out the root key
    again, out-of-prefix requests succeed and the upload test proves nothing.
    """
    grant = elektro.request_zarr_upload()
    endpoint_url = elektro.datalayer.endpoint_url
    store = create_s3_store(endpoint_url, grant)

    with pytest.raises(PermissionDeniedError):
        obstore.get(store, "zarr.json")


@pytest.mark.integration
def test_dataset_upload_with_scoped_grant_roundtrips(elektro: Elektro) -> None:
    """A dataset uploads through a scoped grant and reads back unchanged."""
    folder = elektro.create_folder(name="test_dataset_upload_with_scoped_grant")
    values = np.random.random((1000,))

    created = elektro.create_array_dataset(
        data=values, scales=[], name="scoped_dataset", axes=["t"], folder=folder.id
    )

    fetched = elektro.get_array_dataset(created.id)
    # The store belongs to the pyramid level, not to the dataset.
    stored = zarr.open_array(fetched.data_arrays[0].store.zarr_store, mode="r")
    np.testing.assert_array_equal(stored[...], values)

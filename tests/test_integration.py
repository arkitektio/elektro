"""Integration tests for writing, reading and creating datasets and traces."""

from pathlib import Path

import numpy as np
import pytest
from elektro.api.schema import (
    create_dataset,
    from_file_like,
    from_trace_like,
    get_file,
    get_random_trace,
)

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


@pytest.mark.integration
def test_from_file_like(deployed_app: DeployedElektro, tmp_path: Path) -> None:
    """Uploading a file-like object returns a File backed by a store.

    This exercises the full ``from_file_like`` path: the ``FileLike`` scalar is
    coerced, the ``UploadMiddleware`` requests big-file credentials and uploads
    the bytes to the datalayer, and the ``fromFileLike`` mutation is sent.
    """
    path = tmp_path / "hello.txt"
    path.write_bytes(b"hello elektro integration test\n")

    # The FileLike scalar coerces a path string into an opened file on validation.
    file = from_file_like(name="hello.txt", file=str(path))

    assert file.id, "Did not get a file id back"
    assert file.name, "File did not come back with a name"
    assert file.store is not None, "File was not backed by a store"
    assert file.store.key, "Store did not get a key assigned during upload"


@pytest.mark.integration
def test_from_file_like_into_dataset(deployed_app: DeployedElektro, tmp_path: Path) -> None:
    """A file uploaded with a dataset id is created and backed by a store."""
    dataset = create_dataset(name="test_from_file_like_into_dataset")

    path = tmp_path / "payload.bin"
    path.write_bytes(b"\x00\x01\x02\x03payload")

    file = from_file_like(
        name="payload.bin",
        file=str(path),
        dataset=dataset.id,
    )

    assert file.id, "Did not get a file id back"
    assert file.store.key, "Store did not get a key assigned during upload"


@pytest.mark.integration
def test_get_file_roundtrip(deployed_app: DeployedElektro, tmp_path: Path) -> None:
    """A file uploaded via ``from_file_like`` can be fetched again with ``get_file``."""
    path = tmp_path / "roundtrip.dat"
    path.write_bytes(b"roundtrip-data")

    created = from_file_like(name="roundtrip.dat", file=str(path))
    fetched = get_file(created.id)

    assert fetched.id == created.id, "get_file returned a different file"
    assert fetched.name == created.name, "get_file returned an inconsistent name"

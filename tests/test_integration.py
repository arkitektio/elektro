"""Integration tests for writing, reading and creating datasets and traces."""

from pathlib import Path

import numpy as np
import pytest

from elektro.elektro import Elektro


@pytest.mark.integration
def test_write_random(elektro: Elektro) -> None:
    """Writing a random array into a folder returns an id and the expected shape."""
    folder = elektro.create_folder(name="test_write_random")
    x = elektro.create_array_dataset(
        data=np.random.random((1000,)),
        scales=[],
        name="test_random_write",
        axes=["t"],
        folder=folder.id,
    )
    assert x.id, "Did not get a dataset back"
    assert x.data.shape == (1000,), "Did not write the data the declaration described"


@pytest.mark.integration
def test_get_written(elektro: Elektro) -> None:
    """A written dataset is fetched back by id, and listed by the folder it is in."""
    folder = elektro.create_folder(name="test_get_written")
    written = elektro.create_array_dataset(
        data=np.random.random((1000,)),
        scales=[],
        name="test_random_write",
        axes=["t"],
        folder=folder.id,
    )

    assert elektro.get_array_dataset(written.id).id == written.id
    assert [d.id for d in elektro.get_array_datasets(filters={"folder": folder.id})] == [written.id]


@pytest.mark.integration
def test_create_folder(elektro: Elektro) -> None:
    """``create_folder`` returns a folder with an id."""
    x = elektro.create_folder(name="johannes")
    assert x.id, "Was not able to create a folder"


@pytest.mark.integration
def test_from_file_like(elektro: Elektro, tmp_path: Path) -> None:
    """Uploading a file-like object returns a File backed by a store.

    This exercises the full ``from_file_like`` path: the ``FileLike`` scalar is
    coerced, the ``UploadMiddleware`` requests big-file credentials and uploads
    the bytes to the datalayer, and the ``fromFileLike`` mutation is sent.
    """
    path = tmp_path / "hello.txt"
    path.write_bytes(b"hello elektro integration test\n")

    # The FileLike scalar coerces a path string into an opened file on validation.
    file = elektro.from_file_like(file_name="hello.txt", file=str(path))

    assert file.id, "Did not get a file id back"
    assert file.name, "File did not come back with a name"
    assert file.store is not None, "File was not backed by a store"
    assert file.store.key, "Store did not get a key assigned during upload"


@pytest.mark.integration
def test_from_file_like_into_folder(elektro: Elektro, tmp_path: Path) -> None:
    """A file uploaded with a folder id is created and backed by a store."""
    folder = elektro.create_folder(name="test_from_file_like_into_folder")

    path = tmp_path / "payload.bin"
    path.write_bytes(b"\x00\x01\x02\x03payload")

    file = elektro.from_file_like(
        file_name="payload.bin",
        file=str(path),
        folder=folder.id,
    )

    assert file.id, "Did not get a file id back"
    assert file.store.key, "Store did not get a key assigned during upload"


@pytest.mark.integration
def test_get_file_roundtrip(elektro: Elektro, tmp_path: Path) -> None:
    """A file uploaded via ``from_file_like`` can be fetched again with ``get_file``."""
    path = tmp_path / "roundtrip.dat"
    path.write_bytes(b"roundtrip-data")

    created = elektro.from_file_like(file_name="roundtrip.dat", file=str(path))
    fetched = elektro.get_file(created.id)

    assert fetched.id == created.id, "get_file returned a different file"
    assert fetched.name == created.name, "get_file returned an inconsistent name"

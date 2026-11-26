"""A big file is written so the object store verifies its digest: the server's part size, SHA-256 on each part."""

import io
from types import SimpleNamespace
from typing import Any, cast

import pytest

from elektro.io import upload


def test_the_part_size_is_the_servers() -> None:
    """The same function as arkitekt-datalayer's `digest.part_size_for`: 8 MiB, doubled to fit 10,000 parts."""
    floor = 8 * 1024 * 1024
    assert upload.part_size_for(0) == floor
    assert upload.part_size_for(floor * 10_000) == floor
    assert upload.part_size_for(floor * 10_000 + 1) == 2 * floor


def test_what_a_write_will_send_is_measured_and_left_in_place(tmp_path: Any) -> None:  # noqa: ANN401
    stream = io.BytesIO(b"0123456789")
    stream.seek(3)
    assert upload._remaining_bytes(stream) == 7
    assert stream.tell() == 3
    assert upload._remaining_bytes(b"abc") == 3
    path = tmp_path / "f.bin"
    path.write_bytes(b"x" * 5)
    assert upload._remaining_bytes(path) == 5


def test_a_big_file_store_sends_sha256_on_every_part(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from elektro.io.obstore import create_s3_store

    grant = SimpleNamespace(
        access_key="AK",
        secret_key="SK",
        session_token="T",
        bucket="b",
        key="k",
        store="1",
        expires_in=3600,
    )
    store = create_s3_store(
        "http://s3.test", cast(Any, grant), checksum_algorithm=upload.BIGFILE_CHECKSUM
    )
    assert cast(dict[str, Any], store.config)["checksum_algorithm"] == "SHA256"

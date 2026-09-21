"""Helpers for downloading Zarr, Parquet and big-file data from the DataLayer."""

from elektro.api.schema import (
    ZarrAccessGrant,
    ParquetAccessGrant,
    BigFileAccessGrant,
)
from elektro.datalayer import DataLayer
from elektro.errors import NoDataLayerFound, NoElektroFound
from elektro.rath import ElektroRath
from koil import unkoil
from rath.origin import get_origin
import aiohttp
from pathlib import Path
from typing import TYPE_CHECKING, Any, Tuple, cast
import obstore  # Imported to access direct streaming capabilities

from elektro.io.obstore import (
    ParquetDatasetViaObstore,
    create_s3_store,
    create_zarr_store_path,
)
from rath.scalars import ID
from zarr.storage import StorePath

if TYPE_CHECKING:
    from elektro.elektro import Elektro
    from duckdb import DuckDBPyConnection, DuckDBPyRelation


async def aget_zarr_credentials_and_endpoint(
    store: str,
    rath: ElektroRath,
    datalayer: DataLayer,
) -> Tuple[ZarrAccessGrant, str]:
    """Fetch zarr access credentials and the datalayer endpoint URL.

    Both clients are taken as given: callers pick them (see :func:`_clients`)
    before crossing into the event loop.
    """
    credentials = await _as_client(rath, datalayer).arequest_zarr_access(ID.validate(store))
    endpoint_url = await datalayer.get_endpoint_url()
    return credentials, endpoint_url


async def aget_table_credentials_and_endpoint(
    store: str,
    rath: ElektroRath,
    datalayer: DataLayer,
) -> Tuple[ParquetAccessGrant, str]:
    """Fetch parquet access credentials and the datalayer endpoint URL.

    Both clients are taken as given: callers pick them (see :func:`_clients`)
    before crossing into the event loop.
    """
    credentials = await _as_client(rath, datalayer).arequest_parquet_access(ID.validate(store))
    endpoint_url = await datalayer.get_endpoint_url()
    return credentials, endpoint_url


async def aget_bigfile_credentials_and_endpoint(
    store: str,
    rath: ElektroRath,
    datalayer: DataLayer,
) -> Tuple[BigFileAccessGrant, str]:
    """Fetch big-file access credentials and the datalayer endpoint URL.

    Both clients are taken as given: callers pick them (see :func:`_clients`)
    before crossing into the event loop.
    """
    credentials = await _as_client(rath, datalayer).arequest_bigfile_access(ID.validate(store))
    endpoint_url = await datalayer.get_endpoint_url()
    return credentials, endpoint_url


def _as_client(rath: ElektroRath, datalayer: DataLayer) -> "Elektro":
    """A client over an already-picked rath and datalayer, to call operations on.

    Not entered and not owning either: whoever picked them owns their lifetime.
    It carries no task token, so access requests made through it are not
    attributed to a task.
    """
    from elektro.elektro import Elektro

    return Elektro.model_construct(rath=rath, datalayer=datalayer, task_token=None)


def _datalayer(datalayer: DataLayer | None, obj: Any) -> DataLayer:  # noqa: ANN401
    """The datalayer given, else the one ``obj`` was fetched with.

    Raises:
        NoDataLayerFound: If neither provides one.
    """
    if datalayer is not None:
        return datalayer
    origin = get_origin(obj)
    found = origin.clients.get("datalayer") if origin is not None else None
    if found is None:
        raise NoDataLayerFound(
            f"{type(obj).__name__} was not fetched through an Elektro client, so there "
            "is no datalayer to read it with. Pass one explicitly (datalayer=...)."
        )
    return found


def _clients(
    rath: ElektroRath | None,
    datalayer: DataLayer | None,
    obj: Any,  # noqa: ANN401
) -> Tuple[ElektroRath, DataLayer]:
    """Both clients for a call: the ones given, else the ones ``obj`` was fetched with.

    ``obj`` is the object the call is made on. Nothing is looked up in what happens
    to be current. Picked here rather than deeper down because the sync entry points
    cross into the event loop.

    Raises:
        NoElektroFound: If neither gives a rath.
        NoDataLayerFound: If neither gives a datalayer.
    """
    if rath is None:
        origin = get_origin(obj)
        # Only ever bound by elektro's own executor, so it is an ElektroRath.
        rath = cast("ElektroRath | None", origin.rath if origin is not None else None)
        if rath is None:
            raise NoElektroFound(
                f"{type(obj).__name__} was not fetched through an Elektro client, so "
                "there is none to call through. Pass the clients explicitly (rath=..., "
                "datalayer=...)."
            )
    return rath, _datalayer(datalayer, obj)


async def aopen_zarr_store(
    store_id: str,
    cache: int = 2**30,
    *,
    rath: ElektroRath | None = None,
    datalayer: DataLayer | None = None,
    obj: Any = None,  # noqa: ANN401
) -> StorePath:
    """Open a zarr store for the given store ID asynchronously."""
    rath, datalayer = _clients(rath, datalayer, obj)
    credentials, endpoint_url = await aget_zarr_credentials_and_endpoint(store_id, rath, datalayer)
    return create_zarr_store_path(endpoint_url, credentials)


def open_zarr_store(
    store_id: str,
    cache: int = 2**30,
    *,
    rath: ElektroRath | None = None,
    datalayer: DataLayer | None = None,
    obj: Any = None,  # noqa: ANN401
) -> StorePath:
    """Open a zarr store for the given store ID synchronously."""
    rath, datalayer = _clients(rath, datalayer, obj)
    credentials, endpoint_url = unkoil(
        aget_zarr_credentials_and_endpoint, store_id, rath, datalayer
    )
    return create_zarr_store_path(endpoint_url, credentials)


async def aopen_parquet_filesytem(
    store_id: str,
    *,
    rath: ElektroRath | None = None,
    datalayer: DataLayer | None = None,
    obj: Any = None,  # noqa: ANN401
) -> ParquetDatasetViaObstore:
    """Open a parquet dataset for the given store ID asynchronously."""
    try:
        import pyarrow.parquet as pq  # type: ignore # noqa: F401
    except ImportError as e:
        raise ImportError("You need to install pyarrow to use this function") from e
    rath, datalayer = _clients(rath, datalayer, obj)
    credentials, endpoint_url = await aget_table_credentials_and_endpoint(
        store_id, rath, datalayer
    )
    return ParquetDatasetViaObstore(create_s3_store(endpoint_url, credentials), credentials.key)


def open_parquet_filesystem(
    store_id: str,
    *,
    rath: ElektroRath | None = None,
    datalayer: DataLayer | None = None,
    obj: Any = None,  # noqa: ANN401
) -> ParquetDatasetViaObstore:
    """Open a parquet dataset for the given store ID synchronously."""
    try:
        import pyarrow.parquet as pq  # type: ignore # noqa: F401
    except ImportError as e:
        raise ImportError("You need to install pyarrow to use this function") from e
    rath, datalayer = _clients(rath, datalayer, obj)
    credentials, endpoint_url = unkoil(
        aget_table_credentials_and_endpoint, store_id, rath, datalayer
    )
    return ParquetDatasetViaObstore(create_s3_store(endpoint_url, credentials), credentials.key)


async def aopen_parquet_duckdb(
    store_id: str,
    *,
    rath: ElektroRath | None = None,
    datalayer: DataLayer | None = None,
    obj: Any = None,  # noqa: ANN401
) -> Tuple["DuckDBPyConnection", "DuckDBPyRelation"]:
    """Open a lazy DuckDB relation over the parquet object asynchronously.

    Returns ``(connection, relation)``. The connection is returned alongside the
    relation because the relation is only valid while its connection is alive, so
    the caller must keep a reference to it.
    """
    from elektro.io.duckdb_io import (
        create_duckdb_s3_connection,
        read_parquet_relation,
    )

    rath, datalayer = _clients(rath, datalayer, obj)
    credentials, endpoint_url = await aget_table_credentials_and_endpoint(
        store_id, rath, datalayer
    )
    con = create_duckdb_s3_connection(endpoint_url, credentials)
    relation = read_parquet_relation(con, credentials.bucket, credentials.key)
    return con, relation


def open_parquet_duckdb(
    store_id: str,
    *,
    rath: ElektroRath | None = None,
    datalayer: DataLayer | None = None,
    obj: Any = None,  # noqa: ANN401
) -> Tuple["DuckDBPyConnection", "DuckDBPyRelation"]:
    """Open a lazy DuckDB relation over the parquet object synchronously.

    Returns ``(connection, relation)``; keep a reference to the connection for as
    long as the relation is used (the relation is bound to it).
    """
    rath, datalayer = _clients(rath, datalayer, obj)
    return unkoil(aopen_parquet_duckdb, store_id, rath=rath, datalayer=datalayer)


def _ensure_parent_directory(file_name: str) -> None:
    """Create parent directories for file_name if they do not exist."""
    parent = Path(file_name).expanduser().resolve().parent
    parent.mkdir(parents=True, exist_ok=True)


async def adownload_presigned_file(
    presigned_url: str,
    file_name: str,
    datalayer: DataLayer | None = None,
    *,
    obj: Any = None,  # noqa: ANN401
) -> str:
    """Download a file from a presigned URL and save it to file_name asynchronously.

    Args:
        presigned_url: The presigned URL path (appended to the endpoint URL).
        file_name: Local path to write the downloaded file to.
        datalayer: Optional DataLayer override.
        obj: The object the download is made on; its origin gives the datalayer
            when none is given.

    Returns:
        The local path where the file was saved.
    """
    datalayer = _datalayer(datalayer, obj)

    endpoint_url = await datalayer.get_endpoint_url()
    _ensure_parent_directory(file_name)

    # Stream the file in 1 MiB chunks to avoid per-read syscall overhead.
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint_url + presigned_url) as response:
            response.raise_for_status()
            with open(file_name, "wb") as file:
                while True:
                    chunk = await response.content.read(1024 * 1024)
                    if not chunk:
                        break
                    file.write(chunk)

    return file_name


def download_presigned_file(
    presigned_url: str,
    file_name: str,
    datalayer: DataLayer | None = None,
    *,
    obj: Any = None,  # noqa: ANN401
) -> str:
    """Download a file from a presigned URL and save it to file_name synchronously.

    Args:
        presigned_url: The presigned URL path (appended to the endpoint URL).
        file_name: Local path to write the downloaded file to.
        datalayer: Optional DataLayer override.
        obj: The object the download is made on; its origin gives the datalayer
            when none is given.

    Returns:
        The local path where the file was saved.
    """
    return unkoil(
        adownload_presigned_file,
        presigned_url,
        file_name=file_name,
        datalayer=_datalayer(datalayer, obj),
    )


async def adownload_file(
    store_id: str,
    file_name: str,
    datalayer: DataLayer | None = None,
    *,
    rath: ElektroRath | None = None,
    obj: Any = None,  # noqa: ANN401
) -> str:
    """Download a big file from the store and save it to file_name asynchronously.

    Args:
        store_id: The ID of the big-file store to download from.
        file_name: Local path to write the downloaded file to.
        datalayer: Optional DataLayer override.
        rath: Optional rath client override.
        obj: The object the download is made on; its origin is used when nothing
            explicit is given.

    Returns:
        The local path where the file was saved.
    """
    rath, datalayer = _clients(rath, datalayer, obj)
    credentials, endpoint_url = await aget_bigfile_credentials_and_endpoint(
        store_id, rath, datalayer
    )

    _ensure_parent_directory(file_name)
    store = create_s3_store(endpoint_url, credentials)

    # Stream the file asynchronously directly into the file object
    response = await obstore.get_async(store, credentials.key)
    with open(file_name, "wb") as file:
        async for chunk in response.stream():
            file.write(chunk)

    return file_name


def download_file(
    store_id: str,
    file_name: str,
    datalayer: DataLayer | None = None,
    *,
    rath: ElektroRath | None = None,
    obj: Any = None,  # noqa: ANN401
) -> str:
    """Download a big file from the store and save it to file_name synchronously.

    Args:
        store_id: The ID of the big-file store to download from.
        file_name: Local path to write the downloaded file to.
        datalayer: Optional DataLayer override.
        rath: Optional rath client override.
        obj: The object the download is made on; its origin is used when nothing
            explicit is given.

    Returns:
        The local path where the file was saved.
    """
    rath, datalayer = _clients(rath, datalayer, obj)
    credentials, endpoint_url = unkoil(
        aget_bigfile_credentials_and_endpoint, store_id, rath, datalayer
    )

    _ensure_parent_directory(file_name)
    store = create_s3_store(endpoint_url, credentials)

    # Stream the file synchronously directly into the file object
    response = obstore.get(store, credentials.key)
    with open(file_name, "wb") as file:
        for chunk in response.stream():
            file.write(chunk)

    return file_name

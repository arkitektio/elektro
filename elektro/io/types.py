"""Protocol definitions for naming, uploading and downloading DataLayer files."""

from typing import (
    Protocol,
    Any,
    runtime_checkable,
    Optional,
    Tuple,
    Awaitable,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from elektro.api.schema import (
        Credentials,
    )
from concurrent.futures import ThreadPoolExecutor


@runtime_checkable
class Namer(Protocol):
    """Protocol for Namer

    Protocol for Uploader

    This protocol is used to define the interface for uploading
    files to a Datalayer. It should return the s3_path to the file
    """

    def __call__(
        self,
        file: Any,
    ) -> Awaitable[Tuple[str, str]]:
        """Return the s3 path (bucket and key) for the given file."""
        ...


@runtime_checkable
class Downloader(Protocol):
    """Protocol for objects that download a file from the DataLayer."""

    def __call__(
        self,
        file: str,
        endpoint_url: str,
        bucket: str,
        key: str,
        credentials: "Credentials",
        executor: Optional[ThreadPoolExecutor] = None,
    ) -> Any:
        """Download a file from the DataLayer and return the local path."""
        ...


@runtime_checkable
class Uploader(Protocol):
    """Protocol for Uploader

    This protocol is used to define the interface for uploading
    files to a Datalayer. It should return the s3_path to the file

    """

    def __call__(
        self,
        file: Any,
        credentials: "Credentials",
        endpoint_url: str,
        executor: Optional[ThreadPoolExecutor] = None,
    ) -> str:
        """Upload the file to the DataLayer and return its s3 path."""
        ...

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
    from mikro_new.api.schema import (
        CredentialsFragment as Credentials,
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
    ) -> Awaitable[Tuple[str, str]]: ...


@runtime_checkable
class Downloader(Protocol):
    def __call__(
        self,
        file: str,
        endpoint_url: str,
        bucket: str,
        key: str,
        credentials: "Credentials",
        executor: Optional[ThreadPoolExecutor] = None,
    ) -> Any: ...


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
    ) -> str: ...

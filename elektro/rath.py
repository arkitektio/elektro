from pydantic import Field
from .links.upload import UploadLink
from rath import rath
import contextvars
from rath.links.auth import AuthTokenLink
from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.file import FileExtraction
from rath.links.split import SplitLink
from typing import Optional


current_elektro_rath: contextvars.ContextVar[Optional["ElektroRath"]] = (
    contextvars.ContextVar("current_elektro_rath")
)


class ElektroLinkComposition(TypedComposedLink):
    """The ElektroLinkComposition

    This is a composition of links that are traversed before a request is sent to the
    mikro api. This link composition contains the default links for elektro.

    You shouldn't need to create this directly.
    """

    fileextraction: FileExtraction = Field(default_factory=FileExtraction)
    """ A link that extracts files from the request and follows the graphql multipart request spec"""
    dicting: DictingLink = Field(default_factory=DictingLink)
    """ A link that converts basemodels to dicts"""
    upload: UploadLink
    """ A link that uploads supported data types like numpy arrays and parquet files to the datalayer"""
    auth: AuthTokenLink
    """ A link that splits the request into a http and a websocket request"""
    split: SplitLink


class ElektroRath(rath.Rath):
    """Mikro Rath

    Mikro Rath is the GraphQL client for elektro It is a thin wrapper around Rath
    that provides some default links and a context manager to set the current
    client. (This allows you to use the `elektrorath.current` function to get the
    current client, within the context of mikro app).

    This is a subclass of Rath that adds some default links to convert files and array to support
    the graphql multipart request spec."""

    link: ElektroLinkComposition

    async def __aenter__(self) -> "ElektroRath":
        """Sets the current elektro rath to this instance"""
        await super().__aenter__()
        current_elektro_rath.set(self)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        """Resets the current elektro rath to None"""
        await super().__aexit__(exc_type, exc_val, exc_tb)
        current_elektro_rath.set(None)

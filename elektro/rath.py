from types import TracebackType
from typing import List, Optional
from pydantic import Field
from rath import rath
import contextvars
from rath.links.auth import AuthTokenLink
from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.file import FileExtraction
from rath.links.split import SplitLink
from kanne.contrib.rath.coerce_pint import CoercePintLink
from elektro.middleware.base import FuncsMiddleware


current_elektro_rath: contextvars.ContextVar[Optional["ElektroRath"]] = (
    contextvars.ContextVar("current_elektro_rath")
)


class ElektroLinkComposition(TypedComposedLink):
    """The ElektroLinkComposition

    This is a composition of links that are traversed before a request is sent to the
    elektro api. This link composition contains the default links for elektro.

    Upload logic has been moved to the UploadMiddleware, which runs at the funcs
    level before the rath link chain is entered.

    You shouldn't need to create this directly.
    """

    fileextraction: FileExtraction = Field(default_factory=FileExtraction)
    """ A link that extracts files from the request and follows the graphql multipart request spec"""

    dicting: DictingLink = Field(default_factory=DictingLink)
    """ A link that converts basemodels to dicts"""

    coerce_pint_link: CoercePintLink = Field(default_factory=CoercePintLink)
    """ A link that coerces pint quantities into their magnitude representation"""

    auth: AuthTokenLink
    """ A link that adds auth tokens to the request"""
    split: SplitLink
    """ A link that splits the request into a http and a websocket request"""


class ElektroRath(rath.Rath):
    """Elektro Rath

    Elektro Rath is the GraphQL client for elektro It is a thin wrapper around Rath
    that provides some default links and a context manager to set the current
    client. (This allows you to use the `elektrorath.current` function to get the
    current client, within the context of elektro app).

    This is a subclass of Rath that adds some default links to convert files and array to support
    the graphql multipart request spec.

    Attributes:
        middlewares: A list of FuncsMiddleware instances that process serialized
            variables before they reach the rath link chain. Middleware runs in
            order: first middleware processes first, then passes to the next.
    """

    middlewares: List[FuncsMiddleware] = Field(default_factory=list)
    """Middleware chain applied to serialized variables in funcs.execute/subscribe."""

    async def __aenter__(self) -> "ElektroRath":
        """Sets the current elektro rath to this instance"""
        await super().__aenter__()
        for mw in self.middlewares:
            await mw.aenter()
        current_elektro_rath.set(self)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Resets the current elektro rath to None"""
        for mw in self.middlewares:
            await mw.aexit()
        await super().__aexit__(exc_type, exc_val, exc_tb)
        current_elektro_rath.set(None)

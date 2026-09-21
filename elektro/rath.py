"""The Elektro GraphQL transport layer (Rath) and its link configuration."""

from types import TracebackType
from typing import List
from pydantic import Field
from rath import rath
from rath.links.auth import AuthTokenLink
from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.file import FileExtraction
from rath.links.split import SplitLink
from kanne.contrib.rath.coerce_pint import CoercePintLink
from elektro.middleware.base import OperationMiddleware


class ElektroLinkComposition(TypedComposedLink):
    """The ElektroLinkComposition

    This is a composition of links that are traversed before a request is sent to the
    elektro api. This link composition contains the default links for elektro.

    Upload logic has been moved to the UploadMiddleware, which runs at the operation
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
        middlewares: A list of OperationMiddleware instances that process serialized
            variables before they reach the rath link chain. Middleware runs in
            order: first middleware processes first, then passes to the next.
    """

    middlewares: List[OperationMiddleware] = Field(default_factory=list)
    """Middleware chain applied to serialized variables in Elektro.execute/subscribe."""

    async def __aenter__(self) -> "ElektroRath":
        """Enter the client and its middlewares.

        Entering does not make it "the current client": only the elektro service
        that owns it is current while entered (see :class:`elektro.elektro.Elektro`).
        A rath used on its own is passed where it is needed, as ``rath=``.
        """
        await super().__aenter__()
        for mw in self.middlewares:
            await mw.aenter()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the middlewares and the client"""
        for mw in self.middlewares:
            await mw.aexit()
        await super().__aexit__(exc_type, exc_val, exc_tb)

"""Which client a call on an elektro object goes through.

The one passed explicitly, else the one that fetched the object: every result
remembers its client (``Elektro._origin``), so a follow-up call from an object
reaches the same server, rath and datalayer that produced it. Nothing is looked up
in what happens to be current.
"""

from typing import TYPE_CHECKING, Any

from rath.origin import get_origin

from elektro.errors import NoElektroFound

if TYPE_CHECKING:
    from elektro.elektro import Elektro


def client_of(obj: Any, elektro: "Elektro | None" = None) -> "Elektro":  # noqa: ANN401
    """The client for a call on ``obj``: ``elektro`` if given, else the one that fetched it.

    Raises:
        NoElektroFound: If none was given and ``obj`` was not fetched through a
            client (built by hand, or unpickled: an origin does not travel).
    """
    if elektro is not None:
        return elektro

    from elektro.elektro import Elektro

    origin = get_origin(obj)
    client = origin.client if origin is not None else None
    if isinstance(client, Elektro):
        return client
    raise NoElektroFound(
        f"{type(obj).__name__} was not fetched through an Elektro client, so there is "
        "none to call through. Pass one explicitly (elektro=...)."
    )


__all__ = ["client_of"]

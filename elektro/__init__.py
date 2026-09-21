"""Elektro client package for interacting with the Elektro backend service."""

import logging
from .elektro import Elektro

logger = logging.getLogger(__name__)


try:
    from .arkitekt import elektro as elektro_service
except ImportError as e:
    # Only "rekuest is not installed" may pass silently. Anything else that fails
    # to import here (a renamed query, a rekuest too old for what the module
    # needs) is a bug, and hiding it makes this package's service vanish
    # without a word. Whether it is installed is asked the plain way.
    try:
        import rekuest  # noqa: F401 -- presence is the question
    except ImportError:
        pass
    else:
        raise e


__all__ = [
    "Elektro",
    "elektro_service",
]

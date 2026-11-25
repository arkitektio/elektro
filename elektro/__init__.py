"""Elektro client package for interacting with the Elektro backend service."""

import logging

from .elektro import Elektro

logger = logging.getLogger(__name__)

__all__ = ["Elektro"]

# Marks every type elektro sends by id, so an app using `Elektro` finds them.
from . import structures as _structures  # noqa: E402, F401

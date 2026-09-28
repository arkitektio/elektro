"""Elektro client package for interacting with the Elektro backend service."""

import logging
from .elektro import Elektro

logger = logging.getLogger(__name__)


# The service is declared with arkitekt-spec, a core dependency: it is always there.
from .arkitekt import elektro as elektro_service

__all__ = [
    "Elektro",
    "elektro_service",
]

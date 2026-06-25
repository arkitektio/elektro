"""Elektro client package for interacting with the Elektro backend service."""

import logging
from .elektro import Elektro

logger = logging.getLogger(__name__)


try:
    from .arkitekt import ElektroService
except ImportError as e:
    logger.debug("Could not import ElektroService", e)
try:
    from .rekuest import structure_reg
except ImportError as e:
    logger.debug("Could not import structure_reg", e)


__all__ = [
    "Elektro",
    "structure_reg",
    "ElektroService",
]

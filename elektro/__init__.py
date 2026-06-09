import logging
from .elektro import Elektro

logger = logging.getLogger(__name__)


try:
    from .arkitekt import ElektroService
except ImportError as e:
    pass
try:
    from .rekuest import structure_reg
except ImportError as e:
    logger.debug("Could not import structure_reg", e)
    pass
    pass


__all__ = [
    "Elektro",
    "structure_reg",
    "ElektroService",
]

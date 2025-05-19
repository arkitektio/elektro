class ElektroError(Exception):
    """Base class for all Mikro errors."""


class NoElektroFound(ElektroError):
    """Caused when no Mikro is found."""


class NoDataLayerFound(ElektroError):
    """Caused when no DataLayer is found."""


class NotQueriedError(ElektroError):
    """Caused when a field has not been queries"""

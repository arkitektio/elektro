from .elektro import Elektro

try:
    from .arkitekt import ElektroService
except ImportError:
    pass
try:
    from .rekuest import structure_reg

    print("Imported structure_reg")
except ImportError as e:
    print("Could not import structure_reg", e)
    raise e
    pass


__all__ = [
    "Elektro",
    "structure_reg",
    "ElektroService",
]

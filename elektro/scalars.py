"""
Custom scalars for elektro


"""

import io
import os
import mimetypes
from typing import Any, IO, List, Optional
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
import xarray as xr
import pandas as pd
import numpy as np
import uuid
from collections.abc import Iterable


def is_dask_array(v: Any) -> bool:
    """Check if the input is a dask array."""
    try:
        import dask.array.core as da

        return isinstance(v, da.Array)
    except ImportError:
        return False
    except Exception as e:
        raise ValueError(f"Error checking for dask array: {e}")


class AssignationID(str):
    """A custom scalar to represent an affine matrix."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_before_validator_function(cls.validate, handler(str))

    @classmethod
    def validate(cls, v: Any) -> "AssignationID":
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class RGBAColor(list):
    """A custom scalar to represent an affine matrix."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> "RGBAColor":
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class XArrayConversionException(Exception):
    """An exception that is raised when a conversion to xarray fails."""

    pass


MetricValue = Any
FeatureValue = Any

TraceCoercible = xr.DataArray | np.ndarray | list | tuple
ArrayLikeCoercible = xr.DataArray | np.ndarray | list | tuple

# Raw inputs accepted by the ``FileLike``/``BigFileLike`` scalar validators: either a
# path string (opened in binary mode on validation) or an already-opened file object.
# Used as the argument type in generated resolvers so callers do not need to construct
# the scalar wrapper themselves (see ``coercible_scalars`` in graphql.config.yaml).
FileLikeCoercible = str | IO
BigFileLikeCoercible = str | IO


class Upload:
    """A custom scalar for ensuring an interface to files api supported by elektro It converts the graphql value
    (a string pointed to a zarr store) into a downloadable file. To access the file you need to call the download
    method. This is done to avoid unnecessary requests to the datalayer api.
    """

    __file__ = True

    def __init__(self, value: Any) -> None:
        """Initialize the upload with the underlying file value."""
        self.value = value

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: Any) -> "Upload":
        """Validate the input value and wrap it in an Upload."""
        # you could also return a string here which would mean model.post_code
        # would be a string, pydantic won't care but you could end up with some
        # confusion since the value's type won't match the type annotation
        # exactly
        return cls(v)

    def __repr__(self) -> str:
        """Return a string representation of the Upload."""
        return f"Upload({self.value})"


class Micrometers(float):
    """A custom scalar to represent a micrometer."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_before_validator_function(cls.validate, handler(float))

    @classmethod
    def validate(cls, v: Any) -> "Micrometers":
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class Microliters(float):
    """A custom scalar to represent a a microliter."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_before_validator_function(cls.validate, handler(float))

    @classmethod
    def validate(cls, v: Any) -> "Microliters":
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class Micrograms(float):
    """A custom scalar to represent a a microgram."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_before_validator_function(cls.validate, handler(float))

    @classmethod
    def validate(cls, v: Any) -> "Micrograms":
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class Milliseconds(float):
    """A custom scalar to represent a micrometer."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_before_validator_function(cls.validate, handler(float))

    @classmethod
    def validate(cls, v: Any) -> "Milliseconds":
        """Validate the input array and convert it to a xr.DataArray."""
        return cls(v)


class TwoDVector(list):
    """A custom scalar to represent a vector."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> "TwoDVector":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 1
            v = v.tolist()

        if not isinstance(v, Iterable):
            raise ValueError("The input must be a list or a 1-D numpy array.")
        if not isinstance(v, list):
            v = list(v)

        validated_list = []
        for i in v:
            if isinstance(i, (np.integer, np.floating)):
                validated = float(i) if isinstance(i, np.floating) else int(i)
            else:
                validated = i

            if not isinstance(validated, (int, float)):
                raise ValueError(
                    f"The input must be a list of integers or floats. You provided a list of {type(validated)}"
                )

            validated_list.append(validated)
        if len(validated_list) != 2:
            raise ValueError(
                f"The input must be a list of 2 elements (x, y). You provided a list of {len(v)} elements"
            )
        return cls(validated_list)

    def as_vector(self) -> np.ndarray:
        """Return the vector as a flattened numpy array."""
        return np.array(self).reshape(-1)


class ThreeDVector(list):
    """A custom scalar to represent a vector."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> "ThreeDVector":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 1
            v = v.tolist()

        assert isinstance(v, list)
        assert len(v) == 3
        return cls(v)

    def as_vector(self) -> np.ndarray:
        """Return the vector as a flattened numpy array."""
        return np.array(self).reshape(-1)


class FourDVector(list):
    """A custom scalar to represent a vector."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> "FourDVector":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 1
            v = v.tolist()

        assert isinstance(v, list)
        assert len(v) == 4
        return cls(v)

    def as_vector(self) -> np.ndarray:
        """Return the vector as a flattened numpy array."""
        return np.array(self).reshape(-1)


class FiveDVector(list):
    """A custom scalar to represent a vector."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> list:
        """Validate the input array and convert it to a xr.DataArray."""

        if isinstance(v, np.ndarray):
            if not v.ndim == 1:
                raise ValueError("The input array must be a 1D array")
            v = v.tolist()

        if not isinstance(v, Iterable):
            raise ValueError("The input must be a list or a 1-D numpy array.")

        if not isinstance(v, list):
            v = list(v)

        for i in v:
            if not isinstance(i, (int, float)):
                raise ValueError(
                    f"The input must be a list of integers or floats. You provided a list of {type(i)}"
                )

        if len(v) < 2 or len(v) > 5:
            raise ValueError(
                f"The input must be a list or at least 2 elements (x, y) but not more than 5e lements (c, t, z, x, y). Every additional element is a z value (c, t, z, x, y). You provided a list o {len(v)} elements"
            )

        # prepend list with zeros
        if len(v) < 5:
            v = [0] * (5 - len(v)) + v

        return v

    @classmethod
    def list_from_numpyarray(
        cls: "FiveDVector",
        x: np.ndarray,
        t: Optional[int] = None,
        c: Optional[int] = None,
        z: Optional[int] = None,
    ) -> List["FiveDVector"]:
        """Creates a list of FiveDVectors from a numpy array

        Args:
            vector_list (List[List[float]]): A list of lists of floats

        Returns:
            List[Vectorizable]: A list of InputVector
        """
        assert x.ndim == 2, "Needs to be a List array of vectors"
        if x.shape[1] == 4:
            return [FiveDVector([c] + i) for i in x.tolist()]
        elif x.shape[1] == 3:
            return [FiveDVector([c, t] + i) for i in x.tolist()]
        elif x.shape[1] == 2:
            return [FiveDVector([c, t, z] + i) for i in x.tolist()]
        else:
            raise NotImplementedError(
                f"Incompatible shape {x.shape} of {x}. List dimension needs to either be of size 2 or 3"
            )

    def as_vector(self) -> np.ndarray:
        """Return the vector as a flattened numpy array."""
        return np.array(self).reshape(-1)


class Matrix(list):
    """A custom scalar to represent an affine matrix."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> "Matrix":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 2
            assert v.shape[0] == v.shape[1]
            assert v.shape == (3, 3)
            v = v.tolist()

        assert isinstance(v, list)
        return cls(v)

    def as_matrix(self) -> np.ndarray:
        """Return the matrix as a 3x3 numpy array."""
        return np.array(self).reshape(3, 3)


class FourByFourMatrix(list):
    """A custom scalar to represent a four by four matrix (e.g 3D affine matrix.)"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: Any) -> "FourByFourMatrix":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, np.ndarray):
            assert v.ndim == 2
            assert v.shape[0] == v.shape[1]
            assert v.shape == (4, 4)
            v = v.tolist()

        assert isinstance(v, list)
        return cls(v)

    def as_matrix(self) -> np.ndarray:
        """Return the matrix as a 3x3 numpy array."""
        return np.array(self).reshape(3, 3)

    @classmethod
    def from_np(cls, v: np.ndarray) -> "FourByFourMatrix":
        """Validate the input array and convert it to a xr.DataArray."""
        assert v.ndim == 2
        assert v.shape[0] == v.shape[1]
        assert v.shape == (4, 4)
        v = v.tolist()
        return cls(v)


class TraceLike:
    """A custom scalar for wrapping of every supported array like structure on
    the mikro platform. This scalar enables validation of various array formats
    into a mikro api compliant xr.DataArray.."""

    def __init__(self, value: xr.DataArray) -> None:
        """Initialize the trace with the wrapped xr.DataArray value."""
        self.value = value
        self.key = str(uuid.uuid4())

    def __set__(self, instance: Any, value: TraceCoercible) -> None:
        """Set the descriptor value on the owning instance."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: TraceCoercible) -> "TraceLike":
        """Validate the input array and convert it to a xr.DataArray."""
        # initial coercion checks, if a numpy array is passed, we need to convert it to a xarray
        # but that means the user didnt pass the dimensions explicitly so we need to add them
        # but error if they do not make sense

        if isinstance(v, np.ndarray):
            v = xr.DataArray(v, dims=["c"])

        if not isinstance(v, xr.DataArray):
            raise ValueError("This needs to be a instance of xarray.DataArray")

        if v.ndim != 1:
            raise ValueError("This needs to be a 1D array")

        return cls(v)

    def __repr__(self) -> str:
        """Return a string representation of the TraceLike."""
        return f"TraceLike({self.value})"


class BigFile:
    """A custom scalar for wrapping of every supported array like structure on
    the mikro platform. This scalar enables validation of various array formats
    into a mikro api compliant xr.DataArray.."""

    def __init__(self, value: IO) -> None:
        """Initialize the big file with the wrapped file object."""
        self.value = value
        self.key = str(value.name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: Any) -> "BigFile":
        """Validate the input array and convert it to a xr.DataArray."""

        if isinstance(v, str):
            v = open(v, "rb")

        if not isinstance(v, io.IOBase):
            raise ValueError("This needs to be a instance of a file")

        return cls(v)

    def __repr__(self) -> str:
        """Return a string representation of the BigFile."""
        return f"BigFile({self.value})"


class ParquetLike:
    """A custom scalar for ensuring a common format to support write to the
    parquet api supported by elektro It converts the passed value into
    a compliant format.."""

    def __init__(self, value: pd.DataFrame) -> None:
        """Initialize the parquet wrapper with the source DataFrame."""
        self.value = value
        self.key = str(uuid.uuid4())

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: Any) -> "ParquetLike":
        """Validate the input value and wrap it as a ParquetLike."""
        if not isinstance(v, pd.DataFrame):
            raise ValueError("This needs to be a instance of pandas DataFrame")

        return cls(v)

    def __repr__(self) -> str:
        """Return a string representation of the ParquetLike."""
        return f"ParquetInput({self.value})"


class FileLike:
    """A custom scalar for ensuring a common format to support write to the
    parquet api supported by elektro It converts the passed value into
    a compliant format.."""

    def __init__(self, value: IO, name: str = "") -> None:
        """Initialize the file wrapper with the file object and its name."""
        self.value = value
        self.key = str(name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: Any) -> "FileLike":
        """Validate the input array and convert it to a xr.DataArray."""

        if isinstance(v, str):
            file = open(v, "rb")
            name = v
        else:
            file = v
            name = v.name

        if not isinstance(file, io.IOBase):
            raise ValueError("This needs to be a instance of a file")

        return cls(file, name=name)

    def __repr__(self) -> str:
        """Return a string representation of the FileLike."""
        return f"FileLikeInput({self.value})"


class MeshLike:
    """A custom scalar for ensuring a common format to support write to the
    mesh api supported by elektro It converts the passed value into
    a compliant format.."""

    def __init__(self, value: IO, name: str = "") -> None:
        """Initialize the mesh wrapper with the file object and its name."""
        self.value = value
        self.key = str(name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: Any) -> "MeshLike":
        """Validate the input array and convert it to a xr.DataArray."""

        if isinstance(v, str):
            file = open(v, "rb")
            name = v
        else:
            file = v
            name = v.name

        if not isinstance(file, io.IOBase):
            raise ValueError("This needs to be a instance of a file")

        return cls(file, name=name)

    def __repr__(self) -> str:
        """Return a string representation of the MeshLike."""
        return f"MeshLike({self.value})"


class ArrayLike:
    """A custom scalar for wrapping of every supported array like structure on
    the elektro platform. This scalar enables validation of various array formats
    into an elektro api compliant xr.DataArray. Unlike ``TraceLike`` it preserves
    the caller's labelled dimensions (and arbitrary dimensionality) verbatim."""

    def __init__(self, value: xr.DataArray) -> None:
        """Initialize the array wrapper with the wrapped xr.DataArray value."""
        self.value = value
        self.key = str(uuid.uuid4())

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: Any) -> "ArrayLike":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, xr.DataArray):
            return cls(v)

        if isinstance(v, np.ndarray) or is_dask_array(v):
            return cls(xr.DataArray(v))

        raise ValueError(
            f"Unsupported type {type(v)} for ArrayLike. Supported types are "
            "xr.DataArray, numpy.ndarray and dask.array.Array"
        )

    def __repr__(self) -> str:
        """Return a string representation of the ArrayLike."""
        return f"ArrayLike({self.value})"


class BigFileLike:
    """A custom scalar for ensuring a common format to support write to the
    big file api supported by elektro It converts the passed value into
    a compliant format.."""

    def __init__(self, value: IO, name: str = "") -> None:
        """Initialize the big file wrapper from the file object and its name."""
        self.value = value
        self.file_name = os.path.basename(name)
        self.key = self.file_name
        self.mime_type = mimetypes.guess_type(self.file_name)[0]

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: Any) -> "BigFileLike":
        """Validate the input file and convert it to a compliant format."""

        if isinstance(v, str):
            file = open(v, "rb")
            name = v
        else:
            file = v
            name = v.name

        if not isinstance(file, io.IOBase):
            raise ValueError("This needs to be a instance of a file")

        return cls(file, name=name)

    def __repr__(self) -> str:
        """Return a string representation of the BigFileLike."""
        return f"BigFileLike({self.value})"

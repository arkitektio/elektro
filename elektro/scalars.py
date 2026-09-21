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
from collections.abc import Iterable, Mapping
from pathlib import Path


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

ArrayCoercible = xr.DataArray | np.ndarray | list | tuple


def is_unlabeled(array: xr.DataArray) -> bool:
    """True when no dimension of the array was named by the caller.

    xarray calls the dimensions of a bare array ``dim_0``, ``dim_1``, ...; those
    names state nothing, so they are neither written into the store nor checked
    against declared axes.
    """
    return all(str(dim) == f"dim_{index}" for index, dim in enumerate(array.dims))


def coerce_to_labeled_array(v: Any) -> xr.DataArray:
    """Coerce array-like input into an ``xr.DataArray``, keeping its dimensions verbatim.

    Nothing is added, removed, renamed or transposed. A bare numpy/dask array
    (or a list) carries no labels and keeps xarray's placeholder names; the
    input it is part of names them from its declared ``axes`` (see
    ``elektro.traits.DeclaresAxesTrait``), or the server does. Dask chunks are
    preserved so the upload path can stream the array to zarr.
    """
    if isinstance(v, (list, tuple)):
        v = np.asarray(v)

    if isinstance(v, np.ndarray) or is_dask_array(v):
        v = xr.DataArray(v)

    if not isinstance(v, xr.DataArray):
        raise ValueError(
            f"Unsupported type {type(v)} for ArrayLike. Supported types are "
            "xr.DataArray, numpy.ndarray, dask.array.Array and (nested) lists"
        )

    if v.ndim == 0:
        raise ValueError("An array dataset needs at least one dimension, got a scalar")

    return v


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


class ArrayLike:
    """The array of an array dataset: any labelled or bare array, of any rank.

    An analog signal is one ``(t, c)`` dataset, a waveform set ``(spike, c, t)``,
    so nothing here restricts the rank or names a dimension. The wrapped value
    is always an ``xr.DataArray``; a bare array keeps placeholder dimension
    names until the input it belongs to declares its ``axes``."""

    def __init__(self, value: xr.DataArray) -> None:
        """Initialize the trace with the wrapped xr.DataArray value."""
        self.value = value
        self.key = str(uuid.uuid4())

    def __set__(self, instance: Any, value: ArrayCoercible) -> None:
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
    def validate(cls, v: "ArrayCoercible | ArrayLike") -> "ArrayLike":
        """Validate the input array and convert it to a xr.DataArray."""
        if isinstance(v, ArrayLike):
            return v
        return cls(coerce_to_labeled_array(v))

    def __repr__(self) -> str:
        """Return a string representation of the ArrayLike."""
        return f"ArrayLike({self.value})"


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
    """A table to upload as parquet: a dict of columns, a DataFrame, a parquet file, or arrow.

    Vendored from mikro. Five things count as parquet-like, and the difference matters at
    upload time rather than here (see :func:`elektro.io.upload._parquet_payload`):

    - a ``dict`` of ``{column: values}`` -- turned into a ``pyarrow.Table`` here. The shortest
      way to say a small table (an event list, a units table) without a temporary file;
    - a ``pandas.DataFrame`` -- serialized in memory;
    - a ``str``/``Path`` naming a parquet file already on disk -- streamed, never read in;
    - a ``pyarrow.Table`` -- serialized without the pandas round trip;
    - a ``pyarrow.RecordBatchReader`` -- written batch by batch, then streamed.
    """

    def __init__(self, value: "ParquetCoercible") -> None:
        """Initialize the ParquetLike scalar with a DataFrame, path or arrow object."""
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
        if isinstance(v, ParquetLike):
            return v

        if isinstance(v, (str, Path)):
            path = Path(v)
            # Checked here rather than at upload: a typo'd path should fail while the
            # caller still knows which table it meant.
            if not path.is_file():
                raise ValueError(f"No parquet file at {path}")
            return cls(path)

        if isinstance(v, Mapping):
            import pyarrow as pa  # type: ignore

            try:
                return cls(pa.table(dict(v)))
            except Exception as error:
                raise ValueError(
                    "A dict of columns becomes a pyarrow Table, and this one could not: "
                    f"{error}. Every value has to be a column of the same length -- a numpy "
                    "array, a list, or a pyarrow array."
                ) from error

        try:
            import pyarrow as pa  # type: ignore
        except ImportError:
            pa = None
        if pa is not None and isinstance(v, (pa.Table, pa.RecordBatchReader)):
            return cls(v)

        if not isinstance(v, pd.DataFrame):
            raise ValueError(
                "This needs to be a dict of columns, a pandas DataFrame, a path to a parquet "
                "file, or a pyarrow Table/RecordBatchReader"
            )

        return cls(v)

    def __repr__(self) -> str:
        """Return a string representation of the ParquetLike."""
        return f"ParquetLike({self.value})"


def _sporadik() -> Any:  # noqa: ANN401 - the module object
    """The sparse wire format, or the reason it is missing.

    An extra rather than a dependency: a client that never uploads a sparse dataset should not
    carry the format, so the failure names the extra instead of reading like a broken install.
    """
    try:
        import sporadik
    except ModuleNotFoundError as missing:  # pragma: no cover - depends on the environment
        raise ModuleNotFoundError(
            "A sparse dataset is written in the `sporadik` wire format, which is an optional "
            "extra here: pip install 'elektro[sparse]'."
        ) from missing
    return sporadik


class SporadikLike:
    """A **sparse matrix** -- a spike raster -- uploaded as one prefix holding one or more layouts.

    Vendored from mikro. The value is anything carrying ``.data``, ``.indices``, ``.indptr``,
    ``.shape`` and ``.format`` (a ``scipy.sparse`` CSR or CSC matrix), a list of them, or
    ``sporadik.Layout`` objects. The server reads the encoding, the shape and the chunking back
    off the artifact, which is why ``createSparseDataset`` declares none of them.

    **Which layouts you hand over is a decision.** Over a ``(unit, t)`` raster, ``.tocsr()``
    makes one *unit's* spike train contiguous and ``.tocsc()`` one *instant* across all units.
    Pass ``[raster.tocsr(), raster.tocsc()]`` for both: one upload, one store, two capabilities.

    Validated here rather than only server-side, because the server's check comes after the
    bytes have moved.
    """

    def __init__(self, value: Any, layouts: dict[int, Any] | None = None) -> None:  # noqa: ANN401
        """Wrap the matrix; ``layouts`` is keyed by the axis each layout makes contiguous."""
        self.value = value
        self.layouts = layouts if layouts is not None else _sporadik().layouts_of(value)
        self.key = str(uuid.uuid4())

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """Get the pydantic core schema for the validator function."""
        return core_schema.no_info_after_validator_function(cls.validate, handler(object))

    @classmethod
    def validate(cls, v: Any) -> "SporadikLike":  # noqa: ANN401
        """Accept CSR/CSC matrices (or layouts), and refuse what cannot be written as a store."""
        if isinstance(v, SporadikLike):
            return v

        sporadik = _sporadik()
        layouts = sporadik.layouts_of(v)
        for layout in layouts.values():
            sporadik.validate_layout(
                data=layout.data,
                indices=layout.indices,
                indptr=layout.indptr,
                shape=layout.shape,
                indexed_axis=layout.indexed_axis,
            )
        return cls(v, layouts)

    def __repr__(self) -> str:
        """Return a string representation of the SporadikLike scalar."""
        shape = next(iter(self.layouts.values())).shape if self.layouts else "?"
        axes = "+".join(f"axis{axis}" for axis in sorted(self.layouts))
        return f"SporadikLike({axes}, shape={shape})"


ParquetCoercible = Any
"""What :class:`ParquetLike` accepts: a dict of columns, a DataFrame, a parquet path, or arrow."""

SporadikCoercible = Any
"""What :class:`SporadikLike` accepts: a scipy.sparse CSR/CSC matrix, a list of them, or layouts."""


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

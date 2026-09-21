"""
Traits for elektro

Traits are mixins that are added to every graphql type that exists on the mikro schema.
We use them to add functionality to the graphql types that extend from the base type.

Every GraphQL Model on Mikro gets a identifier and shrinking methods to ensure the compatibliity
with arkitekt. This is done by adding the identifier and the shrinking methods to the graphql type.
If you want to add your own traits to the graphql type, you can do so by adding them in the graphql
.config.yaml file.

"""

from collections import deque
from collections.abc import Sequence
from enum import Enum
from typing import Awaitable, ClassVar, List, NamedTuple, Self, Union
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from pydantic import BaseModel, model_validator
import xarray as xr
from typing import TYPE_CHECKING
from dask.array import from_zarr  # type: ignore
from typing import Any
from rath.origin import ContextBound
from rath.scalars import IDCoercible
from rath.traits import FederationFetchable
from rath.turms.utils import get_attributes_or_error

from .client import client_of
from .scalars import is_unlabeled
from .vocabulary import (
    MATRIX_KINDS,
    AxisSelection,
    ResolvedTransformKind,
    default_axis_type,
    normalize_selection,
)

#: A point or a stack of them: a (N,) vector, a (K, N) array, or anything
#: `np.asarray` turns into one.
PointsLike = Union[Sequence[float], Sequence[Sequence[float]], NDArray[np.generic]]


if TYPE_CHECKING:
    from elektro.elektro import Elektro
    from elektro.api.schema import (
        Compartment,
        Section,
        SectionParamMap,
        Ion,
        SectionInput,
        ModelConfigInput,
        CellInput,
        CompartmentInput,
        SectionParamMapInput,
        Axis,
        GetCoordinateGraphQueryCoordinateGraph,
        Lens,
        PlacementValidity,
        TransformInput,
    )
    from elektro.rath import ElektroRath
    from elektro.io.obstore import ParquetDatasetViaObstore
    from zarr.storage import StorePath
    from duckdb import DuckDBPyRelation


class ModelConfigTrait(BaseModel):
    """Mixin for ModelConfig data."""

    def as_input(self) -> "ModelConfigInput":
        """Convert the model to a ModelConfigInput"""
        from elektro.api.schema import ModelConfigInput

        return ModelConfigInput(
            **self.model_dump(exclude={"id", "created_at", "updated_at"}),
        )


class SectionInputTrait(BaseModel):
    """Mixin for SectionInput data."""

    pass


class CompartmentInputTrait(BaseModel):
    """Mixin for CompartmentInput data."""

    def get_section_param_for_id(self, id: str) -> "SectionParamMapInput":
        """Return the section param mapping matching the given param id."""
        sections = get_attributes_or_error(self, "section_params")
        x = next((section for section in sections if section.param == id), None)
        if x is None:
            raise ValueError(
                f"SectionParam with id {id} not found available are: {','.join(map(lambda x: x.param, sections))}"
            )
        return x


class BiophysicsInputTrait(BaseModel):
    """Mixin for Biophysics data"""

    def get_compartment_for_id(self, id: str) -> "CompartmentInput":
        """Return the compartment input matching the given id."""
        sections = get_attributes_or_error(self, "compartments")
        x = next((section for section in sections if section.id == id), None)
        if x is None:
            raise ValueError(f"Compartment with id {id} not found")
        return x


class TopologyInputTrait(BaseModel):
    """Mixin for Topology data"""

    def get_section_for_id(self, id: str) -> "SectionInput":
        """Return the section input matching the given id."""
        sections = get_attributes_or_error(self, "sections")
        x = next((section for section in sections if section.id == id), None)
        if x is None:
            raise ValueError(f"Section with id {id} not found")
        return x

    @property
    def section_ids(self) -> List[str]:
        """The ids of all sections in the topology."""
        sections = get_attributes_or_error(self, "sections")
        return [section.id for section in sections]


class ModelConfigInputTrait(BaseModel):
    """Mixin for Topology data"""

    def get_cell_for_id(self, id: str) -> "CellInput":
        """Return the cell input matching the given id."""
        sections = get_attributes_or_error(self, "cells")
        x = next((section for section in sections if section.id == id), None)
        if x is None:
            raise ValueError(f"Cell with id {id} not found")
        return x

    @property
    def cell_ids(self) -> List[str]:
        """The ids of all cells in the model config."""
        sections = get_attributes_or_error(self, "cells")
        return [section.id for section in sections]


class BiophysicsTrait:
    """Mixin for Biophysics data"""

    def compartment_for_id(self, id: str) -> "Compartment":
        """Return the compartment matching the given id."""
        compartments = get_attributes_or_error(self, "compartments")
        x = next((compartment for compartment in compartments if compartment.id == id), None)
        if x is None:
            raise ValueError(f"Compartment with id {id} not found")
        return x

    @property
    def compartment_ids(self) -> List[str]:
        """The ids of all compartments in the biophysics data."""
        compartments = get_attributes_or_error(self, "compartments")
        return [compartment.id for compartment in compartments]

    def as_dataframe(self) -> pd.DataFrame:
        """Convert the biophysics data to a pandas DataFrame"""
        from elektro.api.schema import Compartment

        compartments: list[Compartment] = get_attributes_or_error(self, "compartments")

        records = []

        for compartment in compartments:
            data = {
                "id": compartment.id,
                "mechanisms": " ".join(([mechanism for mechanism in compartment.mechanisms])),
                **{param.param: param.distribution.value for param in compartment.section_params},
                **{
                    f"e{ion.ion}": ion.reversal_potential
                    for ion in compartment.ions
                    if ion.reversal_potential is not None
                },
            }

            records.append(data)

        return pd.DataFrame.from_records(records)


class TopologyTrait:
    """Mixin for Biophysics data"""

    def section_for_id(self, id: str) -> "Section":
        """Return the section matching the given id."""
        sections = get_attributes_or_error(self, "sections")
        x = next((sec for sec in sections if sec.id == id), None)
        if x is None:
            raise ValueError(f"Compartment with id {id} not found")
        return x

    @property
    def section_ids(self) -> List[str]:
        """The ids of all sections in the topology."""
        compartments = get_attributes_or_error(self, "sections")
        return [compartment.id for compartment in compartments]

    def as_dataframe(self) -> pd.DataFrame:
        """Convert the biophysics data to a pandas DataFrame"""
        from elektro.api.schema import Section

        compartments: list[Section] = get_attributes_or_error(self, "sections")

        records = []

        for sec in compartments:
            data = {
                "id": sec.id,
                "length": sec.length,
                "diameter": sec.diam,
                "category": sec.category,
                "n_segments": sec.nseg,
                "connections": ", ".join(
                    [f"{conn.parent}({conn.location})" for conn in sec.connections]
                ),
            }

            records.append(data)

        return pd.DataFrame.from_records(records)


class CompartmentTrait:
    """Mixin for Biophysics data"""

    def section_param_for_id(self, id: str) -> "SectionParamMap":
        """Return the section param mapping matching the given param id."""
        compartments = get_attributes_or_error(self, "section_params")
        x = next(
            (compartment for compartment in compartments if compartment.param == id),
            None,
        )
        if x is None:
            raise ValueError(f"SectionParam with id {id} not found")
        return x

    def ion_for_id(self, id: str) -> "Ion":
        """Return the ion setting matching the given ion species name (e.g. 'na')."""
        ions = get_attributes_or_error(self, "ions")
        x = next((ion for ion in ions if ion.ion == id), None)
        if x is None:
            raise ValueError(f"Ion with name {id} not found")
        return x


class ExperimentTrait(ContextBound):
    """Mixin for Experiment data."""

    def layers_of_kind(self, kind: str) -> list[Any]:  # noqa: ANN401
        """The experiment's layers of one kind (``"TRACE"``, ``"SPIKES"``, ``"EVENTS"``, ``"ANNOTATION"``)."""
        layers = get_attributes_or_error(self, "layers")
        return [layer for layer in layers if str(getattr(layer.kind, "value", layer.kind)) == kind]

    @property
    def data(self) -> xr.Dataset:
        """The experiment's TRACE layers as an xarray Dataset with one ``traces`` variable.

        ``traces`` is ``(trace, time)``: one row per trace layer (per channel, for a
        multi-channel lens whose layer names no ``channelIndex``), labelled by the layer's
        name, on a ``time`` coordinate in the unit of the experiment's world. Every layer is
        read through its lens and timed by composing the path from the lens' space into the
        world, so layers over different clocks and offsets line up; where one has no sample
        the row is NaN. Hidden layers are included; ``visible`` is view state.

        Composing needs every edge on the path to state numbers. A layer timed by a lookup
        (a variable-step run) raises, naming the missing path.
        """
        client = client_of(self)
        world: CoordinateSystemTrait = get_attributes_or_error(self, "world")
        graph = world.graph()

        def rows(layer: Any) -> list[xr.DataArray]:  # noqa: ANN401
            # The layer fragment carries the lens' id only (a named fragment spread inside
            # the interface fragment breaks the generated module), so the lens is fetched.
            lens = client.get_lens(layer.lens.id)
            samples = lens.data
            time_axis = lens.time_axis
            space: CoordinateSystemTrait = get_attributes_or_error(lens, "coordinate_system")
            times = space.axis_values_in(world, time_axis, samples.sizes[time_axis], graph=graph)
            samples = samples.rename({time_axis: "time"}).assign_coords(time=times)
            label = layer.name or f"layer {layer.id}"

            others = [dim for dim in samples.dims if dim != "time"]
            if layer.channel_index is not None and others:
                samples = samples.isel({others[0]: layer.channel_index})
                others = others[1:]
            if not others:
                return [samples.expand_dims(trace=[label])]
            flat = samples.stack(trace=others).transpose("trace", "time")
            names = [f"{label}[{', '.join(f'{d}={int(v)}' for d, v in zip(others, key if isinstance(key, tuple) else (key,)))}]" for key in flat.indexes["trace"]]
            return [flat.drop_vars([*others, "trace"]).assign_coords(trace=names)]

        layers = self.layers_of_kind("TRACE")
        if layers:
            traces = xr.concat(
                [row for layer in layers for row in rows(layer)], dim="trace", join="outer"
            )
        else:
            traces = xr.DataArray(
                np.zeros((0, 0)),
                dims=["trace", "time"],
                coords={"trace": np.array([], dtype=object), "time": np.array([], dtype=float)},
            )

        dataset = xr.Dataset({"traces": traces})
        # The numbers are in the world's unit, whatever the datasets' clocks count in.
        unit = world.units[world.time_axis]
        if unit is not None:
            dataset["time"].attrs["units"] = str(unit)
        return dataset


class TableDatasetTrait(ContextBound):
    """A table dataset's rows, read lazily through DuckDB."""

    @property
    def data(self) -> "DuckDBPyRelation":
        """The table as a lazy DuckDB relation over its parquet object on S3.

        Filter/aggregate on the relation and call ``.df()`` to materialise the result.
        """
        store: HasParquetStoreAccesor = get_attributes_or_error(self, "store")
        return store.duckdb_relation


class CreateTableDatasetTrait(BaseModel):
    """Resolves `columns` against the frame, and checks the whole declaration against it.

    Vendored from mikro. A table declares every column of its Parquet, in the file's order,
    with the DuckDB type name the server reads back off it. Every part of that is a fact
    about the file, so the complete list is derived here from the value's Arrow schema and
    what the caller passes in `columns` is merged onto it: a subset, in any order, with
    `dtype` omitted. See :mod:`elektro.tables`.
    """

    @model_validator(mode="after")
    def _resolve_columns(self) -> Self:
        """Derive the declaration, merge the caller's onto it, and refuse what cannot describe this frame."""
        from elektro.tables import TableDeclarationError, file_columns_of, resolve_columns

        data = getattr(self, "data", None)
        if data is None:
            return self
        value = getattr(data, "value", data)

        try:
            file_columns = file_columns_of(value)
        except TableDeclarationError:
            raise
        except Exception:
            # An object this cannot read: the server still checks.
            return self

        # A list, as the field is declared: a tuple set past validation serialises with a warning.
        columns = list(resolve_columns(file_columns, self.columns or ()))
        object.__setattr__(self, "columns", columns)
        # `object.__setattr__` does not touch `fields_set`, and the client's dump with
        # `exclude_unset=True` -- without this the resolved list would be dropped.
        self.__pydantic_fields_set__.add("columns")
        return self


class CreateSparseDatasetTrait(BaseModel):
    """Checks a sparse dataset's declaration against its matrix, before the matrix moves.

    See :mod:`elektro.sparse`: the axis rules (INDEX or one TIME, TIME unidentified, INDEX
    identified) and the one check only this side can make first, the rank against the matrix.
    """

    @model_validator(mode="after")
    def _check_declaration(self) -> Self:
        """Check the axes, then check them against the matrix if one is in hand."""
        from elektro.sparse import check_against_store, check_axes

        axes = getattr(self, "axes", None) or ()
        check_axes(axes)
        layouts = getattr(getattr(self, "store", None), "layouts", None)
        if layouts:
            check_against_store(axes, layouts)
        return self


def _space_id(value: Any) -> Any:  # noqa: ANN401
    """The coordinate system an object means when it is passed where a space is wanted.

    A timing edge runs between *spaces*, and every data object carries an id of its own that is
    also a valid-looking space id -- so passing ``trace`` (or ``trace.id``) where its grid was
    meant is accepted by the server and times whichever grid shares that integer. Objects are
    resolved here; a bare id cannot be, and is passed through.
    """
    for attribute in ("intrinsic_system", "coordinate_system", "clock", "world"):
        space = getattr(value, attribute, None)
        if space is not None and getattr(space, "id", None) is not None:
            return space.id
    return value


class ResolvesSpacesTrait(BaseModel):
    """Maps a dataset, table, raster, clock or experiment to its space on a timing edge.

    ``create_sampling_law(source=trace, clock=experiment, ...)`` then means the trace's sample
    grid and the experiment's world, instead of the two objects' own ids.
    """

    @model_validator(mode="before")
    @classmethod
    def _resolve_spaces(cls, value: Any) -> Any:  # noqa: ANN401
        if not isinstance(value, dict):
            return value
        return {
            key: _space_id(item) if key in ("source", "clock", "onto") else item
            for key, item in value.items()
        }


class SparseAxisInputTrait(BaseModel):
    """Refuses a single identification where the field takes a list.

    ``identifiedBy`` is a list (an axis may be keyed by more than one source), and a bare
    ``TableIdentifiesInput`` otherwise fails as a baffling ``('kind', 'TABLE')`` pydantic
    error. An *empty* list is not refused here: a TIME axis is exactly the one that has none.
    """

    @model_validator(mode="before")
    @classmethod
    def _check_identifications(cls, value: Any) -> Any:  # noqa: ANN401
        if not isinstance(value, dict):
            return value
        for key in ("identified_by", "identifiedBy"):
            entries = value.get(key)
            if isinstance(entries, BaseModel):
                raise ValueError(
                    f"`{key}` is a list, because an axis can be keyed by more than one source. "
                    f"Write {key}=[{type(entries).__name__}(...)]."
                )
        return value


def _labeled(array: Any, axis_names: Sequence[str] | None) -> xr.DataArray:  # noqa: ANN401
    """Wrap a zarr-backed array with the axis names the server states for it."""
    if axis_names is not None and len(axis_names) == array.ndim:
        return xr.DataArray(array, dims=list(axis_names))
    return xr.DataArray(array)


class DataArrayTrait(ContextBound):
    """One pyramid level of an array dataset: the store lives here, not on the dataset."""

    @property
    def data(self) -> xr.DataArray:
        """This level as a (dask-backed) xr.DataArray, its dimensions named.

        A level names its dimensions from *its own* coordinate system, not the
        dataset's: a coarsened level is a different grid, and only its axes are
        guaranteed to describe its shape.
        """
        store = get_attributes_or_error(self, "store")
        system = getattr(self, "coordinate_system", None)
        names = _axis_names_in_order(system) if getattr(system, "axes", None) else None
        return _labeled(from_zarr(store.zarr_store), names)


class DatasetTrait(ContextBound):
    """An array dataset: its pyramid levels, and the lenses cut from them.

    The store belongs to a `DataArray` (a level), never to the dataset — so
    ``.data`` is level 0, and the coarser levels are reached by name.
    """

    def level_data(self, level: int = 0) -> xr.DataArray:
        """One pyramid level of this dataset, with its axes named.

        Level 0 is the full-resolution array; higher levels are coarser.
        """
        arrays = get_attributes_or_error(self, "data_arrays")
        dims = get_attributes_or_error(self, "axis_names")
        for array in arrays:
            if array.level == level:
                return _labeled(from_zarr(array.store.zarr_store), dims)
        raise ValueError(
            f"This dataset has no pyramid level {level}. Available levels: "
            f"{sorted(a.level for a in arrays)}"
        )

    def multi_scale_data(self) -> List[xr.DataArray]:
        """Every pyramid level of this dataset, finest first."""
        arrays = get_attributes_or_error(self, "data_arrays")
        dims = get_attributes_or_error(self, "axis_names")
        return [
            _labeled(from_zarr(array.store.zarr_store), dims)
            for array in sorted(arrays, key=lambda a: a.level)
        ]

    @property
    def data(self) -> xr.DataArray:
        """The full-resolution data of this dataset as a (dask-backed) xr.DataArray."""
        return self.level_data(0)

    def lens(self, elektro: "Elektro | None" = None, **selections: AxisSelection) -> "Lens":
        """Create a lens on this dataset from pythonic per-axis selections.

        With no selections the lens frames the whole dataset. Each keyword names
        an axis and selects along it, in sample indices: an ``int`` pins one
        index, a ``(start, stop[, step])`` tuple or a ``slice()`` selects a range.

        ``signal.dataset.lens(t=(0, 30_000), c=2)`` is the first 30k samples of channel 2.
        The lens is created through ``elektro`` if given, else through the client
        that fetched this dataset.
        """
        from elektro.api.schema import SliceInput

        axis_names = getattr(self, "axis_names", None)
        slices: list[SliceInput] = []
        for axis, selection in selections.items():
            if axis_names is not None and axis not in axis_names:
                raise ValueError(f"Invalid axis {axis!r} for dataset with axes {list(axis_names)}")
            start, stop, step = normalize_selection(axis, selection)
            slices.append(SliceInput(axis=axis, start=start, stop=stop, step=step))

        return client_of(self, elektro).create_lens(
            dataset=get_attributes_or_error(self, "id"), slices=slices
        )


class Lensable:
    """An immutable selection over a trace."""

    @property
    def data(self) -> xr.DataArray:
        """The selected part of the trace, as a (dask-backed) xr.DataArray."""
        dataset: DatasetTrait = get_attributes_or_error(self, "dataset")
        slices = get_attributes_or_error(self, "slices")

        data = dataset.data

        for lens_slice in slices:
            if lens_slice.axis not in data.dims:
                raise ValueError(
                    f"Invalid slice dimension {lens_slice.axis} for data with dimensions {data.dims}"
                )
            if lens_slice.start is None and lens_slice.stop is None and lens_slice.step is None:
                continue

            data = data.isel(
                {lens_slice.axis: slice(lens_slice.start, lens_slice.stop, lens_slice.step)}
            )

        return data

    @property
    def time_axis(self) -> str:
        """The name of the lens' one TIME axis."""
        system: CoordinateSystemTrait = get_attributes_or_error(self, "coordinate_system")
        return system.time_axis


class ElektroFetchable(ContextBound, FederationFetchable):
    """A trait for objects that can be fetched from the elektro service by ID.

    Fetched through a client (``Type.aexpand(id, client)``), an object remembers
    it, and what it fetches later goes through that same client.
    """

    @classmethod
    def fetch_origin(cls, client: "Elektro") -> dict:
        """Bind what is fetched by id to its client, as any other result is.

        Without it an object expanded through ``_entities`` would have its rath
        but no datalayer to read its data with, and no client to make its
        follow-up calls through.
        """
        return client._origin()


class AxisInputTrait(BaseModel):
    """Lets a structural axis be given as a bare name.

    ``axes=["t", "c"]`` is enough for the common case: the axis type is
    inferred from the name (see ``elektro.vocabulary.default_axis_type``). Pass
    a full ``AxisInput`` for anything the convention does not cover.
    """

    @model_validator(mode="before")
    @classmethod
    def _coerce_bare_name(cls, value: Any) -> Any:  # noqa: ANN401
        if isinstance(value, str):
            return {"name": value, "type": default_axis_type(value)}
        return value


class DeclaresAxesTrait(BaseModel):
    """Checks an input's arrays against the axes declared for them, before upload.

    The server refuses a rank mismatch and a store whose dimension names disagree
    with the declaration — but only after the array was uploaded, and an array
    dataset is the expensive thing to upload twice. A bare array has no names to
    disagree with, so it takes the declared ones.

    ``axes`` is required on `CreateArrayDatasetInput`, so there is no rank-1
    default to fall back on here; the refusal is for the declaration that is
    present and wrong.
    """

    @model_validator(mode="after")
    def _axes_describe_the_arrays(self) -> Self:
        axes = getattr(self, "axes", None)
        if not axes:
            return self
        declared = [axis.name for axis in axes]

        # Every level answers to the same axis names: a pyramid coarsens extents,
        # never the meaning of a dimension.
        levels: list[tuple[str, Any]] = [("data", getattr(self, "data", None))]
        for scale in getattr(self, "scales", ()) or ():
            levels.append(
                (f"scales[level={getattr(scale, 'level', '?')}]", getattr(scale, "array", None))
            )

        for name, wrapped in levels:
            array = getattr(wrapped, "value", None)
            if not isinstance(array, xr.DataArray):
                continue

            if len(declared) != array.ndim:
                raise ValueError(
                    f"`{name}` has {array.ndim} dimensions but `axes` declares "
                    f"{len(declared)} ({', '.join(declared)}). Every dimension needs an axis: "
                    f"an axis is what gives a dimension a type, and the type is what decides "
                    f"how it is sampled, windowed and composed."
                )

            if is_unlabeled(array):
                setattr(wrapped, "value", array.rename(dict(zip(array.dims, declared))))
                continue

            dims = [str(dim) for dim in array.dims]
            disagree = [
                (index, dim, declared[index])
                for index, dim in enumerate(dims)
                if dim != f"dim_{index}" and dim != declared[index]
            ]
            if disagree:
                detail = "; ".join(
                    f"dimension {index} is {dim!r} and was declared {given!r}"
                    for index, dim, given in disagree
                )
                raise ValueError(
                    f"`axes` does not describe `{name}`: {detail}. The array's dimensions are "
                    f"{dims} and the declaration reads {declared}. Reorder the axes to match "
                    f"the array (or transpose the array): a transposed declaration applies a "
                    f"sampling law along the wrong dimension instead of raising."
                )
        return self


def _normalize_kind(kind: "ResolvedTransformKind | Enum") -> ResolvedTransformKind:
    """Normalize a transformation kind to its plain string value."""
    return str(getattr(kind, "value", kind))  # type: ignore[return-value]


def _axis_names_in_order(system: Any) -> list[str]:  # noqa: ANN401
    """The axis names of a coordinate system, ordered by their `order` field."""
    axes = get_attributes_or_error(system, "axes")
    return [a.name for a in sorted(axes, key=lambda a: a.order)]


def _homogeneous_from_rows(rows: Any, ndim_in: int | None) -> NDArray[np.float64]:  # noqa: ANN401
    """Turn an M x (N+1) affine (last column translation) into a homogeneous
    (M+1) x (N+1) matrix. An M x N matrix given without a translation column
    gets a zero one appended first."""
    rows = np.asarray(rows, dtype=float)
    if rows.ndim != 2:
        raise ValueError(f"Expected a 2D affine matrix, got shape {rows.shape}")
    m, cols = rows.shape
    if ndim_in is not None and cols == ndim_in:
        rows = np.hstack([rows, np.zeros((m, 1))])
    n = rows.shape[1] - 1
    bottom = np.zeros((1, n + 1))
    bottom[0, n] = 1.0
    return np.vstack([rows, bottom])


def _apply_homogeneous(matrix: NDArray[np.float64], points: PointsLike) -> NDArray[np.float64]:
    """Apply a homogeneous (M+1) x (N+1) matrix to an (K, N) or (N,) point array."""
    pts = np.atleast_2d(np.asarray(points, dtype=float))
    n = matrix.shape[1] - 1
    if pts.shape[1] != n:
        raise ValueError(
            f"Points have dimension {pts.shape[1]}, but the transformation expects {n}"
        )
    out = (matrix @ np.hstack([pts, np.ones((len(pts), 1))]).T).T[:, :-1]
    return out[0] if np.ndim(points) == 1 else out


def _parameter_matrix(edge: Any, ndim: int | None) -> NDArray[np.float64]:  # noqa: ANN401
    """The matrix of an edge that states its numbers, over `ndim` axes."""
    kind = _normalize_kind(get_attributes_or_error(edge, "kind"))

    if kind == "IDENTITY":
        if ndim is None:
            raise ValueError(
                "Cannot determine the dimensionality of an IDENTITY transformation: neither "
                "its axes nor its input coordinate system were selected in the query"
            )
        return np.eye(ndim + 1)
    if kind == "SCALE":
        scale = get_attributes_or_error(edge, "scale")
        return np.diag([float(s) for s in scale] + [1.0])
    if kind == "TRANSLATION":
        translation = get_attributes_or_error(edge, "translation")
        n = len(translation)
        matrix = np.eye(n + 1)
        matrix[:n, n] = [float(t) for t in translation]
        return matrix
    if kind in ("AFFINE", "ROTATION"):
        return _homogeneous_from_rows(get_attributes_or_error(edge, "affine"), ndim)
    raise NotImplementedError(f"Transformations of kind {kind} state no matrix of their own")


class PathStep(NamedTuple):
    """One edge of a composable path between coordinate systems.

    `inverted` is True when the edge is traversed output-to-input, in which
    case its matrix must be inverted before composing.
    """

    transformation: "TransformationTrait"
    inverted: bool


class TransformationTrait:
    """A trait for transformation edges between coordinate systems.

    Turns the per-kind parameters into homogeneous numpy matrices and applies
    them to points. The matrix maps points given in the *input* system's axis
    order to points in the *output* system's axis order.

    The edge this service writes most is the **sampling law**: one
    BY_DIMENSION edge from a sample grid ``(t, c)`` to a clock ``(t)``, naming
    ``t`` and carrying a 1x2 affine over it. Its matrix is therefore ``2 x 3`` (plus the
    homogeneous row): it says nothing about ``c``, so it has no inverse unless
    the grid is ``(t)`` alone. A FIELD edge (a time lookup) states no numbers
    and has no matrix at all.
    """

    #: The kinds that state their numbers on the edge itself.
    MATRIX_KINDS: ClassVar[frozenset[ResolvedTransformKind]] = MATRIX_KINDS
    #: The kinds a path may be composed through without fetching anything.
    COMPOSABLE_KINDS: ClassVar[frozenset[ResolvedTransformKind]] = frozenset(
        {*MATRIX_KINDS, "BY_DIMENSION"}
    )

    def _system_axes(self, side: str) -> list[str] | None:
        system = getattr(self, side, None)
        axes = getattr(system, "axes", None) if system is not None else None
        return _axis_names_in_order(system) if axes is not None else None

    def ndim_in(self) -> int | None:
        """Number of input axes, if the input system was selected in the query."""
        names = self._system_axes("input")
        return len(names) if names is not None else None

    def ndim_out(self) -> int | None:
        """Number of output axes, if the output system was selected in the query."""
        names = self._system_axes("output")
        return len(names) if names is not None else None

    def as_matrix(self) -> NDArray[np.float64]:
        """This transformation as a homogeneous (M+1) x (N+1) numpy matrix.

        IDENTITY, SCALE, TRANSLATION, AFFINE, ROTATION, MAP_AXIS and
        BY_DIMENSION have one. FIELD, SEQUENCE and UNMAPPABLE do not.
        """
        kind = _normalize_kind(get_attributes_or_error(self, "kind"))

        if kind in ("IDENTITY", "SCALE", "TRANSLATION", "AFFINE", "ROTATION"):
            return _parameter_matrix(self, self.ndim_in() or self.ndim_out())

        if kind in ("MAP_AXIS", "BY_DIMENSION"):
            in_names, out_names = self._system_axes("input"), self._system_axes("output")
            if in_names is None or out_names is None:
                raise ValueError(
                    f"Building a {kind} matrix requires the input and output coordinate "
                    f"systems (with axes) to be selected in the query"
                )
            matrix = np.zeros((len(out_names) + 1, len(in_names) + 1))
            matrix[len(out_names), len(in_names)] = 1.0

            if kind == "MAP_AXIS":
                input_axes, output_axes = get_attributes_or_error(self, "input_axes", "output_axes")
                for in_name, out_name in zip(input_axes, output_axes):
                    matrix[out_names.index(out_name), in_names.index(in_name)] = 1.0
                return matrix

            # The children answer to the axes this edge names, not to their own
            # `inputAxes` (which report the whole system's): they are one map over
            # that subset, written out as steps and applied first to last.
            acts_on_in, acts_on_out = get_attributes_or_error(self, "input_axes", "output_axes")
            block: NDArray[np.float64] | None = None
            for child in get_attributes_or_error(self, "by_dimension_children"):
                step = _parameter_matrix(child, len(acts_on_in))
                block = step if block is None else step @ block
            if block is None:
                block = np.eye(len(acts_on_in) + 1)
            if block.shape != (len(acts_on_out) + 1, len(acts_on_in) + 1):
                raise ValueError(
                    f"BY_DIMENSION transformation {getattr(self, 'id', '?')} names "
                    f"{list(acts_on_in)} -> {list(acts_on_out)} but its parameters map "
                    f"{block.shape[1] - 1} -> {block.shape[0] - 1} axes"
                )
            rows = [out_names.index(name) for name in acts_on_out]
            cols = [in_names.index(name) for name in acts_on_in]
            for r, row in enumerate(rows):
                for c, col in enumerate(cols):
                    matrix[row, col] = block[r, c]
                matrix[row, len(in_names)] = block[r, len(cols)]
            return matrix

        if kind == "FIELD":
            raise NotImplementedError(
                "A FIELD transformation is a lookup: the map is the values of the trace living "
                "in its `field` system (a times trace), so it states no matrix. Read that "
                "trace's data for the times."
            )
        if kind == "UNMAPPABLE":
            raise NotImplementedError(
                "An UNMAPPABLE transformation is a declared non-correspondence between "
                "two coordinate systems; it has no matrix by definition"
            )
        raise NotImplementedError(f"Transformations of kind {kind} have no closed-form matrix")

    def inverse_matrix(self) -> NDArray[np.float64]:
        """The inverse of `as_matrix()`; raises ValueError if not invertible."""
        matrix = self.as_matrix()
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError(
                f"Cannot invert transformation {getattr(self, 'id', '?')}: it maps "
                f"{matrix.shape[1] - 1} -> {matrix.shape[0] - 1} dimensions"
            )
        try:
            return np.linalg.inv(matrix).astype(np.float64)
        except np.linalg.LinAlgError as e:
            kind = _normalize_kind(get_attributes_or_error(self, "kind"))
            raise ValueError(
                f"Transformation {getattr(self, 'id', '?')} ({kind}) is singular "
                f"and cannot be inverted"
            ) from e

    def apply(self, points: PointsLike) -> NDArray[np.float64]:
        """Map points from the input system to the output system."""
        return _apply_homogeneous(self.as_matrix(), points)

    def apply_inverse(self, points: PointsLike) -> NDArray[np.float64]:
        """Map points from the output system back to the input system."""
        return _apply_homogeneous(self.inverse_matrix(), points)


def _bfs_path(transformations: Sequence[object], start_id: str, target_id: str) -> list[PathStep]:
    """Find the shortest composable path between two coordinate systems.

    Edges are walked forward (input -> output) and backward (output -> input,
    flagged inverted). Only kinds with a matrix are walkable; a kind this client
    does not model comes back as a fieldless catch-all carrying no trait.
    """
    adjacency: dict[str, list[tuple[PathStep, str]]] = {}
    for t in transformations:
        if not isinstance(t, TransformationTrait):
            continue
        kind = _normalize_kind(get_attributes_or_error(t, "kind"))
        if kind not in TransformationTrait.COMPOSABLE_KINDS:
            continue
        input_system = getattr(t, "input", None)
        output_system = getattr(t, "output", None)
        if input_system is None or output_system is None:
            continue
        in_id, out_id = str(input_system.id), str(output_system.id)
        adjacency.setdefault(in_id, []).append((PathStep(t, False), out_id))
        adjacency.setdefault(out_id, []).append((PathStep(t, True), in_id))

    if start_id == target_id:
        return []

    queue = deque([start_id])
    predecessor: dict[str, tuple[str, PathStep]] = {}
    visited = {start_id}
    while queue:
        node = queue.popleft()
        for step, neighbor in adjacency.get(node, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            predecessor[neighbor] = (node, step)
            if neighbor == target_id:
                path: list[PathStep] = []
                current = neighbor
                while current != start_id:
                    current, prev_step = predecessor[current]
                    path.append(prev_step)
                return list(reversed(path))
            queue.append(neighbor)

    raise ValueError(
        f"No composable transformation path from coordinate system {start_id} to "
        f"{target_id}. Reachable systems: {sorted(visited)}. A path through a FIELD edge "
        f"(a time lookup) states no numbers and cannot be composed."
    )


def _compose_steps(
    steps: Sequence[PathStep], identity_ndim: int | None = None
) -> NDArray[np.float64]:
    """Compose a path of steps into one homogeneous matrix, applied first-to-last."""
    matrix: NDArray[np.float64] | None = None
    for step in steps:
        t = step.transformation
        step_matrix = t.inverse_matrix() if step.inverted else t.as_matrix()
        if matrix is None:
            matrix = step_matrix
        elif step_matrix.shape[1] != matrix.shape[0]:
            raise ValueError(
                f"Transformation {getattr(t, 'id', '?')} expects "
                f"{step_matrix.shape[1] - 1} dimensions but the path so far "
                f"produces {matrix.shape[0] - 1}"
            )
        else:
            matrix = step_matrix @ matrix
    if matrix is None:
        if identity_ndim is None:
            raise ValueError("Cannot compose an empty path without a dimensionality")
        return np.eye(identity_ndim + 1)
    return matrix


class CoordinateSystemTrait:
    """A space: a sample grid, a clock, a world or a drawing space."""

    @property
    def ndim(self) -> int:
        """The number of axes of this coordinate system."""
        return len(get_attributes_or_error(self, "axes"))

    @property
    def axis_names(self) -> list[str]:
        """The axis names, ordered by their `order` field."""
        return _axis_names_in_order(self)

    @property
    def units(self) -> dict[str, str | None]:
        """A mapping of axis name to its unit (None on a sample grid, which never carries one)."""
        axes = get_attributes_or_error(self, "axes")
        return {a.name: a.unit for a in sorted(axes, key=lambda a: a.order)}

    @property
    def time_axis(self) -> str:
        """The name of this system's one TIME axis."""
        axes = get_attributes_or_error(self, "axes")
        names = [a.name for a in axes if _normalize_kind(a.type) == "TIME"]
        if len(names) != 1:
            raise ValueError(
                f"Coordinate system {get_attributes_or_error(self, 'name')!r} has "
                f"{len(names)} TIME axes ({names}); expected exactly one"
            )
        return names[0]

    def get_axis(self, name: str) -> "Axis":
        """Get an axis by its name or long name."""
        axes = get_attributes_or_error(self, "axes")
        for axis in axes:
            if axis.name == name or getattr(axis, "long_name", None) == name:
                return axis
        raise KeyError(
            f"No axis {name!r} in coordinate system "
            f"{get_attributes_or_error(self, 'name')!r}. "
            f"Available axes: {[a.name for a in axes]}"
        )

    def transform_to(
        self,
        other: "IDCoercible | CoordinateSystemTrait",
        transform: "TransformInput",
        *,
        name: str | None = None,
        validity: "PlacementValidity | None" = None,
        elektro: "Elektro | None" = None,
    ) -> Any:  # noqa: ANN401
        """Create a transformation edge from this system to `other`.

        An edge is a fact, stated once: two edges between the same two spaces
        are rivals a path search chooses between, not a composition.
        """
        from elektro.api.schema import UNSET

        other_id = other if isinstance(other, (str, int)) else get_attributes_or_error(other, "id")
        return client_of(self, elektro).create_transformation(
            input=get_attributes_or_error(self, "id"),
            output=other_id,
            transform=transform,
            name=name if name is not None else UNSET,
            validity=validity if validity is not None else UNSET,
        )

    def graph(
        self, max_depth: int | None = None, elektro: "Elektro | None" = None
    ) -> "GetCoordinateGraphQueryCoordinateGraph":
        """Fetch the coordinate graph reachable from this system."""
        from elektro.api.schema import UNSET

        return client_of(self, elektro).get_coordinate_graph(
            coordinate_system=get_attributes_or_error(self, "id"),
            max_depth=max_depth if max_depth is not None else UNSET,
        )

    def path_to(
        self,
        other: "IDCoercible | CoordinateSystemTrait",
        *,
        max_depth: int | None = None,
        graph: "GetCoordinateGraphQueryCoordinateGraph | None" = None,
        elektro: "Elektro | None" = None,
    ) -> list[PathStep]:
        """The shortest composable path of transformation edges to `other`.

        Fetches the coordinate graph (or uses a pre-fetched `graph`) and walks
        it client-side. Empty when `other` is this system.
        """
        my_id = str(get_attributes_or_error(self, "id"))
        other_id = str(
            other if isinstance(other, (str, int)) else get_attributes_or_error(other, "id")
        )
        if my_id == other_id:
            return []
        if graph is None:
            graph = self.graph(max_depth=max_depth, elektro=elektro)
        return _bfs_path(graph.transformations, my_id, other_id)

    def matrix_to(
        self,
        other: "IDCoercible | CoordinateSystemTrait",
        *,
        max_depth: int | None = None,
        graph: "GetCoordinateGraphQueryCoordinateGraph | None" = None,
        elektro: "Elektro | None" = None,
    ) -> NDArray[np.float64]:
        """The composed homogeneous matrix mapping points of this system into `other`."""
        steps = self.path_to(other, max_depth=max_depth, graph=graph, elektro=elektro)
        return _compose_steps(steps, identity_ndim=self.ndim)

    def transform_points_to(
        self,
        other: "IDCoercible | CoordinateSystemTrait",
        points: PointsLike,
        *,
        max_depth: int | None = None,
        graph: "GetCoordinateGraphQueryCoordinateGraph | None" = None,
        elektro: "Elektro | None" = None,
    ) -> NDArray[np.float64]:
        """Map points given in this system's axis order into `other`."""
        matrix = self.matrix_to(other, max_depth=max_depth, graph=graph, elektro=elektro)
        return _apply_homogeneous(matrix, points)

    def axis_values_in(
        self,
        other: "CoordinateSystemTrait",
        axis: str,
        size: int,
        *,
        graph: "GetCoordinateGraphQueryCoordinateGraph | None" = None,
        elektro: "Elektro | None" = None,
    ) -> NDArray[np.float64]:
        """Where the first `size` indices along `axis` land on `other`'s TIME axis.

        The sample times of a grid on a clock or a world: index ``i`` along
        `axis`, zero along every other axis, read off `other`'s one time axis.
        """
        names = self.axis_names
        points = np.zeros((size, len(names)))
        points[:, names.index(axis)] = np.arange(size)
        mapped = self.transform_points_to(other, points, graph=graph, elektro=elektro)
        return mapped[:, other.axis_names.index(other.time_axis)]


class HasZarrStoreAccessor(ContextBound):
    """Accessor mixin exposing the object's zarr store."""

    _openstore: Any = None

    @property
    def zarr_store(self) -> "StorePath":
        """The opened zarr store of this object, cached after first access."""
        from elektro.io.download import open_zarr_store

        if self._openstore is None:
            id = get_attributes_or_error(self, "id")
            self._openstore = open_zarr_store(id, obj=self)
        return self._openstore


class HasParquetStoreAccesor(ContextBound):
    """Parquet Store Accessor

    Allows reading a ParquetStore object's parquet data either as a pyarrow
    dataset or as a lazy DuckDB relation queried directly on S3.
    """

    _dataset: Any = None
    _duckdb_con: Any = None
    _duckdb_rel: Any = None

    @property
    def parquet_dataset(self) -> "ParquetDatasetViaObstore":
        """The pyarrow Parquet Dataset of the ParquetStore object."""
        from elektro.io.download import open_parquet_filesystem

        if self._dataset is None:
            id = get_attributes_or_error(self, "id")
            self._dataset = open_parquet_filesystem(id, obj=self)
        return self._dataset

    @property
    def duckdb_relation(self) -> "DuckDBPyRelation":
        """A lazy DuckDB relation over the parquet object, queried directly on S3.

        Reads through DuckDB's ``httpfs`` extension so the object is never fully
        downloaded. The backing connection is cached for the lifetime of this
        accessor (the relation is only valid while its connection is alive).
        """
        from elektro.io.download import open_parquet_duckdb

        if self._duckdb_rel is None:
            id = get_attributes_or_error(self, "id")
            self._duckdb_con, self._duckdb_rel = open_parquet_duckdb(id, obj=self)
        return self._duckdb_rel

    @property
    def data(self) -> "DuckDBPyRelation":
        """The data of this table as a lazy DuckDB relation.

        Filter/aggregate on the relation and call ``.df()`` to materialise just
        what a query needs, without downloading the whole parquet object.
        """
        return self.duckdb_relation


class HasDownloadAccessor(ContextBound):
    """Accessor mixin for downloading the object's file by store id."""

    _dataset: Any = None

    def download(self, file_name: str | None = None) -> "str":
        """Download the file and return the local path it was written to."""
        from elektro.io.download import download_file

        store_id, key = get_attributes_or_error(self, "id", "key")
        return download_file(store_id, file_name=file_name or key, obj=self)

    async def adownload(self, file_name: str | None = None) -> Awaitable[str]:
        """Download the file asynchronously and return the local path."""
        from elektro.io.download import adownload_file

        store_id, key = get_attributes_or_error(self, "id", "key")
        return await adownload_file(store_id, file_name=file_name or key, obj=self)


class HasPresignedDownloadAccessor(ContextBound):
    """Accessor mixin for downloading the object via its presigned URL."""

    _dataset: Any = None

    def download(self, file_name: str | None = None) -> str:
        """Download the file from its presigned URL and return the local path."""
        from elektro.io.download import download_presigned_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return download_presigned_file(url, file_name=file_name or key, obj=self)

    async def adownload(self, file_name: str | None = None) -> Awaitable[str]:
        """Download the file from its presigned URL asynchronously."""
        from elektro.io.download import adownload_presigned_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return await adownload_presigned_file(url, file_name=file_name or key, obj=self)

"""Offline tests for the coordinate-system, transformation and axis-declaration traits.

The generated models are built by hand here, the way a query response would
validate into them, so nothing in this module needs a server.
"""

import numpy as np
import pytest
import xarray as xr
from pydantic import ValidationError

from elektro.api.schema import (
    AxisInput,
    AxisType,
    CoordinateSystem,
    ScaleInput,
    ScaleMethod,
    CreateArrayDatasetInput,
    GetCoordinateGraphQuery,
)
from elektro.vocabulary import UnknownAxisName, default_axis_type, normalize_selection


def _system(id: str, axes: list[tuple[str, str, str | None]]) -> dict:
    return {
        "id": id,
        "name": f"system {id}",
        "epoch": None,
        "axes": [
            {
                "id": f"{id}-{order}",
                "order": order,
                "name": name,
                "type": kind,
                "unit": unit,
                "longName": None,
            }
            for order, (name, kind, unit) in enumerate(axes)
        ],
    }


GRID = _system("1", [("t", "TIME", None), ("c", "CHANNEL", None)])
CLOCK = _system("2", [("t", "TIME", "second")])
WORLD = _system("3", [("t", "TIME", "second")])

#: t = sample / 30 kHz + 2 s, stated the way the server states a sampling law.
SAMPLING_LAW = {
    "__typename": "ByDimensionTransformation",
    "id": "10",
    "kind": "BY_DIMENSION",
    "name": "sampling law",
    "version": 1,
    "input": GRID,
    "output": CLOCK,
    "inputAxes": ["t"],
    "outputAxes": ["t"],
    "byDimensionChildren": [
        {
            "__typename": "AffineTransformation",
            "id": "11",
            "kind": "AFFINE",
            # As served: a child reports its parent's *system* axes, not the
            # subset it acts on. The parent's lists are the authoritative ones.
            "inputAxes": ["t", "c"],
            "outputAxes": ["t"],
            "affine": [[1 / 30_000, 2.0]],
        }
    ],
}
OFFSET = {
    "__typename": "TranslationTransformation",
    "id": "12",
    "kind": "TRANSLATION",
    "name": "offset",
    "version": 1,
    "input": CLOCK,
    "output": WORLD,
    "translation": [0.05],
}
LOOKUP = {
    "__typename": "FieldTransformation",
    "id": "13",
    "kind": "FIELD",
    "name": "time lookup",
    "version": 1,
    "input": GRID,
    "output": CLOCK,
    "field": CLOCK,
}


def _graph(*edges: dict) -> object:
    return GetCoordinateGraphQuery.model_validate(
        {
            "coordinateGraph": {
                "root": WORLD,
                "systems": [GRID, CLOCK, WORLD],
                "transformations": list(edges),
            }
        }
    ).coordinate_graph


def test_bare_axis_names_are_coerced() -> None:
    """``axes=["t", "c"]`` reads as TIME and CHANNEL; an unknown name is refused."""
    assert AxisInput.model_validate("t").type == AxisType.TIME
    assert default_axis_type("sweep") == "INDEX"
    with pytest.raises(UnknownAxisName):
        default_axis_type("electrode")


def test_bare_array_takes_the_declared_axis_names() -> None:
    """A bare (t, c) array is named from its axes, so the store and the declaration agree."""
    created = CreateArrayDatasetInput(data=np.zeros((100, 4)), scales=[], name="x", axes=["t", "c"])
    assert created.data.value.dims == ("t", "c")


def test_axes_must_describe_the_array() -> None:
    """Refused before the upload, as the server would refuse it after."""
    with pytest.raises(ValidationError, match="declares 1"):
        CreateArrayDatasetInput(data=np.zeros((100, 4)), scales=[], name="x", axes=["t"])


def test_transposed_declaration_is_refused() -> None:
    """(t, c) data declared (c, t) would apply the sampling law along the channels."""
    data = xr.DataArray(np.zeros((100, 4)), dims=["t", "c"])
    with pytest.raises(ValidationError, match="does not describe"):
        CreateArrayDatasetInput(data=data, scales=[], name="x", axes=["c", "t"])


def test_every_pyramid_level_answers_to_the_same_axes() -> None:
    """A level coarsens extents, never the meaning of a dimension."""
    level0 = xr.DataArray(np.zeros((100, 4)), dims=["t", "c"])
    created = CreateArrayDatasetInput(
        data=level0,
        scales=[ScaleInput(level=1, array=np.zeros((50, 4)), scale_method=ScaleMethod.MAX)],
        name="x",
        axes=["t", "c"],
    )
    # The bare level-1 array is named from the same declaration as level 0.
    assert created.scales[0].array.value.dims == ("t", "c")

    with pytest.raises(ValidationError, match=r"scales\[level=1\]"):
        CreateArrayDatasetInput(
            data=level0,
            scales=[ScaleInput(level=1, array=np.zeros((50, 4, 2)))],
            name="x",
            axes=["t", "c"],
        )


def test_sampling_law_matrix() -> None:
    """The law maps (t, c) onto (t): a rate and a start along t, nothing about c."""
    law = _graph(SAMPLING_LAW).transformations[0]
    matrix = law.as_matrix()
    assert matrix.shape == (2, 3)
    np.testing.assert_allclose(matrix, [[1 / 30_000, 0.0, 2.0], [0.0, 0.0, 1.0]])
    np.testing.assert_allclose(law.apply([30_000, 7]), [3.0])
    with pytest.raises(ValueError, match="maps 2 -> 1"):
        law.inverse_matrix()


def test_sample_times_compose_through_the_chain() -> None:
    """grid -> clock -> world: sample i lands at i / rate + t_start + offset."""
    graph = _graph(SAMPLING_LAW, OFFSET)
    grid = CoordinateSystem.model_validate(GRID)
    world = CoordinateSystem.model_validate(WORLD)

    assert [step.inverted for step in grid.path_to(world, graph=graph)] == [False, False]
    times = grid.axis_values_in(world, "t", 4, graph=graph)
    np.testing.assert_allclose(times, 2.05 + np.arange(4) / 30_000)

    # Walked backwards, the offset inverts; the rank-changing law does not.
    clock = CoordinateSystem.model_validate(CLOCK)
    np.testing.assert_allclose(world.transform_points_to(clock, [1.05], graph=graph), [1.0])


def test_lookup_is_not_composable() -> None:
    """A FIELD edge states no numbers: no matrix, and no path through it."""
    graph = _graph(LOOKUP, OFFSET)
    grid = CoordinateSystem.model_validate(GRID)
    with pytest.raises(ValueError, match="FIELD"):
        grid.path_to(CoordinateSystem.model_validate(WORLD), graph=graph)
    with pytest.raises(NotImplementedError, match="lookup"):
        graph.transformations[0].as_matrix()


def test_coordinate_system_reads() -> None:
    """Axis names follow `order`; a sample grid never carries a unit."""
    grid = CoordinateSystem.model_validate(GRID)
    assert grid.axis_names == ["t", "c"]
    assert grid.units == {"t": None, "c": None}
    assert grid.time_axis == "t"
    assert grid.get_axis("c").type == AxisType.CHANNEL


def test_selection_normalization() -> None:
    """The per-axis selection contract shared by `Trace.lens`."""
    assert normalize_selection("c", 2) == (2, 3, None)
    assert normalize_selection("t", (0, 100)) == (0, 100, None)
    assert normalize_selection("t", slice(0, 100, 2)) == (0, 100, 2)
    with pytest.raises(TypeError):
        normalize_selection("c", True)


def test_transformation_union_is_tagged() -> None:
    """The edges of a graph are a union on `__typename`; the sampling law keeps its children."""
    law = _graph(SAMPLING_LAW).transformations[0]
    assert type(law).__name__.endswith("ByDimensionTransformation")
    assert law.by_dimension_children[0].affine == [[1 / 30_000, 2.0]]

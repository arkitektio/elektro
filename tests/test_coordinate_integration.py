"""Integration tests for the coordinate-system model: grids, clocks, lenses and marks."""

import numpy as np
import pytest
import xarray as xr

from elektro.api.schema import (
    AnnotationKind,
    AxisInput,
    AxisType,
    CoordinateAnchorInput,
    ScaleInput,
    ScaleMethod,
    DatasetDerivedFromInput,
    IdentityTransformInput,
    PhysicalAxisInput,
    ValueUnitInput,
)
from kanne.scalars import Unit
from rath.operation import GraphQLException

from elektro.elektro import Elektro


@pytest.mark.integration
def test_dataset_grid_is_unitless(elektro: Elektro) -> None:
    """A one-dimensional array lives in one unit-less TIME sample grid.

    What the *values* measure is a `ValueUnit` anchor, read back as `valueUnit`;
    the axis carries no unit, because a sample grid holds indices.
    """
    dataset = elektro.create_array_dataset(
        data=np.random.random((500,)),
        scales=[],
        name="bare",
        axes=["t"],
        anchors=[
            CoordinateAnchorInput(axis_anchors=[], value_unit=ValueUnitInput(unit=Unit("mV")))
        ],
    )

    assert dataset.axis_names == ["t"]
    assert dataset.shape == [500]
    assert dataset.value_unit == Unit("mV")
    assert dataset.intrinsic_system.time_axis == "t"
    assert dataset.intrinsic_system.units == {"t": None}
    assert dataset.data.dims == ("t",)


@pytest.mark.integration
def test_multichannel_dataset_keeps_its_axes(elektro: Elektro) -> None:
    """A (t, c) array round-trips with its declared axes, given bare or labelled."""
    folder = elektro.create_folder(name="test_multichannel_dataset")
    values = np.random.random((200, 4))

    bare = elektro.create_array_dataset(
        data=values, scales=[], name="bare (t, c)", axes=["t", "c"], folder=folder.id
    )
    assert bare.data.dims == ("t", "c")
    np.testing.assert_allclose(np.asarray(bare.data), values)

    labelled = elektro.create_array_dataset(
        data=xr.DataArray(values, dims=["t", "c"]),
        scales=[],
        name="labelled (t, c)",
        axes=[AxisInput(name="t", type=AxisType.TIME), AxisInput(name="c", type=AxisType.CHANNEL)],
    )
    assert labelled.axis_names == ["t", "c"]


@pytest.mark.integration
def test_session_clock_states_a_sampling_law(elektro: Elektro) -> None:
    """One (t, c) signal on a session clock: the rate is stated once, on the edge."""
    # CS first: the session is a clock, the signal a dataset, the timing one sampling law.
    dataset = elektro.create_array_dataset(
        data=np.random.random((3000, 2)),
        scales=[],
        name="probe A",
        axes=["t", "c"],
        anchors=[
            CoordinateAnchorInput(axis_anchors=[], value_unit=ValueUnitInput(unit=Unit("uV")))
        ],
    )
    clock = elektro.create_coordinate_system(
        name="session",
        axes=[PhysicalAxisInput(name="t", type=AxisType.TIME, unit=Unit("second"))],
        registrations=[],
    )
    # `source` is the grid being timed -- a coordinate system, not the dataset.
    law = elektro.create_sampling_law(
        source=dataset.intrinsic_system.id, clock=clock.id, sampling_rate="30 kHz", t_start="2 s"
    )
    np.testing.assert_allclose(law.apply([30_000, 7]), [3.0])

    # The same numbers, found by walking the graph from the grid to the clock.
    times = dataset.intrinsic_system.axis_values_in(clock, "t", 3)
    np.testing.assert_allclose(times, 2.0 + np.arange(3) / 30_000)

    # A second law of the same grid onto the same clock is a rival, not a correction.
    with pytest.raises(GraphQLException, match="(?i)already|rival|timed"):
        elektro.create_sampling_law(
            source=dataset.intrinsic_system.id, clock=clock.id, sampling_rate="20 kHz", t_start="0 s"
        )


@pytest.mark.integration
def test_lens_selects_in_samples(elektro: Elektro) -> None:
    """A lens is an immutable selection; its data is the sliced dataset."""
    values = np.random.random((1000, 3))
    dataset = elektro.create_array_dataset(data=values, scales=[], name="to be lensed", axes=["t", "c"])

    lens = dataset.lens(t=(100, 300), c=1)
    assert lens.shape == [200, 1]
    np.testing.assert_allclose(np.asarray(lens.data), values[100:300, 1:2])

    assert elektro.get_lens(lens.id).id == lens.id
    with pytest.raises(ValueError, match="Invalid axis"):
        dataset.lens(z=0)


@pytest.mark.integration
def test_marks_drawn_over_a_dataset(elektro: Elektro) -> None:
    """An annotation collection owns its drawing space; an edge says what it marks."""
    dataset = elektro.create_array_dataset(
        data=np.random.random((1000,)), scales=[], name="marked", axes=["t"]
    )

    collection = elektro.create_annotation_collection(
        name="artifacts",
        axes=["t"],
        # Drawn in the dataset's own samples: the two spaces are the same grid.
        derived_from=[
            DatasetDerivedFromInput(dataset=dataset.id, transform=IdentityTransformInput())
        ],
    )
    epoch = elektro.create_annotation(
        kind=AnnotationKind.EPOCH,
        vectors=[[100.0], [250.0]],
        collection=collection.id,
        name="movement",
    )
    assert epoch.kind == AnnotationKind.EPOCH

    fetched = elektro.get_annotation_collection(collection.id)
    assert [a.name for a in fetched.annotations] == ["movement"]
    assert fetched.coordinate_system.axis_names == ["t"]


@pytest.mark.integration
def test_pyramid_levels_upload_and_read_back(elektro: Elektro) -> None:
    """Every level's array is uploaded, and the store belongs to the level.

    The overview a client reads when zoomed out over an hour at 30 kHz. This is
    also what proves the upload middleware walks into `scales`: a level whose
    array never reached S3 would come back as a store id the read cannot open.
    """
    values = np.random.random((1000, 2))
    # MAX, not an average: a decimated spike train must keep its peaks.
    overview = values.reshape(250, 4, 2).max(axis=1)

    dataset = elektro.create_array_dataset(
        data=values,
        scales=[ScaleInput(level=1, array=overview, scale_method=ScaleMethod.MAX)],
        name="pyramid",
        axes=["t", "c"],
    )

    assert dataset.multiscale
    assert sorted(a.level for a in dataset.data_arrays) == [0, 1]

    np.testing.assert_allclose(np.asarray(dataset.level_data(0)), values)
    np.testing.assert_allclose(np.asarray(dataset.level_data(1)), overview)
    assert dataset.data.dims == ("t", "c")
    assert [np.asarray(level).shape for level in dataset.multi_scale_data()] == [
        (1000, 2),
        (250, 2),
    ]

    with pytest.raises(ValueError, match="no pyramid level 2"):
        dataset.level_data(2)

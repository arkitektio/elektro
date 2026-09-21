"""Integration tests for the experiment-as-scene model: tables, spike rasters and layers.

CS first, as a session is built: the clock, then the data, then one timing edge per
dataset onto the clock, then the experiment read off the clock.
"""

import numpy as np
import pytest
import scipy.sparse as sp

from elektro.api.schema import (
    AxisType,
    ColorByInput,
    ColorMap,
    ColumnInput,
    PhysicalAxisInput,
    SparseAxisInput,
    TableIdentifiesInput,
)
from kanne.scalars import Unit

from elektro.elektro import Elektro

RATE_HZ = 1000.0
N_SAMPLES = 2000
N_UNITS = 4


def _session_clock(elektro: Elektro, name: str):  # noqa: ANN202
    return elektro.create_coordinate_system(
        name=name,
        axes=[PhysicalAxisInput(name="t", type=AxisType.TIME, unit=Unit("second"))],
        registrations=[],
    )


def _session(elektro: Elektro, clock_name: str) -> dict:
    """A clock and a trace, an event table, a units table and a raster, all timed on it."""
    clock = _session_clock(elektro, clock_name)

    trace = elektro.create_array_dataset(
        data=np.sin(np.arange(N_SAMPLES) / 50.0),
        scales=[],
        name="V soma",
        axes=["t"],
    )
    # Objects resolve to the space they mean: the trace to its sample grid.
    elektro.create_sampling_law(source=trace, clock=clock, sampling_rate=f"{RATE_HZ} Hz", t_start="0 s")

    events = elektro.create_table_dataset(
        name="TTL edges",
        data={"t": np.array([0.25, 0.5, 1.5]), "label": ["on", "off", "on"]},
        columns=[
            ColumnInput(name="t", axis_type=AxisType.TIME, unit=Unit("second")),
            ColumnInput(name="label"),
        ],
    )
    # An event table owns its (t) space; one offset places it on the session clock.
    elektro.create_clock_offset(clock=events, onto=clock, offset="0 s", drift_ppm=0.0)

    units = elektro.create_table_dataset(
        name="sorted units",
        data={"unit_id": np.arange(N_UNITS), "depth": np.array([10.0, 40.0, 70.0, 120.0])},
        columns=[
            ColumnInput(name="unit_id", axis_type=AxisType.INDEX),
            ColumnInput(name="depth", unit=Unit("micrometer")),
        ],
    )

    # Unit u fires every (u + 2) * 100 samples: a raster whose rows are distinguishable.
    rows, cols = [], []
    for unit in range(N_UNITS):
        spikes = np.arange(0, N_SAMPLES, (unit + 2) * 100)
        rows.extend([unit] * len(spikes))
        cols.extend(spikes.tolist())
    matrix = sp.csr_matrix(
        (np.ones(len(rows), dtype=np.float32), (rows, cols)), shape=(N_UNITS, N_SAMPLES)
    )
    raster = elektro.create_sparse_dataset(
        name="spike raster",
        store=[matrix, matrix.tocsc()],
        axes=[
            SparseAxisInput(name="unit", identified_by=[TableIdentifiesInput(table=units.id)]),
            SparseAxisInput(name="t", type=AxisType.TIME),
        ],
    )
    # A raster is placed exactly as the recording it was sorted from: by a sampling law.
    elektro.create_sampling_law(source=raster.coordinate_system.id, clock=clock.id, sampling_rate=f"{RATE_HZ} Hz", t_start="0 s")

    return {
        "clock": clock,
        "trace": trace,
        "events": events,
        "units": units,
        "raster": raster,
        "matrix": matrix,
    }


@pytest.mark.integration
def test_tables_and_raster_upload(elektro: Elektro) -> None:
    """Both tables and the raster read back as what was uploaded."""
    session = _session(elektro, "tables-and-raster")

    events = elektro.get_table_dataset(session["events"].id)
    assert [c.name for c in events.columns] == ["t", "label"]
    assert events.axis_names == ["t"]
    frame = events.data.df()
    np.testing.assert_allclose(frame["t"].to_numpy(), [0.25, 0.5, 1.5])

    raster = session["raster"]
    assert raster.axis_names == ["unit", "t"]
    assert raster.shape == [N_UNITS, N_SAMPLES]
    assert sorted(raster.indexable_axes) == ["t", "unit"]
    assert [ref.references.id for ref in raster.axis_references] == [session["units"].id]
    assert sum(layout.nnz for layout in raster.arrays[0].store.layouts) == 2 * session["matrix"].nnz


@pytest.mark.integration
def test_experiment_layers_by_hand(elektro: Elektro) -> None:
    """One layer per kind, each a view over data the experiment does not own."""
    session = _session(elektro, "layers-by-hand")
    experiment = elektro.create_experiment(name="by hand", coordinate_system=session["clock"].id)

    trace = elektro.create_trace_layer(
        experiment=experiment.id, dataset=session["trace"].id, name="V soma", color=[0, 0, 0, 255]
    )
    assert trace.lens.dataset.id == session["trace"].id
    assert trace.duration.to("second").magnitude == pytest.approx(N_SAMPLES / RATE_HZ)

    spikes = elektro.create_spikes_layer(
        experiment=experiment.id,
        sparse_dataset=session["raster"].id,
        name="units",
        color_bys=[
            ColorByInput(table=session["units"].id, column="depth", colormap=ColorMap.VIRIDIS)
        ],
    )
    assert spikes.unit_table.id == session["units"].id
    assert [c.column for c in spikes.color_bys] == ["depth"]

    events = elektro.create_events_layer(
        experiment=experiment.id,
        table_dataset=session["events"].id,
        label_column="label",
        name="TTL",
    )
    assert events.time_column == "t"
    assert events.label_column == "label"

    experiment = elektro.get_experiment(experiment.id)
    assert sorted(experiment.layers_of_kind(k)[0].name for k in ("TRACE", "SPIKES", "EVENTS")) == [
        "TTL",
        "V soma",
        "units",
    ]

    # The trace reads back through the graph onto the world, in the world's unit.
    data = experiment.data
    assert data["traces"].sizes == {"trace": 1, "time": N_SAMPLES}
    assert data["time"].attrs["units"] in ("second", "s")
    np.testing.assert_allclose(data["time"].values[:3], np.arange(3) / RATE_HZ)
    np.testing.assert_allclose(
        data["traces"].sel(trace="V soma").values, np.sin(np.arange(N_SAMPLES) / 50.0)
    )


@pytest.mark.integration
def test_experiment_from_clock(elektro: Elektro) -> None:
    """Bootstrapping from the clock lays out everything that reaches it, one layer each."""
    session = _session(elektro, "bootstrap")

    experiment = elektro.create_experiment_from_coordinate_system(
        coordinate_system=session["clock"].id, name="bootstrapped"
    )
    kinds = sorted(str(getattr(layer.kind, "value", layer.kind)) for layer in experiment.layers)
    # The units table has no TIME column and nothing times it: it is looked up, not laid out.
    assert kinds == ["EVENTS", "SPIKES", "TRACE"]
    assert experiment.world.id == session["clock"].id


@pytest.mark.integration
def test_multichannel_trace_layers(elektro: Elektro) -> None:
    """A (t, c) lens is one row per channel, or the one row its layer's channelIndex picks."""
    clock = _session_clock(elektro, "multichannel")
    values = np.stack([np.arange(100.0), 10 * np.arange(100.0), 100 * np.arange(100.0)], axis=1)
    probe = elektro.create_array_dataset(data=values, scales=[], name="probe", axes=["t", "c"])
    elektro.create_sampling_law(
        source=probe.intrinsic_system.id, clock=clock.id, sampling_rate="100 Hz", t_start="0 s"
    )
    experiment = elektro.create_experiment(name="multichannel", coordinate_system=clock.id)
    elektro.create_trace_layer(experiment=experiment.id, dataset=probe.id, name="all")
    elektro.create_trace_layer(experiment=experiment.id, dataset=probe.id, name="one", channel_index=1)

    traces = elektro.get_experiment(experiment.id).data["traces"]
    assert sorted(traces.coords["trace"].values.tolist()) == ["all[c=0]", "all[c=1]", "all[c=2]", "one"]
    np.testing.assert_allclose(traces.sel(trace="one").values, values[:, 1])
    np.testing.assert_allclose(traces.sel(trace="all[c=2]").values, values[:, 2])

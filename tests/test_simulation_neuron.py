"""NEURON-gated simulation tests.

These exercise the real ``run_simulation_processed`` engine against an in-memory,
service-free ``NeuronModel`` built from NEURON's built-in mechanisms (``pas``/``hh``),
so no ``.mod`` compilation and no arkitekt service are required.

The whole module is skipped when the optional ``neuron`` package is not installed.
"""

import numpy as np
import pytest

pytestmark = pytest.mark.neuron

pytest.importorskip("neuron")

from kanne.scalars import Duration, ElectricCurrent  # noqa: E402

from elektro.api.schema import (  # noqa: E402
    Cell,
    CellBiophysics,
    CellTopology,
    Compartment,
    NeuronModel,
    NeuronModelConfig,
    RecordingKind,
    Section,
    StimulusKind,
)
from elektro.neuron.simulate import (  # noqa: E402
    CurrentClampStimulus,
    SimulationResults,
    VRecord,
    run_simulation_processed,
)


def _single_soma_model() -> NeuronModel:
    """A one-section passive+HH soma, with no ModEnvironment (built-in mechanisms)."""
    topology = CellTopology(
        sections=[
            Section(
                id="soma",
                category="soma",
                nseg=1,
                diam="20 um",
                length="20 um",
                connections=[],
            )
        ]
    )
    biophysics = CellBiophysics(
        compartments=[
            Compartment(
                id="soma",
                mechanisms=["pas", "hh"],
                sectionParams=[],
                globalParams=[],
            )
        ]
    )
    config = NeuronModelConfig(
        vInit="-65 mV",
        temperature="310.15 K",
        cells=[Cell(id="cell_1", biophysics=biophysics, topology=topology)],
    )
    # ``environment`` is a required field on NeuronModel; bypass validation so we can
    # leave it ``None`` and skip the download/compile path in run_simulation_processed.
    return NeuronModel.model_construct(
        id="local-model", name="local-test", environment=None, config=config
    )


DURATION_MS = 50.0
DT_MS = 0.025
N_STEPS = int(round(DURATION_MS / DT_MS))


def _run() -> SimulationResults:
    model = _single_soma_model()
    return run_simulation_processed(
        model=model,
        duration=Duration(f"{DURATION_MS} ms"),
        stims=[
            CurrentClampStimulus(
                cell="cell_1",
                location="soma",
                position=0.5,
                amp=ElectricCurrent("0.1 nanoampere"),
                delay=Duration("10 ms"),
            )
        ],
        records=[VRecord(cell="cell_1", location="soma", position=0.5)],
        name="unit-sim",
        dt=Duration(f"{DT_MS} ms"),
    )


def test_time_trace_grid() -> None:
    """The time trace has ``N_STEPS + 1`` points and the snapped duration."""
    result = _run()
    # The engine snaps to an integer number of dt steps and records n_steps + 1 points.
    assert len(result.time_trace) == N_STEPS + 1
    assert result.duration.to("millisecond").magnitude == pytest.approx(N_STEPS * DT_MS)


def test_recordings_shape_and_kind() -> None:
    """The single recording is a voltage trace matching the time-trace length."""
    result = _run()
    assert len(result.recordings) == 1
    rec = result.recordings[0]
    assert rec.kind == RecordingKind.VOLTAGE
    assert np.asarray(rec.trace.value).shape[0] == len(result.time_trace)


def test_stimulus_grouped_and_waveform() -> None:
    """The stimulus is a single CURRENT waveform that is zero before the 10 ms delay."""
    result = _run()
    # One stimulus location -> one combined StimulusInput tagged as CURRENT.
    assert len(result.stimuli) == 1
    stim = result.stimuli[0]
    assert stim.kind == StimulusKind.CURRENT

    waveform = np.asarray(stim.trace.value)
    times = np.asarray(result.time_trace)
    # Zero current before the 10 ms delay, ~0.1 nA after.
    assert waveform[times < 10.0] == pytest.approx(0.0)
    assert waveform[-1] == pytest.approx(0.1, abs=1e-6)

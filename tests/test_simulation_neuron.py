"""NEURON-gated simulation tests.

These exercise the real ``run_simulation_processed`` engine against an in-memory,
service-free ``NeuronModel`` built from NEURON's built-in mechanisms (``pas``/``hh``),
so no ``.mod`` compilation and no arkitekt service are required.

The whole module is skipped when the optional ``neuron`` package is not installed.
"""

import numpy as np
import pytest

pytest.importorskip("neuron")

from kanne.scalars import Ampere  # noqa: E402

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
                diam=20.0,
                length=20.0,
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
        vInit=-65.0,
        celsius=37.0,
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


def _run():
    model = _single_soma_model()
    return run_simulation_processed(
        model=model,
        duration=DURATION_MS,
        stims=[
            CurrentClampStimulus(
                cell="cell_1",
                location="soma",
                position=0.5,
                amp=Ampere(0.1, "nanoampere"),
                delay=10,
            )
        ],
        records=[VRecord(cell="cell_1", location="soma", position=0.5)],
        name="unit-sim",
        dt=DT_MS,
    )


def test_time_trace_grid():
    result = _run()
    # The engine snaps to an integer number of dt steps and records n_steps + 1 points.
    assert len(result.time_trace) == N_STEPS + 1
    assert result.duration.to("millisecond").magnitude == pytest.approx(N_STEPS * DT_MS)


def test_recordings_shape_and_kind():
    result = _run()
    assert len(result.recordings) == 1
    rec = result.recordings[0]
    assert rec.kind == RecordingKind.VOLTAGE
    assert np.asarray(rec.trace.value).shape[0] == len(result.time_trace)


def test_stimulus_grouped_and_waveform():
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

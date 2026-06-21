"""Integration tests for the neuron-model workflow against a deployed Elektro.

Mirrors the user's script: build a ModEnvironment from .mod files, create a
NeuronModel, and (when NEURON is available locally) run a simulation end-to-end
and assemble an Experiment.

Requires the Docker stack via the ``deployed_app`` session fixture (conftest.py).
"""

import numpy as np
import pytest

from elektro.api.schema import (
    BiophysicsInput,
    CellInput,
    CompartmentInput,
    ModelConfigInput,
    RecordingViewInput,
    SectionInput,
    StimulusViewInput,
    TopologyInput,
    create_experiment,
    create_mod_environment,
    create_neuronmodel,
)
from elektro.neuron.parse import build_and_zip_environment

LEAK_MOD = """
TITLE Simple passive leak channel

NEURON {
    SUFFIX customleak
    NONSPECIFIC_CURRENT i
    RANGE g, e
}

PARAMETER {
    g = 0.001 (S/cm2)
    e = -65 (mV)
}

ASSIGNED {
    v (mV)
    i (mA/cm2)
}

BREAKPOINT {
    i = g * (v - e)
}
"""


def _build_environment(tmp_path):
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "customleak.mod").write_text(LEAK_MOD, encoding="utf-8")
    return build_and_zip_environment(
        str(model_dir), output_zip_path=str(tmp_path / "mechanisms.zip")
    )


def _config(environment_id) -> ModelConfigInput:
    topology = TopologyInput(
        sections=[
            SectionInput(
                category="soma", id="soma", nseg=1, diam="20 um", length="20 um", connections=[]
            )
        ]
    )
    biophysics = BiophysicsInput(
        compartments=[CompartmentInput(id="soma", mechanisms=["customleak"])]
    )
    return ModelConfigInput(
        cells=[
            CellInput(id="cell_1", biophysics=biophysics, topology=topology)
        ],
        netSynapses=[],
        netStimulators=[],
        netConnections=[],
        vInit="-65 mV",
        celsius=37,
    )


@pytest.mark.integration
def test_create_mod_environment(deployed_app, tmp_path):
    zip_file, mechanisms = _build_environment(tmp_path)
    env = create_mod_environment(
        name="customleak-env", zip_file=zip_file, mechanisms=mechanisms
    )
    assert env.id
    assert any(m.name == "customleak" for m in env.mechanisms)


@pytest.mark.integration
def test_create_neuronmodel_and_config_roundtrip(deployed_app, tmp_path):
    zip_file, mechanisms = _build_environment(tmp_path)
    env = create_mod_environment(
        name="customleak-env-2", zip_file=zip_file, mechanisms=mechanisms
    )

    model = create_neuronmodel(
        name="single-soma",
        config=_config(env.id),
        environment=env.id,
        description="leak-only soma",
    )
    assert model.id
    # The returned config converts back to a ModelConfigInput cleanly.
    as_input = model.config.as_input()
    assert as_input.cell_ids == ["cell_1"]


@pytest.mark.integration
def test_run_simulation_and_experiment(deployed_app, tmp_path):
    pytest.importorskip("neuron")  # end-to-end run compiles & executes locally

    from kanne.scalars import ElectricCurrent

    from elektro.neuron.simulate import (
        CurrentClampStimulus,
        VRecord,
        arun_simulation,
    )
    from koil import unkoil

    zip_file, mechanisms = _build_environment(tmp_path)
    env = create_mod_environment(
        name="customleak-env-3", zip_file=zip_file, mechanisms=mechanisms
    )
    model = create_neuronmodel(
        name="single-soma-sim", config=_config(env.id), environment=env.id
    )

    simulation = unkoil(
        arun_simulation,
        model=model,
        duration="50 ms",
        records=[VRecord(cell="cell_1", location="soma", position=0.5)],
        stims=[
            CurrentClampStimulus(
                cell="cell_1",
                location="soma",
                position=0.5,
                amp=ElectricCurrent("0.1 nanoampere"),
                delay="10 ms",
            )
        ],
        dt="0.025 ms",
    )

    assert simulation.id
    assert simulation.time_trace.data.shape[0] > 0
    assert len(simulation.recordings) == 1
    assert len(simulation.stimuli) == 1

    experiment = create_experiment(
        name="single-soma-experiment",
        time_trace=simulation.time_trace.id,
        recording_views=[
            RecordingViewInput(recording=rec.id, label=f"{rec.location}")
            for rec in simulation.recordings
        ],
        stimulus_views=[
            StimulusViewInput(stimulus=stim.id, label=f"{stim.location}")
            for stim in simulation.stimuli
        ],
    )
    assert experiment.id
    dataset = experiment.data
    assert "recordings" in dataset
    assert "stimulations" in dataset
    assert np.asarray(dataset["recordings"]).size > 0

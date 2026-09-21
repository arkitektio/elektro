"""Integration tests for the neuron-model workflow against a deployed Elektro.

Mirrors the user's script: build a ModEnvironment from .mod files, create a
NeuronModel, and (when NEURON is available locally) run a simulation end-to-end
and assemble an Experiment.

Requires the Docker stack via the ``elektro`` session fixture (conftest.py).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

from elektro.api.schema import (
    BiophysicsInput,
    CellInput,
    CompartmentInput,
    ModelConfigInput,
    SectionInput,
    TopologyInput,
)
from elektro.neuron.parse import build_and_zip_environment

if TYPE_CHECKING:
    from pathlib import Path

    from elektro.api.schema import MechanismInput

    from elektro.elektro import Elektro

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


def _build_environment(tmp_path: Path) -> tuple[str, list[MechanismInput]]:
    """Write a leak .mod file under ``tmp_path`` and build/zip its environment."""
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "customleak.mod").write_text(LEAK_MOD, encoding="utf-8")
    return build_and_zip_environment(
        str(model_dir), output_zip_path=str(tmp_path / "mechanisms.zip")
    )


def _config(environment_id: str) -> ModelConfigInput:
    topology = TopologyInput(
        sections=[
            SectionInput(
                category="soma", id="soma", nseg=1, diam="20 um", length="20 um"
            )
        ]
    )
    biophysics = BiophysicsInput(
        compartments=[CompartmentInput(id="soma", mechanisms=["customleak"])]
    )
    return ModelConfigInput(
        cells=[CellInput(id="cell_1", biophysics=biophysics, topology=topology)],
        netSynapses=[],
        netStimulators=[],
        netConnections=[],
        vInit="-65 mV",
        temperature="310.15 K",
    )


@pytest.mark.integration
def test_create_mod_environment(elektro: Elektro, tmp_path: Path) -> None:
    """Creating a ModEnvironment registers the custom leak mechanism."""
    zip_file, mechanisms = _build_environment(tmp_path)
    env = elektro.create_mod_environment(name="customleak-env", zip_file=zip_file, mechanisms=mechanisms)
    assert env.id
    assert any(m.name == "customleak" for m in env.mechanisms)


@pytest.mark.integration
def test_create_neuronmodel_and_config_roundtrip(
    elektro: Elektro, tmp_path: Path
) -> None:
    """A created NeuronModel's config round-trips back to a ModelConfigInput."""
    zip_file, mechanisms = _build_environment(tmp_path)
    env = elektro.create_mod_environment(name="customleak-env-2", zip_file=zip_file, mechanisms=mechanisms)

    model = elektro.create_neuronmodel(
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
def test_run_simulation_and_experiment(elektro: Elektro, tmp_path: Path) -> None:
    """End-to-end: run a NEURON simulation and assemble an Experiment from it."""
    pytest.importorskip("neuron")  # end-to-end run compiles & executes locally

    from kanne.scalars import ElectricCurrent

    from elektro.neuron.simulate import (
        CurrentClampStimulus,
        VRecord,
        arun_simulation,
    )
    from kanne.scalars import Duration
    from koil import unkoil

    zip_file, mechanisms = _build_environment(tmp_path)
    env = elektro.create_mod_environment(name="customleak-env-3", zip_file=zip_file, mechanisms=mechanisms)
    model = elektro.create_neuronmodel(name="single-soma-sim", config=_config(env.id), environment=env.id)

    run = unkoil(
        arun_simulation,
        elektro,
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

    # A run is its clock: no run row, just the clock and the datasets timed onto it.
    assert run.clock.id
    assert len(run.recordings) == 1
    assert len(run.stimuli) == 1
    recorded, injected = run.recordings[0], run.stimuli[0]

    # What was run is a spoke on the recording; the stimulus is the run's input and states none.
    recorded_anchor = elektro.get_array_dataset_anchors(recorded.id).anchors[0]
    assert recorded_anchor.simulation is not None
    assert recorded_anchor.simulation.model.id == model.id
    assert recorded_anchor.simulation.dt.to("millisecond").magnitude == pytest.approx(0.025)
    assert recorded_anchor.recording_site is not None
    injected_anchor = elektro.get_array_dataset_anchors(injected.id).anchors[0]
    assert injected_anchor.simulation is None
    assert injected_anchor.stimulus_site is not None

    # The model's runs are read off the graph: its simulated datasets, grouped by clock.
    sessions = elektro.get_neuron_model_sessions(model.id).sessions
    assert [(s.clock.id, [d.id for d in s.datasets]) for s in sessions] == [(run.clock.id, [recorded.id])]

    # The run's clock is the experiment's world: a TRACE layer per dataset timed on it.
    experiment = elektro.create_experiment_from_coordinate_system(
        coordinate_system=run.clock.id, name="single-soma-experiment"
    )
    assert experiment.id
    assert len(experiment.layers_of_kind("TRACE")) == 2 == len(experiment.layers)
    dataset = experiment.data
    assert dataset["traces"].sizes["trace"] == 2
    assert np.asarray(dataset["traces"]).size > 0
    # Timed through the graph: grid -> run clock (= world), in the world's unit.
    step = Duration(f"{float(dataset['time'].values[1])} {dataset['time'].attrs['units']}")
    assert step.to("millisecond").magnitude == pytest.approx(0.025)
    assert float(dataset["time"].values[0]) == 0.0

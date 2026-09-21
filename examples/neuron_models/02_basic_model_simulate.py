"""Basic neuron model — create AND simulate, built-in mechanisms, no .mod files.

Same single-soma model as ``01_basic_model.py``, but after persisting it we run a
NEURON simulation: inject a current-clamp step and record the somatic membrane
voltage, then read the resulting trace back.

Simulation runs the NEURON simulator locally, so this script needs the extra::

    pip install "elektro[neuron]"

Run it inside an Arkitekt environment (a reachable Elektro backend is required)::

    python 02_basic_model_simulate.py
"""

import tempfile

from arkitekt import App, connect

from elektro import Elektro
from elektro.api.schema import (
    BiophysicsInput,
    CellInput,
    CompartmentInput,
    DistributionInput,
    ModelConfigInput,
    SectionInput,
    SectionParamMapInput,
    TopologyInput,
)
from elektro.neuron.parse import build_and_zip_environment


def build_config() -> ModelConfigInput:
    """A one-section soma using only built-in NEURON mechanisms."""
    topology = TopologyInput(
        sections=[
            SectionInput(id="soma", category="soma", nseg=1, diam="20 um", length="20 um"),
        ]
    )
    biophysics = BiophysicsInput(
        compartments=[
            CompartmentInput(
                id="soma",
                mechanisms=["pas", "hh"],
                sectionParams=[
                    SectionParamMapInput(
                        param="g_pas",
                        mechanism="pas",
                        distribution=DistributionInput(value="0.001 S/cm2"),
                        description="passive leak conductance",
                    )
                ],
            )
        ]
    )
    return ModelConfigInput(
        cells=[CellInput(id="cell_1", biophysics=biophysics, topology=topology)],
        netSynapses=[],
        netStimulators=[],
        netConnections=[],
        vInit="-70 mV",
        temperature="310.15 K",
    )


def create_builtin_environment(elektro: Elektro, name: str):
    """Create a minimal, mechanism-free ModEnvironment (see 01_basic_model.py)."""
    empty_dir = tempfile.mkdtemp(prefix="elektro-builtin-env-")
    zip_file, mechanisms = build_and_zip_environment(empty_dir)
    return elektro.create_mod_environment(name=name, zip_file=zip_file, mechanisms=mechanisms)


def main() -> None:
    # Simulation-only imports — kept local so the create-only path in
    # 01_basic_model.py works without the NEURON extra installed.
    try:
        from koil import unkoil
        from kanne.scalars import ElectricCurrent

        from elektro.neuron.simulate import (
            CurrentClampStimulus,
            VRecord,
            arun_simulation,
        )
    except ImportError as exc:  # pragma: no cover - environment guard
        raise SystemExit(
            "This example runs a NEURON simulation and needs the neuron extra:\n"
            '    pip install "elektro[neuron]"\n'
            f"(import failed: {exc})"
        )

    with connect(App("neuron-model-examples", services=[Elektro])) as rt:
        elektro = rt.require(Elektro)
        env = create_builtin_environment(elektro, "builtin-mechanisms")
        model = elektro.create_neuronmodel(
            name="single-soma-basic-sim",
            config=build_config(),
            environment=env.id,
            description="A single-soma cell with built-in pas + hh mechanisms.",
        )
        print(f"Created NeuronModel {model.name!r} with id {model.id}")

        run = unkoil(
            arun_simulation,
            elektro,
            model=model,
            duration="50 ms",
            dt="0.025 ms",
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
        )
        # A run is its clock: the recordings and stimuli are timed onto it.
        print(f"Ran on clock {run.clock.name!r} ({run.clock.id})")
        print(f"Recording shape: {run.recordings[0].data.shape}")


if __name__ == "__main__":
    main()

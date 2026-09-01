"""Custom .mod neuron model — create AND simulate.

Same custom-mechanism workflow as ``03_mod_model.py`` (register ``customleak.mod``
as a ModEnvironment and build a single-soma model that uses it), but after
persisting the model we run a NEURON simulation: inject a current-clamp step,
record the somatic membrane voltage, and read the trace back.

At simulation time the server-side zip is downloaded and compiled with NEURON
(``nrnivmodl``) locally, so this script needs the extra::

    pip install "elektro[neuron]"

Run it inside an Arkitekt environment (a reachable Elektro backend is required)::

    python 04_mod_model_simulate.py
"""

from pathlib import Path

from arkitekt import easy

from elektro.api.schema import (
    BiophysicsInput,
    CellInput,
    CompartmentInput,
    DistributionInput,
    ModelConfigInput,
    SectionInput,
    SectionParamMapInput,
    TopologyInput,
    create_mod_environment,
    create_neuronmodel,
)
from elektro.neuron.parse import build_and_zip_environment

MOD_DIR = Path(__file__).parent / "mod_files"


def build_config() -> ModelConfigInput:
    """A one-section soma whose compartment uses the custom 'customleak' mechanism."""
    topology = TopologyInput(
        sections=[
            SectionInput(id="soma", category="soma", nseg=1, diam="20 um", length="20 um"),
        ]
    )
    biophysics = BiophysicsInput(
        compartments=[
            CompartmentInput(
                id="soma",
                mechanisms=["customleak"],
                sectionParams=[
                    SectionParamMapInput(
                        param="g",
                        mechanism="customleak",
                        distribution=DistributionInput(value="0.001 S/cm2"),
                        description="leak conductance of the custom mechanism",
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
        vInit="-65 mV",
        temperature="310.15 K",
    )


def main() -> None:
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

    zip_file, mechanisms = build_and_zip_environment(str(MOD_DIR))
    print(f"Parsed {len(mechanisms)} mechanism(s) from {MOD_DIR}:")
    for mech in mechanisms:
        print(f"  - {mech.name}")

    with easy("neuron-model-examples"):
        env = create_mod_environment(
            name="customleak-env",
            zip_file=zip_file,
            mechanisms=mechanisms,
        )
        print(f"Created ModEnvironment {env.name!r} with id {env.id}")

        model = create_neuronmodel(
            name="single-soma-customleak-sim",
            config=build_config(),
            environment=env.id,
            description="A single-soma cell driven by a custom leak .mod mechanism.",
        )
        print(f"Created NeuronModel {model.name!r} with id {model.id}")

        simulation = unkoil(
            arun_simulation,
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
        print(f"Ran simulation {simulation.id}")
        print(f"Recorded time trace shape: {simulation.time_trace.data.shape}")


if __name__ == "__main__":
    main()

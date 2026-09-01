"""Custom .mod neuron model — create only.

Registers a custom NEURON mechanism from an NMODL (``.mod``) file and builds a
single-soma model that uses it. The workflow:

1. ``build_and_zip_environment`` — zip the ``mod_files/`` directory and parse each
   ``.mod`` file into a ``MechanismInput`` (its SUFFIX name + RANGE parameters).
2. ``create_mod_environment`` — upload the zip and register the mechanisms as a
   ``ModEnvironment`` on the server.
3. ``create_neuronmodel`` — build the model config, referencing the custom
   mechanism by its SUFFIX name (``"customleak"``), against that environment.

The bundled ``mod_files/customleak.mod`` defines a passive leak channel
``i = g * (v - e)``.

Run it inside an Arkitekt environment (a reachable Elektro backend is required)::

    python 03_mod_model.py
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
                mechanisms=["customleak"],  # the SUFFIX from customleak.mod
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
    # Parse + zip the .mod directory. This step is offline; it does not need a
    # connection, so it can run before entering the Arkitekt context.
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
        print(f"  registered mechanisms: {[m.name for m in env.mechanisms]}")

        model = create_neuronmodel(
            name="single-soma-customleak",
            config=build_config(),
            environment=env.id,
            description="A single-soma cell driven by a custom leak .mod mechanism.",
        )
        print(f"Created NeuronModel {model.name!r} with id {model.id}")


if __name__ == "__main__":
    main()

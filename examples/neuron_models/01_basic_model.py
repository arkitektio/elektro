"""Basic neuron model — create only, built-in mechanisms, no .mod files.

Builds the simplest possible model: a single spherical soma with the built-in
passive leak (``pas``) and Hodgkin-Huxley (``hh``) mechanisms, then persists it
on the Elektro server as a ``NeuronModel``.

Physical quantities are written as unit-bearing strings (``"20 um"``,
``"-70 mV"``, ``"0.001 S/cm2"``) — that is the ``kanne`` quantity protocol the
``elektro`` inputs speak. There is no bare-number guessing.

Run it inside an Arkitekt environment (a reachable Elektro backend is required)::

    python 01_basic_model.py
"""

import tempfile

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


def build_config() -> ModelConfigInput:
    """A one-section soma using only built-in NEURON mechanisms."""
    topology = TopologyInput(
        sections=[
            # `category` is how a section is matched to a biophysics compartment.
            SectionInput(id="soma", category="soma", nseg=1, diam="20 um", length="20 um"),
        ]
    )
    biophysics = BiophysicsInput(
        compartments=[
            CompartmentInput(
                id="soma",  # matched to the "soma" section by category
                mechanisms=["pas", "hh"],  # built-ins — no .mod compilation needed
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


def create_builtin_environment(name: str):
    """Create a minimal ModEnvironment with no custom mechanisms.

    The server requires every NeuronModel to reference an environment, even when
    the model only uses built-in mechanisms. Zipping an *empty* directory yields
    a valid, mechanism-free environment that built-in ``pas``/``hh`` validate
    against.
    """
    empty_dir = tempfile.mkdtemp(prefix="elektro-builtin-env-")
    zip_file, mechanisms = build_and_zip_environment(empty_dir)
    return create_mod_environment(name=name, zip_file=zip_file, mechanisms=mechanisms)


def main() -> None:
    with easy("neuron-model-examples"):
        env = create_builtin_environment("builtin-mechanisms")
        model = create_neuronmodel(
            name="single-soma-basic",
            config=build_config(),
            environment=env.id,
            description="A single-soma cell with built-in pas + hh mechanisms.",
        )
        print(f"Created NeuronModel {model.name!r} with id {model.id}")


if __name__ == "__main__":
    main()

"""Unit tests for the neuron-model input schema and its trait helpers.

Covers the model-building patterns exercised by the user's simulation script:
topology/biophysics construction, ``get_*_for_id`` lookups, field-alias
population, ``extra="forbid"`` strictness, and deep-copy independence.
"""

import pytest
from kanne.scalars import Length
from pydantic import ValidationError

from elektro.api.schema import (
    BiophysicsInput,
    CellInput,
    CompartmentInput,
    ConnectionInput,
    DistributionInput,
    ModelConfigInput,
    SectionInput,
    SectionParamMapInput,
    TopologyInput,
)


def _topology() -> TopologyInput:
    return TopologyInput(
        sections=[
            SectionInput(
                category="soma", id="soma", nseg=1, diam="30 um", length="30 um"
            ),
            SectionInput(
                category="dend",
                id="dendrite",
                nseg=10,
                diam="1 um",
                length="120 um",
                parent=ConnectionInput(parent="soma", parentLocation=0.0),
            ),
        ]
    )


def _biophysics() -> BiophysicsInput:
    return BiophysicsInput(
        compartments=[
            CompartmentInput(
                id="soma",
                mechanisms=["pas", "hh"],
                sectionParams=[
                    SectionParamMapInput(
                        param="g_pas",
                        mechanism="pas",
                        distribution=DistributionInput(value="0.001 S/cm2"),
                        description="leak",
                    )
                ],
            )
        ]
    )


def _config() -> ModelConfigInput:
    return ModelConfigInput(
        cells=[CellInput(id="cell_1", biophysics=_biophysics(), topology=_topology())],
        netSynapses=[],
        netStimulators=[],
        netConnections=[],
        vInit="-70 mV",
        temperature="310.15 K",
    )


def test_topology_get_section_for_id() -> None:
    """``get_section_for_id`` returns the matching section and raises for unknown ids."""
    topo = _topology()
    assert topo.get_section_for_id("dendrite").length.to("micrometer").magnitude == 120
    assert topo.section_ids == ["soma", "dendrite"]
    with pytest.raises(ValueError):
        topo.get_section_for_id("missing")


def test_biophysics_get_compartment_for_id() -> None:
    """``get_compartment_for_id`` returns the matching compartment and raises otherwise."""
    bio = _biophysics()
    assert bio.get_compartment_for_id("soma").mechanisms == ["pas", "hh"]
    with pytest.raises(ValueError):
        bio.get_compartment_for_id("missing")


def test_compartment_get_section_param_for_id() -> None:
    """``get_section_param_for_id`` returns the matching param and raises for unknown ids."""
    comp = _biophysics().get_compartment_for_id("soma")
    assert comp.get_section_param_for_id("g_pas").distribution.value.to(
        "S/cm**2"
    ).magnitude == pytest.approx(0.001)
    with pytest.raises(ValueError):
        comp.get_section_param_for_id("missing")


def test_modelconfig_cell_lookup() -> None:
    """``get_cell_for_id`` and ``cell_ids`` resolve cells and raise for unknown ids."""
    config = _config()
    assert config.cell_ids == ["cell_1"]
    assert config.get_cell_for_id("cell_1").id == "cell_1"
    with pytest.raises(ValueError):
        config.get_cell_for_id("missing")


def test_field_alias_population() -> None:
    """snake_case attributes resolve even though they were set via camelCase aliases."""
    config = _config()
    assert config.v_init.to("millivolt").magnitude == -70
    assert config.net_synapses == []
    comp = config.get_cell_for_id("cell_1").biophysics.get_compartment_for_id("soma")
    assert comp.section_params[0].param == "g_pas"


def test_extra_fields_forbidden() -> None:
    """Passing an unknown field to ``SectionInput`` raises a ValidationError."""
    with pytest.raises(ValidationError):
        SectionInput(
            id="soma",
            category="soma",
            nseg=1,
            diam="30 um",
            length="30 um",
            bogus=1,
        )


def test_deep_copy_is_independent() -> None:
    """The script mutates a deep copy; the original must stay untouched."""
    original = _topology()
    copy = original.model_copy(deep=True)

    copy.get_section_for_id("soma").length = Length("99 um")

    assert copy.get_section_for_id("soma").length.to("micrometer").magnitude == 99.0
    assert original.get_section_for_id("soma").length.to("micrometer").magnitude == 30

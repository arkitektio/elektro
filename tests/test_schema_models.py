"""Unit tests for the neuron-model input schema and its trait helpers.

Covers the model-building patterns exercised by the user's simulation script:
topology/biophysics construction, ``get_*_for_id`` lookups, field-alias
population, ``extra="forbid"`` strictness, and deep-copy independence.
"""

import pytest
from pydantic import ValidationError

from elektro.api.schema import (
    BiophysicsInput,
    CellInput,
    CompartmentInput,
    ConnectionInput,
    ModelConfigInput,
    SectionInput,
    SectionParamMapInput,
    TopologyInput,
)


def _topology() -> TopologyInput:
    return TopologyInput(
        sections=[
            SectionInput(category="soma", id="soma", nseg=1, diam=30, length=30, connections=[]),
            SectionInput(
                category="dend",
                id="dendrite",
                nseg=10,
                diam=1.0,
                length=120,
                connections=[ConnectionInput(parent="soma", location=0.0)],
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
                        param="g_pas", mechanism="pas", value=0.001, description="leak"
                    )
                ],
            )
        ]
    )


def _config() -> ModelConfigInput:
    return ModelConfigInput(
        environments=[],
        cells=[CellInput(id="cell_1", biophysics=_biophysics(), topology=_topology())],
        netSynapses=[],
        netStimulators=[],
        netConnections=[],
        vInit=-70,
        celsius=37,
    )


def test_topology_get_section_for_id():
    topo = _topology()
    assert topo.get_section_for_id("dendrite").length == 120
    assert topo.section_ids == ["soma", "dendrite"]
    with pytest.raises(ValueError):
        topo.get_section_for_id("missing")


def test_biophysics_get_compartment_for_id():
    bio = _biophysics()
    assert bio.get_compartment_for_id("soma").mechanisms == ["pas", "hh"]
    with pytest.raises(ValueError):
        bio.get_compartment_for_id("missing")


def test_compartment_get_section_param_for_id():
    comp = _biophysics().get_compartment_for_id("soma")
    assert comp.get_section_param_for_id("g_pas").value == pytest.approx(0.001)
    with pytest.raises(ValueError):
        comp.get_section_param_for_id("missing")


def test_modelconfig_cell_lookup():
    config = _config()
    assert config.cell_ids == ["cell_1"]
    assert config.get_cell_for_id("cell_1").id == "cell_1"
    with pytest.raises(ValueError):
        config.get_cell_for_id("missing")


def test_field_alias_population():
    # snake_case attributes resolve even though they were set via camelCase aliases.
    config = _config()
    assert config.v_init == -70
    assert config.net_synapses == []
    comp = config.get_cell_for_id("cell_1").biophysics.get_compartment_for_id("soma")
    assert comp.section_params[0].param == "g_pas"


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        SectionInput(
            id="soma", category="soma", nseg=1, diam=30, length=30, connections=[], bogus=1
        )


def test_deep_copy_is_independent():
    """The script mutates a deep copy; the original must stay untouched."""
    original = _topology()
    copy = original.model_copy(deep=True)

    copy.get_section_for_id("soma").length = 99.0

    assert copy.get_section_for_id("soma").length == 99.0
    assert original.get_section_for_id("soma").length == 30

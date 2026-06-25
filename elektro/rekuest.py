"""Register elektro GraphQL types as rekuest structures.

Imported for its side effects: each ``register_as_structure`` call wires an
elektro type (Trace, Simulation, Experiment, ...) into the default structure
registry so it can be expanded, shrunk and searched within rekuest.
"""

from rekuest_next.structures.default import (
    get_default_structure_registry,
    id_shrink,
)
from rekuest_next.widgets import SearchWidget
from elektro.api.schema import *

structure_reg = get_default_structure_registry()

structure_reg.register_as_structure(
    Trace,
    identifier="@elektro/trace",
    aexpand=aget_trace,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchTracesQuery.Meta.document, ward="elektro"),
)

structure_reg.register_as_structure(
    Simulation,
    identifier="@elektro/simulation",
    aexpand=aget_simulation,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchSimulationsQuery.Meta.document, ward="elektro"),
)

structure_reg.register_as_structure(
    Experiment,
    identifier="@elektro/experiment",
    aexpand=aget_experiment,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchExperimentsQuery.Meta.document, ward="elektro"),
)

structure_reg.register_as_structure(
    Block,
    identifier="@elektro/block",
    aexpand=aget_block,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchBlocksQuery.Meta.document, ward="elektro"),
)

structure_reg.register_as_structure(
    Recording,
    identifier="@elektro/recording",
    aexpand=aget_recording,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchRecordingsQuery.Meta.document, ward="elektro"),
)

structure_reg.register_as_structure(
    Stimulus,
    identifier="@elektro/stimulus",
    aexpand=aget_stimulus,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchStimuliQuery.Meta.document, ward="elektro"),
)

structure_reg.register_as_structure(
    ModelCollection,
    identifier="@elektro/modelcollection",
    aexpand=aget_model_collection,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchModelCollectionQuery.Meta.document, ward="elektro"),
)

structure_reg.register_as_structure(
    ROI,
    identifier="@elektro/roi",
    aexpand=aget_roi,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchRoisQuery.Meta.document, ward="elektro"),
)


structure_reg.register_as_structure(
    NeuronModel,
    identifier="@elektro/neuronmodel",
    aexpand=aget_neuron_model,
    ashrink=id_shrink,
    default_widget=SearchWidget(query=SearchNeuronModelsQuery.Meta.document, ward="elektro"),
)

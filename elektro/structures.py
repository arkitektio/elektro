"""The types elektro sends by id: each expanded by the ``Elektro`` client.

Imported by ``elektro/__init__``, so each class is marked whenever elektro is.
"""

from arkitekt_spec.declare.structures.declare import structure
from arkitekt_spec.declare.widgets import SearchWidget

from elektro.api.schema import (
    Annotation,
    AnnotationCollection,
    ArrayDataset,
    CoordinateSystem,
    Experiment,
    File,
    Folder,
    Lens,
    ModelCollection,
    NeuronModel,
    SearchAnnotationCollectionsQuery,
    SearchArrayDatasetsQuery,
    SearchCoordinateSystemsQuery,
    SearchExperimentsQuery,
    SearchFilesQuery,
    SearchFoldersQuery,
    SearchModelCollectionQuery,
    SearchNeuronModelsQuery,
    SearchSparseDatasetsQuery,
    SearchTableDatasetsQuery,
    SparseDataset,
    TableDataset,
)
from elektro.elektro import Elektro
from elektro.specs import describe_lens


def _search(query: object) -> SearchWidget:
    """The widget that picks one of these out of the deployment."""
    return SearchWidget(query=query.Meta.document, ward="elektro")  # type: ignore[attr-defined]


@structure(
    "@elektro/arraydataset",
    widget=_search(SearchArrayDatasetsQuery),
    describe=describe_lens,
)
async def expand_array_dataset(id: str, elektro: Elektro) -> ArrayDataset:
    """An array dataset, by id."""
    return await elektro.aget_array_dataset(id)


@structure("@elektro/experiment", widget=_search(SearchExperimentsQuery))
async def expand_experiment(id: str, elektro: Elektro) -> Experiment:
    """An experiment, by id."""
    return await elektro.aget_experiment(id)


@structure("@elektro/tabledataset", widget=_search(SearchTableDatasetsQuery))
async def expand_table_dataset(id: str, elektro: Elektro) -> TableDataset:
    """A table dataset, by id."""
    return await elektro.aget_table_dataset(id)


@structure("@elektro/sparsedataset", widget=_search(SearchSparseDatasetsQuery))
async def expand_sparse_dataset(id: str, elektro: Elektro) -> SparseDataset:
    """A sparse dataset, by id."""
    return await elektro.aget_sparse_dataset(id)


@structure("@elektro/modelcollection", widget=_search(SearchModelCollectionQuery))
async def expand_model_collection(id: str, elektro: Elektro) -> ModelCollection:
    """A model collection, by id."""
    return await elektro.aget_model_collection(id)


@structure(
    "@elektro/annotationcollection",
    widget=_search(SearchAnnotationCollectionsQuery),
)
async def expand_annotation_collection(
    id: str, elektro: Elektro
) -> AnnotationCollection:
    """An annotation collection, by id."""
    return await elektro.aget_annotation_collection(id)


# The annotations themselves have no search query: one is picked through its
# collection, not out of every shape in the deployment.
@structure("@elektro/annotation")
async def expand_annotation(id: str, elektro: Elektro) -> Annotation:
    """One annotation, by id."""
    return await elektro.aget_annotation(id)


@structure("@elektro/lens", describe=describe_lens)
async def expand_lens(id: str, elektro: Elektro) -> Lens:
    """A lens, by id."""
    return await elektro.aget_lens(id)


@structure(
    "@elektro/coordinatesystem",
    widget=_search(SearchCoordinateSystemsQuery),
)
async def expand_coordinate_system(id: str, elektro: Elektro) -> CoordinateSystem:
    """A coordinate system, by id."""
    return await elektro.aget_coordinate_system(id)


@structure("@elektro/neuronmodel", widget=_search(SearchNeuronModelsQuery))
async def expand_neuron_model(id: str, elektro: Elektro) -> NeuronModel:
    """A neuron model, by id."""
    return await elektro.aget_neuron_model(id)


# `@elektro/folder`, the identifier the elektro service declares it hosts. (A
# folder used to travel as `@elektro/dataset`; an app registered with that
# identifier has to re-register.)
@structure("@elektro/folder", widget=_search(SearchFoldersQuery))
async def expand_folder(id: str, elektro: Elektro) -> Folder:
    """A folder, by id."""
    return await elektro.aget_folder(id)


@structure("@elektro/file", widget=_search(SearchFilesQuery))
async def expand_file(id: str, elektro: Elektro) -> File:
    """A file, by id."""
    return await elektro.aget_file(id)

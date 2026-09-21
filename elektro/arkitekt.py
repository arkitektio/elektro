"""The elektro service of an arkitekt app, and the types it sends by id.

Declared on one registry: the service first, then the structures whose expanders
ask for the ``Elektro`` it returns. Each type is declared once -- the class, the
identifier it travels under, the widget a user picks one with, and how to fetch it
back. An app takes all of it in with ``App(services=[elektro_service])``.
"""

import os
from typing import Annotated

from fakts import Alias, Require, TokenLoader
from fakts.contrib.rath.auth import FaktsAuthLink
from graphql import OperationType
from kanne.contrib.rath.coerce_pint import CoercePintLink
from rath.links import compose
from rath.links.aiohttp import AIOHttpLink
from rath.links.dictinglink import DictingLink
from rath.links.file import FileExtraction
from rath.links.graphql_ws import GraphQLWSLink
from rath.links.split import SplitLink

from rekuest.app import AppRegistry
from rekuest.widgets import SearchWidget

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

from elektro.datalayer import DataLayer
from elektro.elektro import Elektro
from elektro.middleware.upload import UploadMiddleware
from elektro.rath import ElektroRath


def build_relative_path(*path: str) -> str:
    """Build a path relative to this file, for the files shipped beside it."""
    return os.path.join(os.path.dirname(__file__), *path)


registry = AppRegistry()
"""What elektro brings to an app: its service, and the types it can send by id."""


@registry.service(
    schema=build_relative_path("api", "schema.graphql"),
    turms=build_relative_path("api", "project.json"),
)
def elektro(
    elektro: Annotated[
        Alias,
        Require("live.arkitekt.elektro", "Where the user's traces and recordings live"),
    ],
    datalayer: Annotated[
        Alias,
        Require("live.arkitekt.s3", "Where the user's files are stored"),
    ],
    tokens: TokenLoader,
) -> Elektro:
    """Elektro: electrophysiology traces, recordings and their metadata."""
    store = DataLayer.from_alias(datalayer)

    return Elektro(
        rath=ElektroRath(
            link=compose(
                FileExtraction(),
                DictingLink(),
                CoercePintLink(),
                FaktsAuthLink(token_loader=tokens),
                SplitLink(
                    left=AIOHttpLink(endpoint_url=elektro.to_http_path("graphql")),
                    right=GraphQLWSLink(ws_endpoint_url=elektro.to_ws_path("graphql")),
                    split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                ),
            ),
            middlewares=[UploadMiddleware(datalayer=store)],
        ),
        datalayer=store,
    )


def _search(query: object) -> SearchWidget:
    """The widget that picks one of these out of the deployment."""
    return SearchWidget(query=query.Meta.document, ward="elektro")  # type: ignore[attr-defined]


@registry.structure("@elektro/arraydataset", widget=_search(SearchArrayDatasetsQuery)
)
async def expand_array_dataset(id: str, elektro: Elektro) -> ArrayDataset:
    """An array dataset, by id."""
    return await elektro.aget_array_dataset(id)


@registry.structure("@elektro/experiment", widget=_search(SearchExperimentsQuery))
async def expand_experiment(id: str, elektro: Elektro) -> Experiment:
    """An experiment, by id."""
    return await elektro.aget_experiment(id)


@registry.structure("@elektro/tabledataset", widget=_search(SearchTableDatasetsQuery)
)
async def expand_table_dataset(id: str, elektro: Elektro) -> TableDataset:
    """A table dataset, by id."""
    return await elektro.aget_table_dataset(id)


@registry.structure("@elektro/sparsedataset", widget=_search(SearchSparseDatasetsQuery)
)
async def expand_sparse_dataset(id: str, elektro: Elektro) -> SparseDataset:
    """A sparse dataset, by id."""
    return await elektro.aget_sparse_dataset(id)


@registry.structure("@elektro/modelcollection", widget=_search(SearchModelCollectionQuery)
)
async def expand_model_collection(id: str, elektro: Elektro) -> ModelCollection:
    """A model collection, by id."""
    return await elektro.aget_model_collection(id)


@registry.structure("@elektro/annotationcollection",
    widget=_search(SearchAnnotationCollectionsQuery),
)
async def expand_annotation_collection(id: str, elektro: Elektro) -> AnnotationCollection:
    """An annotation collection, by id."""
    return await elektro.aget_annotation_collection(id)


# The annotations themselves have no search query: one is picked through its
# collection, not out of every shape in the deployment.
@registry.structure("@elektro/annotation")
async def expand_annotation(id: str, elektro: Elektro) -> Annotation:
    """One annotation, by id."""
    return await elektro.aget_annotation(id)


@registry.structure("@elektro/lens")
async def expand_lens(id: str, elektro: Elektro) -> Lens:
    """A lens, by id."""
    return await elektro.aget_lens(id)


@registry.structure("@elektro/coordinatesystem",
    widget=_search(SearchCoordinateSystemsQuery),
)
async def expand_coordinate_system(id: str, elektro: Elektro) -> CoordinateSystem:
    """A coordinate system, by id."""
    return await elektro.aget_coordinate_system(id)


@registry.structure("@elektro/neuronmodel", widget=_search(SearchNeuronModelsQuery)
)
async def expand_neuron_model(id: str, elektro: Elektro) -> NeuronModel:
    """A neuron model, by id."""
    return await elektro.aget_neuron_model(id)


# `Dataset` was renamed `Folder` (it collided with the data it filed), but the
# identifier is a wire contract workflow definitions name, so it stays -- exactly
# as mikro's `Folder` keeps `@mikro/dataset`.
@registry.structure("@elektro/dataset", widget=_search(SearchFoldersQuery))
async def expand_folder(id: str, elektro: Elektro) -> Folder:
    """A folder, by id -- it travels as `@elektro/dataset`."""
    return await elektro.aget_folder(id)


@registry.structure("@elektro/file", widget=_search(SearchFilesQuery))
async def expand_file(id: str, elektro: Elektro) -> File:
    """A file, by id."""
    return await elektro.aget_file(id)

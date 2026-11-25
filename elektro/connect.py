"""How ``Elektro`` reaches a resolved deployment: its links and upload middleware."""

from arkitekt_spec.declare.wiring import Alias, TokenLoader
from fakts.contrib.rath.auth import FaktsAuthLink
from kanne.contrib.rath.coerce_pint import CoercePintLink
from rath.links import compose
from rath.links.aiohttp import AIOHttpLink
from rath.links.dictinglink import DictingLink
from rath.links.file import FileExtraction
from rath.links.graphql_ws import GraphQLWSLink
from rath.links.split import SplitLink

from elektro.datalayer import DataLayer
from elektro.middleware.upload import UploadMiddleware
from elektro.rath import ElektroRath
from graphql import OperationType


def elektro_rath(
    elektro: Alias, datalayer: DataLayer, tokens: TokenLoader
) -> ElektroRath:
    """The rath over http and ws, uploading files to ``datalayer`` first."""
    return ElektroRath(
        link=compose(
            FileExtraction(),
            DictingLink(),
            CoercePintLink(),
            FaktsAuthLink(token_loader=tokens),
            SplitLink(
                left=AIOHttpLink(
                    endpoint_url=elektro.to_http_path("graphql"),
                    proxy=elektro.proxy,
                    ssl_context=elektro.ssl_context(),
                ),
                right=GraphQLWSLink(
                    ws_endpoint_url=elektro.to_ws_path("graphql"),
                    proxy=elektro.proxy,
                    ssl_context=elektro.ssl_context(),
                ),
                split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
            ),
        ),
        middlewares=[UploadMiddleware(datalayer=datalayer)],
    )


__all__ = ["elektro_rath"]

import json
import os
from elektro.elektro import Elektro
from elektro.rath import ElektroLinkComposition, ElektroRath
from rath.links.split import SplitLink
from fakts_next import Fakts
from herre_next import Herre
from arkitekt_next.service_registry import BaseArkitektService, Params
from arkitekt_next.base_models import Manifest, Requirement

from fakts_next.contrib.rath.aiohttp import FaktsAIOHttpLink
from fakts_next.contrib.rath.graphql_ws import FaktsGraphQLWSLink
from herre_next.contrib.rath.auth_link import HerreAuthLink
from elektro.contrib.fakts.datalayer import FaktsDataLayer
from elektro.links.upload import UploadLink
from graphql import OperationType
from arkitekt_next.service_registry import (
    get_default_service_registry,
)


def build_relative_path(*path: str) -> str:
    return os.path.join(os.path.dirname(__file__), *path)


class ElektroService(BaseArkitektService):
    def get_service_name(self):
        return "elektro"

    def build_service(
        self, fakts: Fakts, herre: Herre, params: Params, manifest: Manifest
    ):
        datalayer = FaktsDataLayer(fakts_group="datalayer", fakts=fakts)

        return Elektro(
            rath=ElektroRath(
                link=ElektroLinkComposition(
                    auth=HerreAuthLink(herre=herre),
                    upload=UploadLink(
                        datalayer=datalayer,
                    ),
                    split=SplitLink(
                        left=FaktsAIOHttpLink(
                            fakts_group="elektro", fakts=fakts, endpoint_url="FAKE_URL"
                        ),
                        right=FaktsGraphQLWSLink(
                            fakts_group="elektro",
                            fakts=fakts,
                            ws_endpoint_url="FAKE_URL",
                        ),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                )
            ),
            datalayer=datalayer,
        )

    def get_requirements(self):
        return [
            Requirement(
                key="elektro",
                service="live.arkitekt.elektro",
                description="An instance of ArkitektNext Mikro to make requests to the user's data",
                optional=True,
            ),
            Requirement(
                key="datalayer",
                service="live.arkitekt.s3",
                description="An instance of ArkitektNext Datalayer to make requests to the user's data",
                optional=True,
            ),
        ]

    def get_graphql_schema(self):
        schema_graphql_path = build_relative_path("api", "schema.graphql")
        with open(schema_graphql_path) as f:
            return f.read()

    def get_turms_project(self):
        turms_prject = build_relative_path("api", "project.json")
        with open(turms_prject) as f:
            return json.loads(f.read())


get_default_service_registry().register(ElektroService())

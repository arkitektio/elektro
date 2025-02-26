import pytest
from dokker import mirror, Deployment
import os
from koil.composition import Composition
from elektro.elektro import Elektro
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links.sign_local_link import ComposedSignTokenLink
from rath.links.graphql_ws import GraphQLWSLink
from elektro.elektro import ElektroRath
from elektro.rath import (
    ElektroRath,
    UploadLink,
    SplitLink,
    ElektroLinkComposition,
)
from elektro.datalayer import DataLayer
from graphql import OperationType

project_path = os.path.join(os.path.dirname(__file__), "integration")
private_key = os.path.join(project_path, "private_key.pem")


async def payload_retriever(o):
    return {"sub": 1}

@pytest.fixture(scope="session")
def deployed_app() -> Elektro:


    setup = mirror(project_path)
    setup.project.overwrite = True
    setup.add_health_check(
        url="http://localhost:8456/ht", service="mikro", timeout=5, max_retries=10
    )

    watcher = setup.create_watcher("mikro")

    datalayer = DataLayer(
        endpoint_url="http://localhost:8457",
    )

    y = ElektroRath(
        link=ElektroLinkComposition(
            auth=ComposedSignTokenLink(
                private_key=private_key,
                payload_retriever=payload_retriever
            ),
            upload=UploadLink(datalayer=datalayer),
            split=SplitLink(
                left=AIOHttpLink(endpoint_url="http://localhost:8456/graphql"),
                right=GraphQLWSLink(ws_endpoint_url="ws://localhost:8456/graphql"),
                split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
            ),
        ),
    )

    elektro = Elektro(
        datalayer=datalayer,
        rath=y,
    )

    with setup:
            
            setup.up()
            
            setup.check_health()

            with watcher:
                
                with elektro as m:
                    yield elektro






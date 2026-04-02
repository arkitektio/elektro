from typing import Generator
import pytest
from dokker import local, Deployment
from dokker.log_watcher import LogWatcher
import os
from elektro.elektro import Elektro
from rath.links.auth import ComposedAuthLink
from rath.links.aiohttp import AIOHttpLink
from rath.links.graphql_ws import GraphQLWSLink
from elektro.rath import (
    ElektroRath,
    UploadLink,
    SplitLink,
    ElektroLinkComposition,
)
from elektro.datalayer import DataLayer
from graphql import OperationType
from dataclasses import dataclass

project_path = os.path.join(os.path.dirname(__file__), "integration")
docker_compose_file = os.path.join(project_path, "docker-compose.yml")
private_key = os.path.join(project_path, "private_key.pem")


async def token_loader() -> str:
    """Asynchronous function to load a token for authentication.

    This returns the "test" token which is configured as a static token to map to
    the user "test" in the test environment. In a real application, this function
    will return an oauth2 token or similar authentication token.

    To change this mapping you can alter the static_token configuration in the
    mikro configuration file (inside the integration folder).

    """
    return "test"


@dataclass
class DeployedElektro:
    """Dataclass to hold the deployed MikroNext application and its components."""

    deployment: Deployment
    mikro_watcher: LogWatcher
    minio_watcher: LogWatcher
    mikro: Elektro


@pytest.fixture(scope="session")
def deployed_app() -> Generator[DeployedElektro, None, None]:
    """Fixture to deploy the MikroNext application with Docker Compose.

    This fixture sets up the MikroNext application using Docker Compose,
    configures health checks, and provides a deployed instance of MikroNext
    for testing purposes. It also includes watchers for the Mikro and MinIO
    services to monitor their logs, when performing requests against the application.

    Yields:
        DeployedMikro: An instance containing the deployment, watchers, and MikroNext instance

    """
    setup = local(docker_compose_file)
    setup.add_health_check(
        url=lambda spec: f"http://localhost:{spec.find_service('elektro').get_port_for_internal(80).published}/graphql",
        service="elektro",
        timeout=5,
        max_retries=10,
    )

    watcher = setup.create_watcher("elektro")
    minio_watcher = setup.create_watcher("minio")

    with setup:
        setup.down()
        setup.pull()

        minio_url = f"http://localhost:{setup.spec.find_service('minio').get_port_for_internal(9000).published}"
        elektro_http_url = f"http://localhost:{setup.spec.find_service('elektro').get_port_for_internal(80).published}/graphql"
        elektro_ws_url = f"ws://localhost:{setup.spec.find_service('elektro').get_port_for_internal(80).published}/graphql"

        datalayer = DataLayer(
            endpoint_url=minio_url,
        )

        y = ElektroRath(
            link=ElektroLinkComposition(
                auth=ComposedAuthLink(token_loader=token_loader, token_refresher=token_loader),
                upload=UploadLink(datalayer=datalayer),
                split=SplitLink(
                    left=AIOHttpLink(endpoint_url=elektro_http_url),
                    right=GraphQLWSLink(ws_endpoint_url=elektro_ws_url),
                    split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                ),
            ),
        )

        mikro = Elektro(
            datalayer=datalayer,
            rath=y,
        )

        setup.up()

        setup.check_health()

        with mikro as mikro:
            deployed = DeployedElektro(
                deployment=setup,
                mikro_watcher=watcher,
                minio_watcher=minio_watcher,
                mikro=mikro,
            )

            yield deployed

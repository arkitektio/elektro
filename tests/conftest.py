"""Shared pytest fixtures and configuration for the elektro test suite."""

import sys
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
    SplitLink,
    ElektroLinkComposition,
)
from elektro.datalayer import DataLayer
from elektro.middleware.upload import UploadMiddleware
from graphql import OperationType
from dataclasses import dataclass


def pytest_configure(config: pytest.Config) -> None:
    """Register custom platform markers."""
    config.addinivalue_line("markers", "linux_only: skip on non-Linux platforms")
    config.addinivalue_line("markers", "no_windows: skip on Windows")


def pytest_collection_modifyitems(config: pytest.Config, items: list) -> None:  # noqa: ARG001
    """Skip tests marked linux_only or no_windows on the wrong platform."""
    for item in items:
        if item.get_closest_marker("linux_only") and sys.platform != "linux":
            item.add_marker(pytest.mark.skip(reason="Linux only"))
        if item.get_closest_marker("no_windows") and sys.platform == "win32":
            item.add_marker(pytest.mark.skip(reason="Not supported on Windows"))


project_path = os.path.join(os.path.dirname(__file__), "integration")
docker_compose_file = os.path.join(project_path, "docker-compose.yml")
private_key = os.path.join(project_path, "private_key.pem")


async def token_loader() -> str:
    """Asynchronous function to load a token for authentication.

    This returns the "test" token which is configured as a static token to map to
    the user "test" in the test environment. In a real application, this function
    will return an oauth2 token or similar authentication token.

    To change this mapping you can alter the static_token configuration in the
    elektro configuration file (inside the integration folder).

    """
    return "test"


@dataclass
class DeployedElektro:
    """Dataclass to hold the deployed Elektro application and its components."""

    deployment: Deployment
    elektro_watcher: LogWatcher
    minio_watcher: LogWatcher
    elektro: Elektro


@pytest.fixture(scope="session")
def deployed_app() -> Generator[DeployedElektro, None, None]:
    """Fixture to deploy the Elektro application with Docker Compose.

    This fixture sets up the Elektro application using Docker Compose,
    configures health checks, and provides a deployed instance of Elektro
    for testing purposes. It also includes watchers for the Elektro and MinIO
    services to monitor their logs, when performing requests against the application.

    Yields:
        DeployedElektro: An instance containing the deployment, watchers, and Elektro instance

    """
    setup = local(docker_compose_file)
    setup.add_health_check(
        url=lambda spec: (
            f"http://localhost:{spec.find_service('elektro').get_port_for_internal(80).published}/graphql"
        ),
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
                split=SplitLink(
                    left=AIOHttpLink(endpoint_url=elektro_http_url),
                    right=GraphQLWSLink(ws_endpoint_url=elektro_ws_url),
                    split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                ),
            ),
            middlewares=[
                UploadMiddleware(datalayer=datalayer),
            ],
        )

        elektro = Elektro(
            datalayer=datalayer,
            rath=y,
        )

        setup.up()

        setup.run("initc", command="python init.py")

        setup.check_health()

        with elektro as elektro:
            deployed = DeployedElektro(
                deployment=setup,
                elektro_watcher=watcher,
                minio_watcher=minio_watcher,
                elektro=elektro,
            )

            yield deployed

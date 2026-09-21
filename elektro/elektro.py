"""The top-level Elektro client composition."""

from collections.abc import AsyncGenerator, Generator
from typing import Any

from koil import unkoil_gen
from koil.composition import Composition
from pydantic import Field
from rath.origin import origin_context
from rath.task import TASK_HEADER, TaskLike, current_task, token_of
from rath.turms.funcs import TOperation

from elektro.api.schema import ElektroApi
from elektro.datalayer import DataLayer
from elektro.middleware.base import OperationMiddleware
from elektro.rath import ElektroRath



class Elektro(Composition, ElektroApi):
    """The Elektro Composition

    This composition provides a datalayer and a rath for interacting with the
    elektro api and beyond. Every operation of the api is a method of it
    (``elektro.aget_lens(id)``), mixed in from the generated ``ElektroApi``. Each
    generated method hands its operation class and variables to ``execute``/
    ``aexecute`` (queries and mutations) or ``subscribe``/``asubscribe``
    (subscriptions), implemented here over ``self.rath``. Nothing is looked up.
    The objects a call returns remember the client it was called on, so what
    they fetch later (``.data``, ``.download()``) goes through it too.

    Middleware Support:
        The execute/subscribe methods support a middleware chain that processes
        serialized variables before they reach the rath link chain. Middleware is
        configured on the ElektroRath instance via its `middlewares` field.

        Two distinct paths are provided:
            - Sync (execute/subscribe): Calls middleware.process_variables()
              which uses sync I/O (e.g., obstore for S3 uploads).
            - Async (aexecute/asubscribe): Calls middleware.aprocess_variables()
              which uses async I/O (e.g., obstore for S3 uploads).

    You shouldn't need to create this directly, instead use the builder functions
    to generate a new instance of this composition.

    ```python

    from elektro import Elektro

    async def aget_token():
        return "XXXX"

    e = Elektro(
        datalayer=DataLayer(endpoint_url="s3.amazonaws.com", access_key="XXXX", secret_key="XXXX"),
        rath=ElektroRath(link=ElektroLinkComposition(auth=AuthTokenLink(token_loader=aget_token))),
    )
    ```
    """

    datalayer: DataLayer = Field(
        ..., description="The datalayer for interacting with the minio api"
    )
    rath: ElektroRath = Field(
        ...,
        description="The rath for interacting with the elektro api",
    )


    def _origin(self) -> dict[str, Any]:
        """What the objects of a result should remember: the client that fetched them.

        The origin names the client, so an object's later calls (``.data``,
        ``.download()``, a follow-up query) go through the exact client, rath and
        datalayer, that produced it.
        """
        return origin_context(client=self, rath=self.rath, datalayer=self.datalayer)

    def _headers(self, task: "TaskLike | None" = None) -> dict[str, Any] | None:
        """The per-call headers: the provenance token of the task this call is for.

        ``task`` when the caller named one, else whichever task is running. There
        is no per-task copy of this client: one instance serves every task, and
        what a request is attributed to is decided per call.
        """
        token = token_of(task)
        return {TASK_HEADER: token} if token else None

    def _apply_middlewares(
        self,
        variables: dict[str, Any],
        operation: type[TOperation],
        middlewares: list[OperationMiddleware],
    ) -> dict[str, Any]:
        """Apply the middleware chain to the serialized variables (sync path).

        Each middleware processes the variables in order using its sync
        ``process_variables`` method. This happens *after* pydantic
        serialization (model_dump) but *before* the operation is sent to rath.
        """
        for middleware in middlewares:
            variables = middleware.process_variables(variables, operation, self.rath)
        return variables

    async def _aapply_middlewares(
        self,
        variables: dict[str, Any],
        operation: type[TOperation],
        middlewares: list[OperationMiddleware],
    ) -> dict[str, Any]:
        """Apply the middleware chain to the serialized variables (async path).

        Each middleware processes the variables in order using its async
        ``aprocess_variables`` method.
        """
        for middleware in middlewares:
            variables = await middleware.aprocess_variables(variables, operation, self.rath)
        return variables

    def execute(
        self,
        operation: type[TOperation],
        variables: dict[str, Any],
        task: "TaskLike | None" = None,
    ) -> TOperation:
        """Executes a query or mutation in a blocking way.

        Uses the sync middleware path (process_variables) which runs
        uploads via obstore in the calling thread.
        """
        rath = self.rath

        # First serialize through operation.Arguments (pydantic validation + alias resolution)
        serialized = operation.Arguments(**variables).model_dump(by_alias=True, exclude_unset=True)

        # Apply sync middleware chain (e.g., upload arrays via obstore)
        serialized = self._apply_middlewares(serialized, operation, rath.middlewares)

        x = rath.query(operation.Meta.document, serialized, headers=self._headers(task))
        return operation.model_validate(x.data, context=self._origin())

    async def aexecute(
        self,
        operation: type[TOperation],
        variables: dict[str, Any],
        task: "TaskLike | None" = None,
    ) -> TOperation:
        """Executes a query or mutation in a non-blocking way.

        Uses the async middleware path (aprocess_variables) which runs
        uploads via obstore.
        """
        rath = self.rath

        # First serialize through operation.Arguments (pydantic validation + alias resolution)
        serialized = operation.Arguments(**variables).model_dump(by_alias=True, exclude_unset=True)

        # Apply async middleware chain (e.g., upload arrays via obstore)
        serialized = await self._aapply_middlewares(serialized, operation, rath.middlewares)

        x = await rath.aquery(operation.Meta.document, serialized, headers=self._headers(task))
        return operation.model_validate(x.data, context=self._origin())

    def subscribe(
        self,
        operation: type[TOperation],
        variables: dict[str, Any],
        task: "TaskLike | None" = None,
    ) -> Generator[TOperation, None, None]:
        """Subscribes to an operation in a blocking way."""
        return unkoil_gen(
            self.asubscribe,
            operation,
            variables,
            task=task if task is not None else current_task.get(),
        )

    async def asubscribe(
        self,
        operation: type[TOperation],
        variables: dict[str, Any],
        task: "TaskLike | None" = None,
    ) -> AsyncGenerator[TOperation, None]:
        """Subscribes to an operation in a non-blocking way.

        Uses the async middleware path (aprocess_variables).
        """
        rath = self.rath

        # First serialize through operation.Arguments (pydantic validation + alias
        # resolution). Unlike a query or mutation, unset variables are sent (as their
        # defaults): the subscription wire has always been serialized this way.
        serialized = operation.Arguments(**variables).model_dump(by_alias=True)

        # Apply async middleware chain
        serialized = await self._aapply_middlewares(serialized, operation, rath.middlewares)

        async for event in rath.asubscribe(
            operation.Meta.document, serialized, headers=self._headers(task)
        ):
            yield operation.model_validate(event.data, context=self._origin())

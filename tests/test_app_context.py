"""Which elektro client answers: the one a call is made on, or the one an object came from.

No server: the rath clients are fakes returning canned data. Every operation is a
method of the client, and the executor is handed that client; nothing is looked up
in what happens to be current. An object remembers the client that fetched it, so
what it fetches later goes through that client too.
"""

from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict

from elektro.elektro import TASK_HEADER
from elektro.client import client_of
from elektro.datalayer import DataLayer
from elektro.elektro import Elektro
from elektro.errors import NoDataLayerFound, NoElektroFound
from elektro.traits import ElektroFetchable, HasDownloadAccessor, HasZarrStoreAccessor


class FakeRath:
    """Answers every query with the same canned store, and remembers being asked."""

    middlewares: list[Any] = []

    def __init__(self, name: str) -> None:
        """Start uncalled."""
        self.name = name
        self.calls = 0
        self.headers: list[Any] = []
        self.variables: list[dict[str, Any]] = []

    def _answer(self, variables: dict[str, Any], headers: Any) -> SimpleNamespace:  # noqa: ANN401
        self.calls += 1
        self.headers.append(headers)
        self.variables.append(variables)
        return SimpleNamespace(data={"store": {"id": "store-1", "nested": {"id": "n-1"}}})

    def query(
        self, document: str, variables: dict[str, Any], headers: Any = None  # noqa: ANN401
    ) -> SimpleNamespace:
        """Answer in the blocking way."""
        return self._answer(variables, headers)

    async def aquery(
        self, document: str, variables: dict[str, Any], headers: Any = None  # noqa: ANN401
    ) -> SimpleNamespace:
        """Answer in the non-blocking way."""
        return self._answer(variables, headers)

    async def asubscribe(
        self, document: str, variables: dict[str, Any], headers: Any = None  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Answer one event."""
        yield self._answer(variables, headers)


class FakeApp:
    """An app as elektro sees one: something holding an elektro client."""

    def __init__(self, name: str) -> None:
        """Build the fake client and a datalayer of its own."""
        self.name = name
        self.rath = FakeRath(name)
        self.datalayer = DataLayer(endpoint_url=f"http://{name}.invalid")
        # A real client over fakes: `client_of` only follows an origin that is one.
        self.elektro = Elektro.model_construct(
            rath=self.rath, datalayer=self.datalayer, task_token=None
        )

    def get(self, key: type) -> Any:  # noqa: ANN401
        """Answer for the elektro client, and for nothing else."""
        return self.elektro if key is Elektro else None




class Nested(HasZarrStoreAccessor):
    """An inline selection: all it has is an accessor trait, as the generated stores do."""

    model_config = ConfigDict(frozen=True)
    id: str


class Store(HasZarrStoreAccessor, ElektroFetchable, BaseModel):
    """Shaped like a generated store fragment."""

    model_config = ConfigDict(frozen=True)
    id: str
    nested: Nested


class GetStore(BaseModel):
    """Shaped like a generated operation."""

    store: Store

    class Arguments(BaseModel):
        """The variables of the operation."""

        id: str
        limit: int | None = None

    class Meta:
        """The document of the operation."""

        document = "query GetStore($id: ID!) { store(id: $id) { id nested { id } } }"


@pytest.fixture()
def apps() -> tuple[FakeApp, FakeApp]:
    """Two apps that could answer for each other."""
    return FakeApp("a"), FakeApp("b")


# --------------------------------------------------------------------------- #
# Calls, and what they return
# --------------------------------------------------------------------------- #


def test_execute_goes_through_the_client_it_is_handed(apps: tuple[FakeApp, FakeApp]) -> None:
    """What is current plays no part: the client is an argument."""
    a, b = apps

    result = a.elektro.execute(GetStore, {"id": "store-1"})

    assert (a.rath.calls, b.rath.calls) == (1, 0)
    assert result.store.bound_client() is a.elektro
    assert result.store.bound_rath() is a.rath


@pytest.mark.asyncio
async def test_aexecute_remembers_the_client_and_its_datalayer(
    apps: tuple[FakeApp, FakeApp],
) -> None:
    """The client is remembered, and with it its rath and datalayer, down to nested objects."""
    from rath.origin import get_origin

    a, b = apps

    result = await a.elektro.aexecute(GetStore, {"id": "store-1"})

    assert (a.rath.calls, b.rath.calls) == (1, 0)
    origin = get_origin(result.store.nested)
    assert origin is not None and origin.client is a.elektro
    assert origin.rath is a.rath and origin.clients["datalayer"] is a.datalayer


@pytest.mark.asyncio
async def test_unset_variables_stay_off_the_wire_of_a_query_but_not_a_subscription(
    apps: tuple[FakeApp, FakeApp],
) -> None:
    """The serialization each path always had: queries leave the server its defaults."""
    a, _ = apps

    await a.elektro.aexecute(GetStore, {"id": "store-1"})
    async for _ in a.elektro.asubscribe(GetStore, {"id": "store-1"}):
        pass

    assert a.rath.variables == [{"id": "store-1"}, {"id": "store-1", "limit": None}]


def test_the_generated_operations_are_methods_of_the_client() -> None:
    """``ElektroApi`` is mixed in: the client's own fields do not shadow an operation."""
    from elektro.api.schema import ElektroApi

    assert issubclass(Elektro, ElektroApi)
    assert callable(Elektro.aget_lens) and callable(Elektro.get_lens)
    assert set(Elektro.model_fields) == {"datalayer", "rath", "task_token"}


# --------------------------------------------------------------------------- #
# What an object fetches later
# --------------------------------------------------------------------------- #


@pytest.fixture()
def opened(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Record which clients the zarr accessor reaches for, without any I/O."""
    seen: list[dict[str, Any]] = []

    def fake_unkoil(
        function: object, store_id: str, rath: object, datalayer: object
    ) -> tuple[SimpleNamespace, str]:
        seen.append({"store": store_id, "rath": rath, "datalayer": datalayer})
        return SimpleNamespace(), "http://endpoint.invalid"

    monkeypatch.setattr("elektro.io.download.unkoil", fake_unkoil)
    monkeypatch.setattr(
        "elektro.io.download.create_zarr_store_path", lambda *args: "a-store-path"
    )
    return seen


def test_object_keeps_to_its_own_clients_while_another_app_is_current(
    apps: tuple[FakeApp, FakeApp], opened: list[dict[str, Any]]
) -> None:
    """The case that leaked: an object from app A touched while app B is current."""
    a, b = apps
    store = a.elektro.execute(GetStore, {"id": "store-1"}).store

    assert store.zarr_store == "a-store-path"
    assert store.nested.zarr_store == "a-store-path"

    assert [(seen["rath"], seen["datalayer"]) for seen in opened] == [
        (a.rath, a.datalayer),
        (a.rath, a.datalayer),
    ]


def test_an_object_fetched_through_no_client_says_so(
    apps: tuple[FakeApp, FakeApp], opened: list[dict[str, Any]]
) -> None:
    """Built by hand (or unpickled): there is no client to fall back to, current or not."""
    _, b = apps
    store = Store(id="store-1", nested=Nested(id="n-1"))

    with pytest.raises(NoElektroFound, match="not fetched through an Elektro client"):
        store.zarr_store
    with pytest.raises(NoElektroFound, match="elektro=..."):
        client_of(store)
    assert opened == []


def test_the_download_accessor_reads_through_its_objects_datalayer(
    apps: tuple[FakeApp, FakeApp], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The accessor passes ``obj=self`` down; the io function reads its origin, not the current app."""
    from elektro.io import download

    a, b = apps
    seen: dict[str, Any] = {}

    class Big(HasDownloadAccessor):
        id: str
        key: str

    def fake_download(store_id: str, file_name: str, **kwargs: object) -> str:
        seen.update(kwargs)
        return file_name

    monkeypatch.setattr("elektro.io.download.download_file", fake_download)
    big = Big.model_validate({"id": "1", "key": "file.bin"}, context=a.elektro._origin())

    assert big.download() == "file.bin"

    assert seen["obj"] is big
    assert download._clients(None, None, seen["obj"]) == (a.rath, a.datalayer)
    with pytest.raises(NoDataLayerFound):
        download._datalayer(None, Big(id="2", key="x"))


def test_client_of_prefers_the_client_passed(apps: tuple[FakeApp, FakeApp]) -> None:
    """``elektro=`` on a trait method wins over the client the object came from."""
    a, b = apps
    store = a.elektro.execute(GetStore, {"id": "store-1"}).store

    assert client_of(store) is a.elektro
    assert client_of(store, b.elektro) is b.elektro


# --------------------------------------------------------------------------- #
# Fetching by id (rath's federation contract)
# --------------------------------------------------------------------------- #


def test_what_is_fetched_by_id_is_bound_to_the_client_too(
    apps: tuple[FakeApp, FakeApp],
) -> None:
    """An object expanded through ``_entities`` is as capable as one a query returned."""
    from rath.origin import ORIGIN_KEY

    a, _ = apps

    origin = Store.fetch_origin(a.elektro)[ORIGIN_KEY]

    assert origin.client is a.elektro and origin.rath is a.rath
    assert origin.clients == {"datalayer": a.datalayer}


# --------------------------------------------------------------------------- #
# The service answers for itself
# --------------------------------------------------------------------------- #


def test_the_client_has_exactly_its_fields() -> None:
    """A real composition over a link that needs no server."""
    from rath.links.testing.direct_succeeding_link import DirectSucceedingLink

    from elektro.rath import ElektroRath

    service = Elektro(
        rath=ElektroRath(link=DirectSucceedingLink()),
        datalayer=DataLayer(endpoint_url="self"),
    )



# --------------------------------------------------------------------------- #
# Through rekuest: an argument is expanded through the client its registry is bound to
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_rekuest_expands_through_the_client_its_registry_was_bound_to(
    apps: tuple[FakeApp, FakeApp], opened: list[dict[str, Any]]
) -> None:
    """The whole chain, as an actor drives it.

    The expander is handed the client the registry was bound to; B being current
    plays no part. The object then remembers that client, which is what keeps it on
    app A afterwards even though B is the only app current by then.
    """
    pytest.importorskip("rekuest.app")
    from typing import Annotated

    from fakts import Alias, Require
    from rath.origin import get_origin

    from rekuest.app import AppRegistry
    from rekuest.definition.define import prepare_definition
    from rekuest.structures.serialization.actor import expand_inputs

    a, b = apps

    async def aget_store(client: Elektro, id: str) -> Store:
        return (await client.aexecute(GetStore, {"id": id})).store

    class StoreClient:
        """The elektro client, as far as expanding the test store goes."""

        async def aget_store(self, id: str) -> Store:
            return await aget_store(a.elektro, id)

    def elektro(alias: Annotated[Alias, Require("live.test.elektro")]) -> StoreClient:
        """A parameter is only a client once a registered service returns its type."""
        return StoreClient()

    async def expand_store(id: str, elektro: StoreClient) -> Store:
        """The expander names the client it needs; binding supplies it."""
        return await elektro.aget_store(id)

    app_registry = AppRegistry()
    app_registry.service()(elektro)
    app_registry.structure("@elektro/teststore")(expand_store)
    bound = app_registry.structure_registry.bound({"elektro": StoreClient()})

    def uses_store(store: Store) -> str:
        """Takes a store."""
        return store.id

    definition = prepare_definition(uses_store, structure_registry=bound)
    wire = {"store": {"__identifier": "@elektro/teststore", "object": "store-1"}}

    expanded = await expand_inputs(
        definition, wire, structure_registry=bound, shelver=None  # type: ignore[arg-type]
    )
    store = expanded["store"]
    store.zarr_store  # touched while the OTHER app is current

    assert (a.rath.calls, b.rath.calls) == (1, 0)
    assert (opened[0]["rath"], opened[0]["datalayer"]) == (a.rath, a.datalayer)
    origin = get_origin(store)
    assert origin is not None and origin.client is a.elektro


# --------------------------------------------------------------------------- #
# A per-task view
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_a_task_view_stamps_its_token_and_shares_the_clients() -> None:
    """Requests from the view name the task; the shared client is never changed."""
    rath = FakeRath("shared")
    client = Elektro.model_construct(
        rath=rath, datalayer=DataLayer(endpoint_url="http://x.invalid"), task_token=None
    )
    view = client.for_task(SimpleNamespace(token="token-1"))

    await client.aexecute(GetStore, {"id": "store-1"})
    result = await view.aexecute(GetStore, {"id": "store-1"})

    assert rath.headers == [None, {TASK_HEADER: "token-1"}]
    assert view.rath is client.rath and view.datalayer is client.datalayer
    assert client.task_token is None
    assert result.store.bound_client() is view


@pytest.mark.asyncio
async def test_the_ambient_task_is_stamped_without_a_view() -> None:
    """One shared client attributes each call to whatever task is running."""
    from rath.task import task_scope

    rath = FakeRath("shared")
    client = Elektro.model_construct(
        rath=rath, datalayer=DataLayer(endpoint_url="http://x.invalid"), task_token=None
    )

    await client.aexecute(GetStore, {"id": "store-1"})
    with task_scope(SimpleNamespace(token="token-1")):
        await client.aexecute(GetStore, {"id": "store-1"})
    await client.aexecute(GetStore, {"id": "store-1"})

    assert rath.headers == [None, {TASK_HEADER: "token-1"}, None]
    assert client.task_token is None, "the shared client is never changed"


@pytest.mark.asyncio
async def test_a_task_named_at_the_call_beats_the_ambient_one() -> None:
    from rath.task import task_scope

    rath = FakeRath("shared")
    client = Elektro.model_construct(
        rath=rath, datalayer=DataLayer(endpoint_url="http://x.invalid"), task_token=None
    )

    with task_scope(SimpleNamespace(token="ambient")):
        await client.aexecute(
            GetStore, {"id": "store-1"}, task=SimpleNamespace(token="explicit")
        )

    assert rath.headers == [{TASK_HEADER: "explicit"}]

# elektro

[![PyPI version](https://badge.fury.io/py/elektro.svg)](https://pypi.org/project/elektro/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/elektro/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/elektro.svg)](https://pypi.python.org/pypi/elektro/)
[![PyPI status](https://img.shields.io/pypi/status/elektro.svg)](https://pypi.python.org/pypi/elektro/)
[![PyPI download month](https://img.shields.io/pypi/dm/elektro.svg)](https://pypi.python.org/pypi/elektro/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/jhnnsrs/elektro)

## What is Elektro?

Elektro is the Python client for the **Elektro electrophysiology backend** — a service for
storing, organizing and analysing ephys data (traces, recordings, stimuli, experiments) and
the biophysical neuron models behind them.

It splits every object into two halves and keeps them in sync for you: the **metadata**
(a trace's name, its dataset, the experiment it belongs to) lives in a GraphQL API, while the
**heavy numeric payload** (the actual signal, arrays, tables, meshes) is streamed to and from
object storage as [Zarr](https://zarr.dev/) and [Parquet](https://parquet.apache.org/). You
hand Elektro a NumPy array; it uploads the bytes, registers the metadata, and gives you back a
typed object whose `.data` is a **lazy** [`xarray.DataArray`](https://docs.xarray.dev/) — so
you can ask for `trace.data.max()` on a multi-gigabyte recording and only the bytes you touch
are ever pulled down.

It answers questions like *"store this recording and give it back to me as an array I can slice
without downloading the whole thing"* — and does it as one line of typed, async-first Python.

> **Note:** Elektro is built for the [Arkitekt](https://arkitekt.live) ecosystem. Configuration
> and authentication come from [Fakts](https://github.com/jhnnsrs/fakts), the transport from
> [Rath](https://github.com/jhnnsrs/rath), and its domain types plug straight into
> [Rekuest](https://github.com/jhnnsrs/rekuest-next) workflows.

## Installation

```bash
pip install elektro
```

Elektro requires **Python ≥ 3.11**. Two optional extras pull in heavier, domain-specific
dependencies only when you need them:

```bash
pip install "elektro[table]"   # pyarrow + pandas + duckdb — query Parquet stores
pip install "elektro[neuron]"  # the NEURON simulator — build & run biophysical models
```

## Scope

Elektro is responsible for the **client side** of ephys data and nothing else:

1. **Modelling** — it exposes the Elektro domain (traces, datasets, experiments, simulations,
   neuron models, …) as typed, validated Python objects generated from the GraphQL schema.
2. **Moving data** — array-, table- and file-like values you pass into a mutation are
   transparently uploaded to object storage *before* the GraphQL call, and read back lazily
   afterwards. You work with NumPy/xarray; Elektro handles Zarr, Parquet and credentials.
3. **Composing** — it bundles a GraphQL client (`rath`) and an object-storage client
   (`datalayer`) into one `Elektro` app, usable sync or async.

It does **not** run the backend, define the schema, or mint your credentials — those come from
the Elektro server and from [Fakts](https://github.com/jhnnsrs/fakts) /
[Arkitekt](https://arkitekt.live). Elektro is the piece that turns a configured, authenticated
connection into typed objects and lazy arrays.

## Core concepts

The domain types you work with (all registered as Rekuest structures in `elektro/rekuest.py`):

| Type              | Meaning                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `Trace`           | A time-series recording — the signal itself, backed by a Zarr store.    |
| `Dataset`         | A named collection that groups traces and other objects.                |
| `Experiment`      | An experimental setup tying together recordings and stimuli.            |
| `Recording`       | A single recording of a trace within an experiment.                     |
| `Stimulus`        | A stimulus protocol applied during an experiment.                       |
| `Block`           | An organisational unit grouping recordings/stimuli in time.             |
| `Simulation`      | A run of a biophysical neuron model.                                    |
| `NeuronModel`     | A specific morphology + biophysics model.                               |
| `ModelCollection` | A library of related neuron models.                                     |
| `ROI`             | A region of interest on a trace.                                        |

Heavy payloads enter the API as **store-backed scalars** (`elektro/scalars.py`). You pass a
plain in-memory value; Elektro uploads it and substitutes a store reference:

| Scalar        | You pass…                          | Stored as…            |
|---------------|------------------------------------|-----------------------|
| `TraceLike`   | `np.ndarray` / `xr.DataArray`      | a Zarr store          |
| `ArrayLike`   | an N-dimensional array             | a Zarr store          |
| `ParquetLike` | a pandas / Arrow table             | a Parquet store       |
| `FileLike`    | a file path / handle               | a big-file store      |
| `MeshLike`    | a 3D mesh                          | a mesh store          |

## How it fits together

An `Elektro` app is a small composition of two clients (`elektro/elektro.py`):

```
        ┌──────────────────── Elektro ────────────────────┐
        │                                                  │
        │   rath: ElektroRath          datalayer: DataLayer│
        │   (GraphQL metadata)         (object storage)    │
        └───────┬──────────────────────────────┬──────────┘
                │                               │
   write path   │                               │
   from_trace_like(np.ndarray)                  │
                │                               │
        ┌───────▼────────┐   upload bytes   ┌───▼──────────────┐
        │ UploadMiddleware├─────────────────►│  Zarr / Parquet  │
        │ (intercepts the │                  │  object storage  │
        │  array variable)│◄─────────────────┤  (via obstore)   │
        └───────┬────────┘   store id        └───▲──────────────┘
                │                                 │
        ┌───────▼────────┐                        │  lazy reads
        │ GraphQL mutation│  carries store id      │
        │ via ElektroRath │                        │
        └───────┬────────┘                        │
                │                                  │
   read path    │  Trace                           │
        trace.data  ──── HasZarrStoreTrait ───────►│  xr.DataArray
                       (only the bytes you touch are pulled)
```

The write path: you call `from_trace_like(array, …)`; `UploadMiddleware`
(`elektro/middleware/upload.py`) pulls the array out of the variables, uploads it to a Zarr
store through the `datalayer`, and the GraphQL mutation only ever carries the resulting store
id. The read path: the returned `Trace` mixes in `HasZarrStoreTrait`, whose `.data` property
opens that Zarr store as a lazy `xarray.DataArray` — nothing is downloaded until you compute.

## Quickstart

In the Arkitekt ecosystem the app is built and entered for you, and the top-level schema
functions in `elektro.api.schema` operate against the current connection:

```python
import numpy as np
from elektro.api.schema import create_dataset, from_trace_like, get_random_trace
from arkitekt import easy

# Create a dataset (metadata only)
with easy():
        dataset = create_dataset(name="my_experiment")

        # Upload a 1-D signal — the array is stored in Zarr, the metadata in GraphQL
        trace = from_trace_like(
        np.random.random((1000,)),
        name="signal_1",
        dataset=dataset.id,
        )

        trace.id           # the new trace's id
        trace.data.shape   # (1000,) — a lazy xarray.DataArray, materialized on access

        # Fetch one back
        again = get_random_trace()
```

Every function has an `a`-prefixed async twin (`acreate_dataset`, `afrom_trace_like`,
`aget_random_trace`, …) for use inside an async context:

```python
dataset = await acreate_dataset(name="my_experiment")
trace = await afrom_trace_like(np.random.random((1000,)), name="signal_1", dataset=dataset.id)
```

> Outside Arkitekt you can construct the app yourself — `Elektro(rath=ElektroRath(...),
> datalayer=DataLayer(...))` — and use it as a context manager (`with elektro: ...`). See
> `tests/conftest.py` for a full manual wiring against a local deployment.

## Working with data

**Lazy arrays.** A `Trace` (and anything mixing in `HasZarrStoreTrait`) exposes its payload as
an `xarray.DataArray` that is only fetched on demand:

```python
data = trace.data                 # xr.DataArray (lazy, dask-backed)
peak = data.max().compute()       # pulls only what it needs
trace.multi_scale_data            # list[xr.DataArray] — the multiscale pyramid
trace.export_csv("signal.csv")    # dump the trace to CSV
```

**Tables.** Parquet-backed stores expose a queryable relation (requires `elektro[table]`):

```python
relation = store.duckdb_relation  # a duckdb.DuckDBPyRelation you can SQL against
df = store.parquet_dataset        # the underlying Parquet dataset
```

**Files & meshes.** Big-file and media stores download to disk on request:

```python
path = bigfile_store.download()              # → local file path
path = media_store.download("frame.png")     # presigned download
```

**Units.** Physical quantities are real [pint](https://pint.readthedocs.io/) quantities via
[`kanne`](https://github.com/jhnnsrs/kanne) (`Milliseconds`, `Micrometers`, `Microliters`,
…), coerced on the wire by `CoercePintLink` so the server always receives canonical units.

## Neuron modelling

Elektro models biophysical neurons as a typed hierarchy —
`ModelConfig` → `Cell` → `Topology` (sections & connections) → `Biophysics` (mechanisms &
conductances) → `Compartment`. The input traits (`elektro/traits.py`) make these easy to build
and inspect:

```python
config.as_input()            # ModelConfig → its GraphQL input form
biophysics.as_dataframe()    # inspect compartments/mechanisms as a pandas DataFrame
```

With the `elektro[neuron]` extra installed, `elektro/neuron/` parses NEURON `.mod` mechanism
files and runs simulations directly from a `ModelConfig`, recording the result as a
`Simulation`.

## In the Arkitekt ecosystem

- **`ElektroService`** (`elektro/arkitekt.py`) — registers Elektro as an Arkitekt service. It
  builds a fully wired `Elektro` app from a [Fakts](https://github.com/jhnnsrs/fakts) config
  (`FaktsAuthLink` for auth, `FaktsAIOHttpLink`/`FaktsGraphQLWSLink` for transport, a
  `FaktsDataLayer` for storage) so an Arkitekt app gets a ready-to-use client with no manual
  setup.
- **`structure_reg`** (`elektro/rekuest.py`) — registers the domain types (`Trace`, `Dataset`,
  `Experiment`, `Simulation`, …) as [Rekuest](https://github.com/jhnnsrs/rekuest-next)
  structures, each under an identifier like `@elektro/trace`, so they can be passed in and out
  of Rekuest workflow nodes (expand/shrink/search handled for you).

Under the hood the transport is [Rath](https://github.com/jhnnsrs/rath) (`ElektroRath`, a link
chain of file extraction, dicting, pint coercion, auth and an HTTP/WebSocket split), the
composition is [koil](https://github.com/jhnnsrs/koil), and object storage goes through
[obstore](https://github.com/developmentseed/obstore) + Zarr/Parquet.

## Public API

```python
from elektro import Elektro, ElektroService, structure_reg

# the building blocks of the app
from elektro.rath import ElektroRath
from elektro.datalayer import DataLayer

# the domain operations (turms-generated; sync + async `a*` twins)
from elektro.api.schema import (
    create_dataset,
    from_trace_like,
    get_random_trace,
    create_experiment,
    create_simulation,
    Trace,
    Dataset,
)
```

`elektro.api.schema` is generated from the GraphQL schema by
[turms](https://github.com/jhnnsrs/turms) and regenerated whenever the schema changes — it is
the source of truth for the full set of available operations and types.

## Development

```bash
uv sync
uv run pytest
```

Integration tests spin up a real Elektro + MinIO deployment with testcontainers and are marked
`@pytest.mark.integration`; tests needing the NEURON simulator are marked `@pytest.mark.neuron`.
Run just the fast suite with `uv run pytest -m "not integration and not neuron"`.

See [`RELEASING.md`](./RELEASING.md) for the semantic-release flow (`main` → stable,
`next` → `rc` prereleases, `N.x` → maintenance).

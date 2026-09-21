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
storing, organizing and analysing ephys data (signals, recordings, stimuli, experiments) and
the biophysical neuron models behind them.

It splits every object into two halves and keeps them in sync for you: the **metadata**
(a dataset's name, its folder, the experiment it belongs to) lives in a GraphQL API, while the
**heavy numeric payload** (the actual signal, arrays, tables, meshes) is streamed to and from
object storage as [Zarr](https://zarr.dev/) and [Parquet](https://parquet.apache.org/). You
hand Elektro a NumPy array; it uploads the bytes, registers the metadata, and gives you back a
typed object whose `.data` is a **lazy** [`xarray.DataArray`](https://docs.xarray.dev/) — so
you can ask for `dataset.data.max()` on a multi-gigabyte recording and only the bytes you touch
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

1. **Modelling** — it exposes the Elektro domain (array datasets, folders, experiments,
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

The domain types you work with (all registered as Rekuest structures in `elektro/arkitekt.py`, beside the service):

| Type              | Meaning                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `ArrayDataset`    | An array of samples living in one sample grid; its bytes are `DataArray` levels. |
| `DataArray`       | One pyramid level of a dataset — the Zarr store lives here.             |
| `CoordinateSystem`| A space: a dataset's sample grid, a clock, or an experiment's world.    |
| `Transformation`  | An edge between two spaces — a sampling law, an offset, a time lookup.  |
| `Lens`            | An immutable selection (in samples) over an array dataset.              |
| `TableDataset`    | Rows in a Parquet store: events/epochs (a TIME column), a sorter's units. |
| `SparseDataset`   | A sparse matrix — a spike raster `(unit: INDEX, t: TIME)`.              |
| `Folder`          | A named collection that files datasets and files.                       |
| `Experiment`      | mikro's scene for time: a world (a clock) and the layers drawn on it.   |
| `ExperimentLayer` | A view over data it does not own: `TRACE` (a lens), `SPIKES` (a raster), `EVENTS` (a table), `ANNOTATION`. |
| `NeuronModel`     | A specific morphology + biophysics model.                               |
| `ModelCollection` | A library of related neuron models.                                     |
| `Annotation`      | A mark (event, epoch, line, …) in an `AnnotationCollection`'s space.    |

Heavy payloads enter the API as **store-backed scalars** (`elektro/scalars.py`). You pass a
plain in-memory value; Elektro uploads it and substitutes a store reference:

| Scalar        | You pass…                          | Stored as…            |
|---------------|------------------------------------|-----------------------|
| `ArrayLike`   | `np.ndarray` / dask / `xr.DataArray`, any rank | a Zarr store |
| `ParquetLike` | a dict of columns / pandas / Arrow table / parquet path | a Parquet store |
| `SporadikLike`| `scipy.sparse` CSR and/or CSC (`elektro[sparse]`) | a sparse store |
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
   create_array_dataset(data=np.ndarray, …)     │
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
   read path    │  ArrayDataset                    │
      dataset.data  ──── DatasetTrait ───────────►│  xr.DataArray
                       (only the bytes you touch are pulled)
```

The write path: you call `create_array_dataset(data=array, …)`; `UploadMiddleware`
(`elektro/middleware/upload.py`) pulls every array out of the variables — the level-0 `data`
and each `scales` entry alike — uploads them to Zarr stores through the `datalayer`, and the
GraphQL mutation only ever carries the resulting store ids. The read path: the returned
`ArrayDataset` mixes in `DatasetTrait`, whose `.data` property opens **level 0's** store as a
lazy `xarray.DataArray` — nothing is downloaded until you compute. A store belongs to a
pyramid level, not to the dataset: `level_data(2)` and `multi_scale_data()` reach the rest.

## Quickstart

In the Arkitekt ecosystem the app is built and entered for you. Every GraphQL operation is a
method of the `Elektro` client it holds, so you take that client from the app and call through
it — nothing is looked up behind your back:

```python
import numpy as np
from arkitekt import App, connect
from elektro import Elektro

with connect(App("my-app", services=[Elektro])) as rt:
        elektro = rt.require(Elektro)

        # Create a folder (metadata only)
        folder = elektro.create_folder(name="my_experiment")

        # Upload a 1-D signal — the array is stored in Zarr, the metadata in GraphQL.
        # `axes` is required: an axis is what gives a dimension a type.
        dataset = elektro.create_array_dataset(
        data=np.random.random((1000,)),
        scales=[],
        name="signal_1",
        axes=["t"],
        folder=folder.id,
        )

        dataset.id           # the new dataset's id
        dataset.data.shape   # (1000,) — a lazy xarray.DataArray, materialized on access

        # Fetch one back
        again = elektro.get_array_dataset(dataset.id)
```

Every method has an `a`-prefixed async twin (`acreate_folder`, `acreate_array_dataset`,
`aget_array_dataset`, …) for use inside an async context:

```python
folder = await elektro.acreate_folder(name="my_experiment")
dataset = await elektro.acreate_array_dataset(
    data=np.random.random((1000,)), scales=[], name="signal_1", axes=["t"], folder=folder.id
)
```

> Outside Arkitekt you can construct the client yourself — `elektro = Elektro(rath=ElektroRath(...),
> datalayer=DataLayer(...))` — and use it as a context manager (`with elektro: ...`). See
> `tests/conftest.py` for a full manual wiring against a local deployment. An object a call
> returns remembers the client that fetched it, so its own follow-up calls (`dataset.data`,
> `system.graph()`, `dataset.lens(...)`) go through that client; trait methods that call the
> API also take an explicit `elektro=`.

## Working with data

**Lazy arrays.** An `ArrayDataset` (anything mixing in `DatasetTrait`) exposes its payload as
an `xarray.DataArray` that is only fetched on demand:

```python
data = dataset.data               # level 0, as a lazy dask-backed xr.DataArray
peak = data.max().compute()       # pulls only what it needs
overview = dataset.level_data(3)          # a coarser pyramid level, same axis names
dataset.multi_scale_data()                # every level, finest first
window = dataset.lens(t=(0, 30_000), c=2) # a Lens: an immutable selection, in samples
window.data                               # the sliced xr.DataArray
```

**Time lives in the graph, not in columns.** elektro uses the model
[mikro](https://github.com/jhnnsrs/mikro) uses for space, for time. A dataset lives in a
unit-less **sample grid**; physical time enters once, as a **clock** plus one edge — a
*sampling law* (`t = sample · period + t_start`) or, for irregular data, a *time lookup*.
Offsets between clocks are edges too, so nothing stores a composed answer:

```python
# CS first: the session is a clock, a signal is a dataset, the timing is one edge.
# What the values measure is a ValueUnit anchor, not an axis. Bare axis names cover
# the conventional ones ("t", "c", "sweep", ...).
clock = elektro.create_coordinate_system(
    name="session 12", registrations=[],
    axes=[PhysicalAxisInput(name="t", type=AxisType.TIME, unit="second")],
)
probe = elektro.create_array_dataset(
    data=np.zeros((90_000, 4)), scales=[], name="probe A", axes=["t", "c"],
    anchors=[CoordinateAnchorInput(axis_anchors=[], value_unit=ValueUnitInput(unit="uV"))],
)
# `source` is the grid being timed: a coordinate system id, never the dataset's own id.
# Passing the dataset *object* is fine -- it resolves to its grid client-side.
law = elektro.create_sampling_law(
    source=probe.intrinsic_system.id, clock=clock.id, sampling_rate="30 kHz", t_start="2 s",
)
law.as_matrix()                                  # [[1/30000, 0, 2], [0, 0, 1]]
probe.intrinsic_system.axis_values_in(clock, "t", 5)  # the first five sample times, in s
```

Declared axes are checked against the array *before* it is uploaded — a missing
declaration, a rank mismatch and a transposed `(c, t)` are all refused client-side, as the
server would refuse them afterwards.

**Marks.** An `AnnotationCollection` owns the space its shapes are drawn in; an edge says
what they mark (a dataset's samples, a segment's clock, an experiment's world):

```python
marks = elektro.create_annotation_collection(
    name="artifacts", axes=["t"],
    derived_from=[DatasetDerivedFromInput(dataset=probe.id, transform=IdentityTransformInput())],
)
elektro.create_annotation(kind=AnnotationKind.EPOCH, vectors=[[100.0], [250.0]], collection=marks.id)
```

**Experiments** are mikro's scenes for time: a world (usually a session clock) and layers
over data the experiment does not own. A layer carries view state only; where it sits in time
is the graph's answer, so there is no per-layer offset -- a segment's clock is placed once, with
`create_clock_offset`, and everything timed on it moves together.

```python
experiment = elektro.create_experiment_from_coordinate_system(coordinate_system=clock.id)
# ...or by hand, one layer per kind:
experiment = elektro.create_experiment(name="session 12", coordinate_system=clock.id)
elektro.create_trace_layer(experiment=experiment.id, dataset=probe.id, channel_index=2)
elektro.create_spikes_layer(experiment=experiment.id, sparse_dataset=raster.id,
                    color_bys=[ColorByInput(table=units.id, column="depth")])
elektro.create_events_layer(experiment=experiment.id, table_dataset=ttl.id, label_column="label")

experiment.data   # xr.Dataset: `traces` (trace, time), timed through the graph, world units
```

A session is a clock and the datasets timed onto it; `create_session` writes one sampling law
per dataset in one call (`time_unit` is required client-side -- the server's default is
seconds). A **simulated run is a session too**: there is no run object. Each output states what
computed it as a `simulation` spoke (`SimulationStateInput`: the neuron model, `dt`, `duration`)
beside its `RecordingSite` / `StimulusSite`, on the dataset's `{}` anchor; the server refuses
outputs of one clock that disagree on it. A model's runs read back as
`get_neuron_model_sessions(model.id).sessions` (clock + simulated datasets).

```python
clock = elektro.create_session(name="sweep 1", datasets=[v_soma.id, i_inj.id], time_unit="millisecond",
                       sampling=SamplingInput(rate="40 kHz", t_start="0 ms"))
```

**Spike rasters** are sparse datasets over `(unit, t)`: the unit axis identified by a units
table, the TIME axis by nothing (a sampling law places it). Declarations are checked against
the matrix before it is uploaded (`elektro/sparse.py`):

```python
raster = elektro.create_sparse_dataset(
    name="spikes", store=[spikes.tocsr(), spikes.tocsc()],
    axes=[SparseAxisInput(name="unit", identified_by=[TableIdentifiesInput(table=units.id)]),
          SparseAxisInput(name="t", type=AxisType.TIME)],
)
elektro.create_sampling_law(source=raster.coordinate_system.id, clock=clock.id,
                    sampling_rate="30 kHz", t_start="0 s")
```

**Tables.** `create_table_dataset` takes a dict of columns, a DataFrame, an Arrow table or a
parquet path; `columns` is partial -- the rest (names, DuckDB dtypes, order) is read off the
data. A table reads back as a lazy relation (requires `elektro[table]`):

```python
ttl = elektro.create_table_dataset(
    name="TTL", data={"t": onsets_s, "label": labels},
    columns=[ColumnInput(name="t", axis_type=AxisType.TIME, unit="second")],
)
ttl.data.df()                     # a duckdb relation over the parquet on S3, materialised
```

**Files & meshes.** Big-file and media stores download to disk on request:

```python
path = bigfile_store.download()              # → local file path
path = media_store.download("frame.png")     # presigned download
```

**Units.** Physical quantities are real [pint](https://pint.readthedocs.io/) quantities via
[`kanne`](https://github.com/jhnnsrs/kanne) (`Duration`, `Frequency`, `ElectricPotential`,
`Unit`, …), coerced on the wire by `CoercePintLink` so the server always receives canonical units.

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
files and runs simulations directly from a `ModelConfig`. `arun_simulation` publishes the run
as a session: each recorded array becomes its own `ArrayDataset` (recordings carry a
`simulation` spoke, stimuli -- the run's input -- only their site), then `create_session` times
them all onto one new clock with a sampling law. It returns a `PublishedRun` (`clock`,
`recordings`, `stimuli`), a client-side bundle, not a server object.

## In the Arkitekt ecosystem

- **`ElektroService`** (`elektro/arkitekt.py`) — registers Elektro as an Arkitekt service. It
  builds a fully wired `Elektro` app from a [Fakts](https://github.com/jhnnsrs/fakts) config
  (`FaktsAuthLink` for auth, `FaktsAIOHttpLink`/`FaktsGraphQLWSLink` for transport, a
  `FaktsDataLayer` for storage) so an Arkitekt app gets a ready-to-use client with no manual
  setup.
- **`structure_reg`** (`elektro/arkitekt.py`) — registers the domain types (`ArrayDataset`,
  `Folder`, `Experiment`, `NeuronModel`, …) as [Rekuest](https://github.com/jhnnsrs/rekuest-next)
  structures, each under an identifier like `@elektro/arraydataset`, so they can be passed in and out
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
    create_folder,
    create_array_dataset,
    get_array_dataset,
    create_experiment,
    create_session,
    ArrayDataset,
    Folder,
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

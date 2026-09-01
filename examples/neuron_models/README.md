# Neuron model examples

Small, runnable scripts that build **simple NEURON models** with the `elektro`
client and create them on an Elektro server. Each is a single self-contained


|                          | Create only            | Create **and** simulate            |
| ------------------------ | ---------------------- | ---------------------------------- |
| **Basic** (built-ins)    | `01_basic_model.py`    | `02_basic_model_simulate.py`       |
| **Custom `.mod`**        | `03_mod_model.py`      | `04_mod_model_simulate.py`         |

- **Basic** uses NEURON's built-in mechanisms (`pas`, `hh`) — no mechanism files
  to compile.
- **Custom `.mod`** registers the mechanism in [`mod_files/customleak.mod`](./mod_files/customleak.mod)
  (a passive leak channel `i = g * (v - e)`) as a `ModEnvironment`, then
  references it by its `SUFFIX` name, `"customleak"`.

## How a model is built

A model is a plain, validated Python object graph (all from `elektro.api.schema`):

```
ModelConfigInput
└── CellInput
    ├── TopologyInput  → SectionInput   (morphology: soma, dendrites, …)
    └── BiophysicsInput → CompartmentInput  (mechanisms + parameters)
```

Sections are matched to biophysics compartments by the section's `category`
(e.g. a `"soma"` section ↔ the `"soma"` compartment).

Physical quantities are **unit-bearing strings** — `"20 um"`, `"-65 mV"`,
`"0.001 S/cm2"`, `ElectricCurrent("0.1 nanoampere")`. This is the
[`kanne`](https://github.com/jhnnsrs) quantity protocol: `elektro` builds and
creates the model; `kanne` supplies and validates the quantities (a bare number
like `20` is rejected — 20 what?).

## Registering `.mod` files

The custom-mechanism scripts do this in three steps:

```python
zip_file, mechanisms = build_and_zip_environment("./mod_files")   # zip + parse
env = create_mod_environment(name="customleak-env",
                             zip_file=zip_file, mechanisms=mechanisms)  # upload + register
model = create_neuronmodel(name=..., config=..., environment=env.id)   # reference it
```

`build_and_zip_environment` parses each `.mod` file's `SUFFIX`/`PARAMETER` block
into a `MechanismInput`; `create_mod_environment` uploads the zip to object
storage and registers the mechanisms. There is also a one-shot convenience,
`create_mod_environment_from_directory(name=..., directory_path="./mod_files")`,
that folds those first two steps together.

> Note: the server requires **every** model to reference an environment — even
> the built-in-only case. The basic scripts therefore create a minimal,
> mechanism-free environment by zipping an empty directory.

## Connecting

All scripts connect through the Arkitekt ecosystem:

```python
from arkitekt import easy

with easy("neuron-model-examples"):
    ...
```

`easy()` resolves the Elektro service and authenticates you; the top-level
`create_*` functions then operate against that connection. A reachable Elektro
backend is required to actually run these.

## Running

```bash
# create-only examples
python 01_basic_model.py
python 03_mod_model.py

# create + simulate — these run NEURON locally, so install the extra first:
pip install "elektro[neuron]"
python 02_basic_model_simulate.py
python 04_mod_model_simulate.py
```

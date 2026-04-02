from elektro.api.schema import Simulation

import os
import json
import csv
import re
from typing import Any
import xarray as xr


def _sanitize_filename(s: str) -> str:
    """Make a filename-safe string."""
    if s is None:
        return ""
    # replace problematic characters with underscore
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s)


# helper to write a trace array together with time to CSV
def _write_trace_csv(time: xr.DataArray, data: xr.DataArray, path: str) -> None:
    # Ensure 1D/2D shape handling
    data = data.to_numpy()
    time = time.to_numpy()
    if data.ndim == 0:
        data = data.reshape((1,))
    if data.ndim == 1:
        ncols = 1
        data = data.reshape((-1, 1))
    else:
        ncols = data.shape[1]

    header = ["time"] + [f"value{i}" for i in range(ncols)]

    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        for i in range(len(time)):
            row = [time[i]] + data[i].tolist()
            writer.writerow(row)


def export_simulation(simulation: Simulation, to_folder: str) -> None:
    """Export traces from `simulation` to CSV files and metadata to JSON.

    Behavior:
    - For each `recording` write a CSV named `<cell>-<trace-name>.record.csv`.
    - For each `stimulus` write a CSV named `<cell>-<trace-name>.stim.csv`.
    - Write the full simulation metadata as `simulation_metadata.json`.

    The `to_file` parameter is treated as a directory path. The directory will
    be created if it does not exist.
    """
    out_dir = to_folder
    os.makedirs(out_dir, exist_ok=True)

    time_trace_array = simulation.time_trace.data

    # export recordings
    for rec in simulation.recordings:
        cell = rec.cell
        position = rec.position
        location = rec.location
        arr = rec.trace.data

        fname = f"{cell}-{location}-{position}.record.csv"
        fname = _sanitize_filename(fname)
        path = os.path.join(out_dir, fname)
        _write_trace_csv(time_trace_array, arr, path)
        print(f"Wrote recording CSV: {path}")

    # export stimuli
    for stim in getattr(simulation, "stimuli", []) or []:
        cell = stim.cell
        position = stim.position
        location = stim.location
        arr = stim.trace.data

        fname = f"{cell}-{location}-{position}.stim.csv"
        fname = _sanitize_filename(fname)
        path = os.path.join(out_dir, fname)
        _write_trace_csv(time_trace_array, arr, path)
        print(f"Wrote recording CSV: {path}")

    meta = simulation.model_dump(by_alias=True, exclude_none=True)
    meta_path = os.path.join(out_dir, "simulation_metadata.json")
    with open(meta_path, "w") as fh:
        json.dump(meta, fh, indent=2)

    print(f"Wrote simulation metadata: {meta_path}")

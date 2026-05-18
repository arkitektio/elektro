from ast import mod
import asyncio
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
from dataclasses import dataclass
import time
import numpy as np
import logging
import uuid
import os
import platform
import subprocess
import zipfile
from pathlib import Path
from filelock import FileLock, Timeout
from typing import Any, Dict, List, Optional, Literal, Union
from pydantic import BaseModel, Field

from elektro.api.schema import (
    ModEnvironment,
    NeuronModelConfig,
    Cell,
    ExpTwoSynapse,
    Simulation,
    SynapticConnection,
    RecordingInput,
    StimulusInput,
    StimulusKind,
    RecordingKind,
    NeuronModel,
    acreate_simulation,
)

from kanne.scalars import Ampere, Hertz, Millisecond, MillisecondCoercible, PintQuantity
from rath.scalars import ID
from collections import defaultdict

logger = logging.getLogger(__name__)

# Track loaded DLLs per worker process to prevent NEURON namespace collisions
_LOADED_DLLS = set()

# --------------------------------------------------------
# ASYNC CACHING AND COMPILATION LAYER
# --------------------------------------------------------


def _extract_zip(zip_path: Path, extract_dir: Path):
    """Synchronous zip extraction to be run in a thread."""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)


async def aensure_compiled_mechanisms(
    environment: ModEnvironment, base_cache_dir: str = "/tmp/neuron_cache"
):
    """
    PHASE 1: Natively async mechanism compiler.
    Downloads the single ModEnvironment zip, extracts it, and compiles it.
    Uses a non-blocking FileLock to prevent OS-level race conditions.
    """
    if not environment:
        return

    os.makedirs(base_cache_dir, exist_ok=True)
    machine = platform.machine()
    is_windows = platform.system() == "Windows"

    # Use the environment's unique ID to isolate its cache directory
    env_hash = str(environment.id)
    cache_dir = Path(base_cache_dir) / env_hash
    lock_path = Path(base_cache_dir) / f"{env_hash}.lock"

    if is_windows:
        dll_path = cache_dir / "nrnmech.dll"
    else:
        ext = "dylib" if platform.system() == "Darwin" else "so"
        dll_path = cache_dir / machine / f"libnrnmech.{ext}"

    # 1. Non-blocking Async File Lock
    lock = FileLock(str(lock_path))
    while True:
        try:
            lock.acquire(timeout=0)
            break
        except Timeout:
            # Yield control to the event loop so the server doesn't freeze
            await asyncio.sleep(0.5)

    try:
        # 2. Check Cache
        if not dll_path.exists():
            logger.info(
                f"Cache miss for environment {env_hash}. Downloading asynchronously..."
            )
            cache_dir.mkdir(parents=True, exist_ok=True)
            zip_path = cache_dir / "mechanisms.zip"

            # 3. Async S3 Download of the ENTIRE environment zip
            await environment.store.adownload(file_name=str(zip_path))

            # 4. Offload sync zip extraction to thread
            await asyncio.to_thread(_extract_zip, zip_path, cache_dir)

            # 5. Async Subprocess for C-Compilation
            logger.info(f"Compiling environment {env_hash} using async subprocess...")
            process = await asyncio.create_subprocess_exec(
                "nrnivmodl",
                cwd=str(cache_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"Compilation failed for {env_hash}:\n{stderr.decode()}")
                raise ValueError(f"Failed to compile environment {env_hash}.")

            logger.info(f"Successfully compiled environment {env_hash}.")
        else:
            logger.debug(f"Cache hit for environment {env_hash}. Skipping compilation.")

    finally:
        # Always release the lock
        lock.release()


def load_compiled_mechanisms(
    h: Any, environment: ModEnvironment, base_cache_dir: str = "/tmp/neuron_cache"
):
    """
    PHASE 2: Synchronous loader.
    Runs strictly inside the ProcessPool worker to inject the single C-library into its memory space.
    """
    global _LOADED_DLLS
    if not environment:
        return

    machine = platform.machine()
    is_windows = platform.system() == "Windows"
    env_hash = str(environment.id)
    cache_dir = Path(base_cache_dir) / env_hash

    if is_windows:
        dll_path = cache_dir / "nrnmech.dll"
    else:
        ext = "dylib" if platform.system() == "Darwin" else "so"
        dll_path = cache_dir / machine / f"libnrnmech.{ext}"

    if not dll_path.exists():
        raise FileNotFoundError(
            f"DLL not found at {dll_path}. Async compilation step must have failed."
        )

    str_dll_path = str(dll_path)

    # Check if this worker process has already loaded this exact DLL
    if str_dll_path in _LOADED_DLLS:
        logger.debug(f"DLL already loaded in this worker process: {str_dll_path}")
        return

    logger.debug(f"Loading environment library: {str_dll_path}")
    h.nrn_load_dll(str_dll_path)
    _LOADED_DLLS.add(str_dll_path)


class RecordBase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    cell: str
    location: str
    position: float = 0.5
    kind: Literal[RecordingKind.VOLTAGE, RecordingKind.CURRENT] = RecordingKind.VOLTAGE


class VRecord(RecordBase):
    kind: Literal[RecordingKind.VOLTAGE] = RecordingKind.VOLTAGE  # type: ignore[assignment]


class StimulusBase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    kind: StimulusKind
    cell: str
    location: str
    position: float = 0.5
    duration: Millisecond | None = None


class CurrentClampStimulus(StimulusBase):
    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    delay: Millisecond = Millisecond(100.0)
    amp: Ampere = Ampere(0.1, "nanoampere")


class WhiteNoiseStimulus(StimulusBase):
    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    noise_level: Ampere = Ampere(0.05, "nanoampere")


class SineWaveStimulus(StimulusBase):
    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    frequency: Hertz = Hertz(10.0)
    amplitude: Ampere = Ampere(0.1, "nanoampere")


def instantiate_cell(h: Any, cell: Cell):
    h_sections: Dict[str, Any] = {}

    for sec_def in cell.topology.sections:
        sec = h.Section(name=f"{cell.id}_{sec_def.id}")
        sec.nseg = sec_def.nseg
        sec.diam = sec_def.diam
        h_sections[sec_def.id] = sec

        if sec_def.coords is not None:
            h.pt3dclear(sec=sec)
            for pt in sec_def.coords:
                h.pt3dadd(pt.x, pt.y, pt.z, sec_def.diam, sec=sec)
        elif sec_def.length is not None:
            sec.L = sec_def.length
        else:
            raise ValueError(
                "Either coords or length must be provided for section geometry"
            )

    for sec_def in cell.topology.sections:
        for conn in sec_def.connections:
            parent = h_sections[conn.parent]
            child = h_sections[sec_def.id]
            child.connect(parent(conn.location))

    for sec_def in cell.topology.sections:
        sec = h_sections[sec_def.id]
        comp = cell.biophysics.compartment_for_id(sec_def.category)
        assert comp, f"Compartment {sec_def.category} not found."

        for mechanism in comp.mechanisms:
            try:
                sec.insert(mechanism)
            except Exception as e:
                raise ValueError(
                    f"Failed add mechanism {mechanism} to section {sec_def.id}"
                ) from e

        for param in comp.section_params:
            assert param.mechanism in comp.mechanisms
            value = param.value
            for seg in sec.allseg():
                try:
                    setattr(sec, param.param, value)
                except Exception as e:
                    raise ValueError(f"Failed to set parameter {param.param}") from e

        for gparam in comp.global_params:
            try:
                setattr(sec, gparam.param, gparam.value)
            except Exception as e:
                raise ValueError(
                    f"Failed to set global parameter {gparam.param}"
                ) from e

    return h_sections


@dataclass
class NeuronModelInstance:
    h: object
    cell_h_sections: Dict[str, Dict[str, Any]]
    net_stimulations: Dict[str, Any]
    net_connections: Dict[str, Any]
    net_synapses: Dict[str, Any]


@dataclass
class SimulationResults:
    time_trace: np.ndarray[Any, Any]
    recordings: List[RecordingInput]
    stimuli: List[StimulusInput]
    model: NeuronModel
    duration: Millisecond
    dt: Millisecond
    name: str
    raw_results: dict[str, Any] | None = None
    raw_stimulations: dict[str, Any] | None = None


def instantiate_model(h: Any, model: NeuronModelConfig):
    cell_h_sections: Dict[str, Dict[str, Any]] = {}
    net_stimulations: Dict[str, Any] = {}
    net_connections: Dict[str, Any] = {}
    net_synapses: Dict[str, Any] = {}

    for cell in model.cells:
        cell_h_sections[cell.id] = instantiate_cell(h, cell)

    h.define_shape()

    if model.net_synapses:
        for synapse in model.net_synapses:
            if isinstance(synapse, ExpTwoSynapse):
                hsec = cell_h_sections[synapse.cell][synapse.location]
                hsyn = h.Exp2Syn(hsec(synapse.position))
                hsyn.tau1 = synapse.tau1
                hsyn.tau2 = synapse.tau2
                hsyn.e = synapse.e
                net_synapses[synapse.id] = hsyn

    if model.net_stimulators:
        for net_stim in model.net_stimulators:
            hnet_stim = h.NetStim()
            hnet_stim.number = net_stim.number
            hnet_stim.start = net_stim.start
            if net_stim.interval is not None:
                hnet_stim.interval = net_stim.interval
            net_stimulations[net_stim.id] = hnet_stim

    if model.net_connections:
        for net_conn in model.net_connections:
            if isinstance(net_conn, SynapticConnection):
                hnet_syn = net_synapses[net_conn.synapse]
                hnet_stim = net_stimulations[net_conn.net_stimulator]
                hnet_conn = h.NetCon(hnet_stim, hnet_syn)
                hnet_conn.weight[0] = net_conn.weight
                if net_conn.delay is not None:
                    hnet_conn.delay = net_conn.delay
                if net_conn.threshold is not None:
                    hnet_conn.threshold = net_conn.threshold
                net_connections[net_conn.id] = hnet_conn

    return NeuronModelInstance(
        h=h,
        cell_h_sections=cell_h_sections,
        net_stimulations=net_stimulations,
        net_connections=net_connections,
        net_synapses=net_synapses,
    )


def run_simulation_processed(
    model: NeuronModel,
    duration: Millisecond,
    stims: List[Union[CurrentClampStimulus, SineWaveStimulus, WhiteNoiseStimulus]],
    records: List[Union[VRecord]],
    name: str,
    dt: Millisecond,
) -> SimulationResults:
    from neuron import h
    import numpy as np
    from collections import defaultdict

    h.load_file("stdrun.hoc")

    # --------------------------------------------------------
    # Execute Phase 2: Load DLLs into Worker Memory
    # --------------------------------------------------------
    if model.environment:
        load_compiled_mechanisms(h, model.environment)

    hmodel = instantiate_model(h, model.config)

    # 1. Validate units
    dt_obj = Millisecond.validate(dt)
    dt_ms = dt_obj.to("millisecond").magnitude
    requested_duration = Millisecond.validate(duration).to("millisecond").magnitude

    # 2. SNAP TO GRID
    n_steps = int(round(requested_duration / dt_ms))
    actual_dur_ms = n_steps * dt_ms

    # 3. Configure NEURON with the ALIGNED values
    h.dt = dt_ms
    h.tstop = actual_dur_ms
    h.CVode().active(0)
    h.steps_per_ms = 1.0 / h.dt

    h.v_init = model.config.v_init
    h.celsius = model.config.celsius
    h.finitialize(model.config.v_init)
    h.fcurrent()
    h.setdt()
    h.init()

    # 4. Create Precise Time Vector
    times = np.linspace(0, actual_dur_ms, n_steps + 1)
    t_vec_play = h.Vector(times)

    # 5. Group Stimuli
    grouped: dict[tuple[str, str, float], list] = defaultdict(list)
    for stim in stims:
        key = (stim.cell, stim.location, stim.position)
        grouped[key].append(stim)

    # 6. Build Waveforms
    refs = []
    input_waveforms = {}

    for key, stim_list in grouped.items():
        cell, loc, pos = key
        sec = hmodel.cell_h_sections[cell][loc]

        iclamp = h.IClamp(sec(pos))
        iclamp.delay = 0
        iclamp.dur = 1e9

        combined = np.zeros_like(times, dtype=np.float64)

        for stim_param in stim_list:
            if isinstance(stim_param, CurrentClampStimulus):
                delay = stim_param.delay.to("millisecond").magnitude
                d = (
                    stim_param.duration.to("millisecond").magnitude
                    if stim_param.duration
                    else actual_dur_ms
                )
                amp = stim_param.amp.to("nanoampere").magnitude

                mask = (times >= delay) & (times < (delay + d))
                combined[mask] += amp

            elif isinstance(stim_param, SineWaveStimulus):
                A = stim_param.amplitude.to("nanoampere").magnitude
                f = stim_param.frequency.to("hertz").magnitude
                combined += A * np.sin(2 * np.pi * f * (times / 1000.0))

            elif isinstance(stim_param, WhiteNoiseStimulus):
                sigma = stim_param.noise_level.to("nanoampere").magnitude
                combined += np.random.normal(0, sigma, size=len(times))

        i_vec = h.Vector(combined)
        i_vec.play(iclamp._ref_amp, t_vec_play, True)

        refs.append((iclamp, i_vec, t_vec_play))
        input_waveforms[key] = combined

    # 7. Prepare Recordings
    rec_t = h.Vector().record(h._ref_t)

    raw_results = {}
    for rec in records:
        sec = hmodel.cell_h_sections[rec.cell][rec.location]
        v_vec = h.Vector().record(sec(rec.position)._ref_v)
        raw_results[rec.id] = v_vec

    # 8. Run
    h.stdinit()
    h.dt = dt_ms
    h.steps_per_ms = 1.0 / dt_ms
    h.continuerun(actual_dur_ms)

    # 9. Process Outputs
    time_trace = rec_t.as_numpy().copy()

    recordings_out = []
    for rec in records:
        trace = raw_results[rec.id].as_numpy().copy()
        recordings_out.append(
            RecordingInput(
                cell=ID.validate(rec.cell),
                location=ID.validate(rec.location),
                kind=rec.kind,
                position=rec.position,
                trace=trace,
            )
        )

    stimuli_out = []
    for key, waveform in input_waveforms.items():
        cell, loc, pos = key
        if len(waveform) != len(time_trace):
            final_wave = np.interp(time_trace, times, waveform)
        else:
            final_wave = waveform

        stimuli_out.append(
            StimulusInput(
                cell=ID.validate(cell),
                location=ID.validate(loc),
                kind=StimulusKind.CURRENT,
                position=pos,
                trace=final_wave,
            )
        )

    return SimulationResults(
        time_trace=time_trace,
        recordings=recordings_out,
        stimuli=stimuli_out,
        model=model,
        duration=Millisecond(actual_dur_ms, "millisecond"),
        dt=dt_obj,
        name=name or f"Simulation for {model.name}",
        raw_results={},
        raw_stimulations={},
    )


def _get_isolated_pool() -> ProcessPoolExecutor:
    """Helper to generate a clean process pool that forces worker recycling."""
    # max_tasks_per_child=1 ensures a completely fresh NEURON memory space for every task
    return ProcessPoolExecutor(
        max_workers=1, mp_context=mp.get_context("spawn"), max_tasks_per_child=1
    )


async def asimulate(
    model: NeuronModel,
    duration: MillisecondCoercible,
    stims: List[Union[CurrentClampStimulus]],  # type: ignore[no-untyped-call]
    records: List[Union[VRecord]],  # type: ignore[no-untyped-call]
    name: str | None = None,
    dt: MillisecondCoercible = 1,
    process_pool: ProcessPoolExecutor | None = None,
) -> SimulationResults:
    """
    Asynchronously run a simulation in a separate process and return raw SimulationResults.
    """

    if process_pool is None:
        process_pool = _get_isolated_pool()

    loop = asyncio.get_event_loop()

    if not name:
        name = f"Simulation for {model.name}"

    # --------------------------------------------------------
    # Execute Phase 1: Async Download & Compile
    # --------------------------------------------------------
    if model.environment:
        await aensure_compiled_mechanisms(model.environment)

    future = loop.run_in_executor(
        process_pool,
        run_simulation_processed,
        model,
        duration,
        stims,
        records,
        name,
        dt,
    )
    result = await future
    return result


async def arun_simulation(
    model: NeuronModel,
    duration: MillisecondCoercible,
    stims: List[Union[CurrentClampStimulus]],  # type: ignore[no-untyped-call]
    records: List[Union[VRecord]],  # type: ignore[no-untyped-call]
    name: str | None = None,
    dt: MillisecondCoercible = 0.05,
    process_pool: ProcessPoolExecutor | None = None,
) -> Simulation:
    """
    Run a simulation asynchronously and publish results as a `Simulation` API object.
    """

    if process_pool is None:
        process_pool = _get_isolated_pool()

    loop = asyncio.get_event_loop()

    if not name:
        name = f"Simulation for {model.name}"

    # --------------------------------------------------------
    # Execute Phase 1: Async Download & Compile
    # --------------------------------------------------------
    if model.environment:
        await aensure_compiled_mechanisms(model.environment)

    future = loop.run_in_executor(
        process_pool,
        run_simulation_processed,
        model,
        duration,
        stims,
        records,
        name,
        dt,
    )

    result = await future

    return await acreate_simulation(
        name=result.name,
        duration=result.duration,
        dt=result.dt,
        model=result.model.id,
        recordings=result.recordings,
        stimuli=result.stimuli,
        time_trace=result.time_trace,  # type: ignore[no-untyped-call]
    )

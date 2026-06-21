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

from kanne.scalars import (
    Duration,
    DurationCoercible,
    ElectricCurrent,
    Frequency,
)
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
    duration: Duration | None = None


class CurrentClampStimulus(StimulusBase):
    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    delay: Duration = Duration("100 ms")
    amp: ElectricCurrent = ElectricCurrent("0.1 nanoampere")


class WhiteNoiseStimulus(StimulusBase):
    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    noise_level: ElectricCurrent = ElectricCurrent("0.05 nanoampere")


class SineWaveStimulus(StimulusBase):
    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    frequency: Frequency = Frequency("10 Hz")
    amplitude: ElectricCurrent = ElectricCurrent("0.1 nanoampere")


def instantiate_cell(h: Any, cell: Cell):
    h_sections: Dict[str, Any] = {}

    for sec_def in cell.topology.sections:
        sec = h.Section(name=f"{cell.id}_{sec_def.id}")
        sec.nseg = sec_def.nseg
        # NEURON geometry is expressed in micrometers; convert from the section's
        # labelled Length quantities regardless of the unit they were supplied in.
        diam_um = sec_def.diam.to("micrometer").magnitude
        sec.diam = diam_um
        h_sections[sec_def.id] = sec

        if sec_def.coords is not None:
            h.pt3dclear(sec=sec)
            for pt in sec_def.coords:
                h.pt3dadd(
                    pt.x.to("micrometer").magnitude,
                    pt.y.to("micrometer").magnitude,
                    pt.z.to("micrometer").magnitude,
                    diam_um,
                    sec=sec,
                )
        elif sec_def.length is not None:
            sec.L = sec_def.length.to("micrometer").magnitude
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
    duration: Duration
    dt: Duration
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
                # NEURON time constants are in ms, reversal potential in mV.
                hsyn.tau1 = synapse.tau1.to("millisecond").magnitude
                hsyn.tau2 = synapse.tau2.to("millisecond").magnitude
                hsyn.e = synapse.e.to("millivolt").magnitude
                net_synapses[synapse.id] = hsyn

    if model.net_stimulators:
        for net_stim in model.net_stimulators:
            hnet_stim = h.NetStim()
            hnet_stim.number = net_stim.number
            hnet_stim.start = net_stim.start.to("millisecond").magnitude
            if net_stim.interval is not None:
                hnet_stim.interval = net_stim.interval.to("millisecond").magnitude
            net_stimulations[net_stim.id] = hnet_stim

    if model.net_connections:
        for net_conn in model.net_connections:
            if isinstance(net_conn, SynapticConnection):
                hnet_syn = net_synapses[net_conn.synapse]
                hnet_stim = net_stimulations[net_conn.net_stimulator]
                hnet_conn = h.NetCon(hnet_stim, hnet_syn)
                # NetCon weight for Exp2Syn is a peak conductance in microsiemens.
                if net_conn.weight is not None:
                    hnet_conn.weight[0] = net_conn.weight.to("microsiemens").magnitude
                if net_conn.delay is not None:
                    hnet_conn.delay = net_conn.delay.to("millisecond").magnitude
                if net_conn.threshold is not None:
                    hnet_conn.threshold = net_conn.threshold.to("millivolt").magnitude
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
    duration: DurationCoercible,
    stims: List[Union[CurrentClampStimulus, SineWaveStimulus, WhiteNoiseStimulus]],
    records: List[Union[VRecord]],
    name: str,
    dt: DurationCoercible,
) -> SimulationResults:
    from neuron import h

    h.load_file("stdrun.hoc")

    # Load compiled .mod mechanisms into this worker's memory space.
    if model.environment:
        load_compiled_mechanisms(h, model.environment)

    hmodel = instantiate_model(h, model.config)

    # --- Time grid: snap the requested duration to an integer number of dt steps ---
    dt_obj = Duration.validate(dt)
    dt_ms = dt_obj.to("millisecond").magnitude
    requested_duration = Duration.validate(duration).to("millisecond").magnitude
    n_steps = int(round(requested_duration / dt_ms))
    total_ms = n_steps * dt_ms
    times = np.linspace(0.0, total_ms, n_steps + 1)

    # --- Stimuli ---
    # `refs` keeps NEURON objects alive for the lifetime of the run; without it they
    # are garbage-collected and silently stop injecting current.
    #
    # Step currents are injected with native `IClamp(delay, dur, amp)` point processes
    # (NEURON sums overlapping point processes for us). They need NO played vector, so
    # we avoid allocating a full-length NEURON Vector per stimulus -- the main source of
    # memory spikes on long, fine-dt runs. Only genuinely time-varying stimuli (sine /
    # white-noise) get a single played Vector, built from the grouped output waveform.
    refs: list = []
    grouped: dict[tuple[str, str, float], list] = defaultdict(list)
    for stim in stims:
        grouped[(stim.cell, stim.location, stim.position)].append(stim)

    # Per group, the output trace is either rebuilt deterministically from step
    # parameters after the run (so it aligns with the recorded time axis), or it is
    # the exact array we played for time-varying stimuli.
    step_groups: dict[tuple[str, str, float], list[tuple[float, float, float]]] = {}
    played_groups: dict[tuple[str, str, float], np.ndarray] = {}

    for key, stim_list in grouped.items():
        cell, loc, pos = key
        seg = hmodel.cell_h_sections[cell][loc](pos)

        waveform = np.zeros(n_steps + 1, dtype=np.float64)
        step_clamps: list[tuple[float, float, float]] = []  # (delay, dur, amp)
        needs_vector = False

        for stim_param in stim_list:
            if isinstance(stim_param, CurrentClampStimulus):
                delay = stim_param.delay.to("millisecond").magnitude
                d = (
                    stim_param.duration.to("millisecond").magnitude
                    if stim_param.duration
                    else total_ms
                )
                amp = stim_param.amp.to("nanoampere").magnitude
                step_clamps.append((delay, d, amp))
                waveform[(times >= delay) & (times < (delay + d))] += amp

            elif isinstance(stim_param, SineWaveStimulus):
                A = stim_param.amplitude.to("nanoampere").magnitude
                f = stim_param.frequency.to("hertz").magnitude
                waveform += A * np.sin(2 * np.pi * f * (times / 1000.0))
                needs_vector = True

            elif isinstance(stim_param, WhiteNoiseStimulus):
                sigma = stim_param.noise_level.to("nanoampere").magnitude
                waveform += np.random.normal(0.0, sigma, size=n_steps + 1)
                needs_vector = True

        if needs_vector:
            # Time-varying: play the exact combined waveform so the recorded
            # stimulus matches what was injected.
            iclamp = h.IClamp(seg)
            iclamp.delay = 0
            iclamp.dur = 1e9
            i_vec = h.Vector(waveform)
            t_vec = h.Vector(times)
            i_vec.play(iclamp._ref_amp, t_vec, True)
            refs += [iclamp, i_vec, t_vec]
            played_groups[key] = waveform
        else:
            for delay, d, amp in step_clamps:
                iclamp = h.IClamp(seg)
                iclamp.delay = delay
                iclamp.dur = d
                iclamp.amp = amp
                refs.append(iclamp)
            step_groups[key] = step_clamps

    # --- Recordings (registered before init, as NEURON requires) ---
    rec_t = h.Vector().record(h._ref_t)
    rec_vecs = {
        rec.id: h.Vector().record(
            hmodel.cell_h_sections[rec.cell][rec.location](rec.position)._ref_v
        )
        for rec in records
    }

    # --- Run: minimal fixed-step initialisation, then integrate ---
    h.dt = dt_ms
    h.steps_per_ms = 1.0 / dt_ms
    h.tstop = total_ms
    h.CVode().active(0)
    h.celsius = model.config.temperature.to("degC").magnitude
    v_init_mv = model.config.v_init.to("millivolt").magnitude
    h.v_init = v_init_mv
    h.finitialize(v_init_mv)
    h.continuerun(total_ms)

    # --- Collect outputs (copy out of NEURON-owned buffers) ---
    time_trace = rec_t.as_numpy().copy()

    recordings_out = [
        RecordingInput(
            cell=ID.validate(rec.cell),
            location=ID.validate(rec.location),
            kind=rec.kind,
            position=rec.position,
            trace=rec_vecs[rec.id].as_numpy().copy(),
        )
        for rec in records
    ]

    # Step waveforms are rebuilt on the recorded time axis so the reported stimulus
    # lines up exactly with `time_trace`; played waveforms are returned verbatim.
    output_waveforms: dict[tuple[str, str, float], np.ndarray] = dict(played_groups)
    for key, step_clamps in step_groups.items():
        waveform = np.zeros_like(time_trace)
        for delay, d, amp in step_clamps:
            waveform[(time_trace >= delay) & (time_trace < (delay + d))] += amp
        output_waveforms[key] = waveform

    stimuli_out = [
        StimulusInput(
            cell=ID.validate(cell),
            location=ID.validate(loc),
            kind=StimulusKind.CURRENT,
            position=pos,
            trace=waveform,
        )
        for (cell, loc, pos), waveform in output_waveforms.items()
    ]

    return SimulationResults(
        time_trace=time_trace,
        recordings=recordings_out,
        stimuli=stimuli_out,
        model=model,
        duration=Duration(f"{total_ms} ms"),
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
    duration: DurationCoercible,
    stims: List[Union[CurrentClampStimulus]],  # type: ignore[no-untyped-call]
    records: List[Union[VRecord]],  # type: ignore[no-untyped-call]
    name: str | None = None,
    dt: DurationCoercible = "1 ms",
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
    duration: DurationCoercible,
    stims: List[Union[CurrentClampStimulus, WhiteNoiseStimulus, SineWaveStimulus]],  # type: ignore[no-untyped-call]
    records: List[Union[VRecord]],  # type: ignore[no-untyped-call]
    name: str | None = None,
    dt: DurationCoercible = "0.05 ms",
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

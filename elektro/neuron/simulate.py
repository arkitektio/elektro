# The simulation function that applies the stimulation and records the outputs
import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import time
import numpy as np
import logging
from elektro.api.schema import (
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
import uuid
from typing import Any, Dict, List, Optional, Literal, Union
from pydantic import BaseModel, Field

from kanne.scalars import Ampere, Hertz, Millisecond, MillisecondCoercible
from rath.scalars import ID
from collections import defaultdict

logger = logging.getLogger(__name__)


class RecordBase(BaseModel):
    """Base class for recording parameters."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )  # Unique identifier for the recording
    name: Optional[str] = None  # Name of the recording
    cell: str
    location: str  # Section name
    position: float = 0.5  # Between 0 and 1
    kind: Literal[RecordingKind.VOLTAGE, RecordingKind.CURRENT] = RecordingKind.VOLTAGE


class VRecord(RecordBase):
    """VTEC-specific recording parameters."""

    kind: Literal[RecordingKind.VOLTAGE] = RecordingKind.VOLTAGE  # type: ignore[assignment]
    pass


class StimulusBase(BaseModel):
    """Base class for stimulus parameters."""

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )  # Unique identifier for the recording
    name: Optional[str] = None  # Name of the recording# Name of the stimulus
    kind: StimulusKind
    cell: str
    location: str  # Section name
    position: float = 0.5  # Between 0 and 1
    duration: Millisecond | None = None  # Duration of the stimulus (in ms)


class CurrentClampStimulus(StimulusBase):
    """Current clamp stimulus parameters."""

    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    delay: Millisecond = Millisecond(100.0)  # ms
    amp: Ampere = Ampere(0.1, "nanoampere")  # nA


class WhiteNoiseStimulus(StimulusBase):
    """Custom noise stimulus parameters."""

    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    noise_level: Ampere = Ampere(0.05, "nanoampere")  # nA


class SineWaveStimulus(StimulusBase):
    """Custom sine wave stimulus parameters."""

    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    frequency: Hertz = Hertz(10.0)  # Hz
    amplitude: Ampere = Ampere(0.1, "nanoampere")  # nA


def instantiate_cell(h: Any, cell: Cell):
    h_sections: Dict[str, Any] = {}

    # Create sections and set geometry
    for sec_def in cell.topology.sections:
        logger.debug(f"Creating section {sec_def} with geometry {sec_def}")
        sec = h.Section(name=f"{cell.id}_{sec_def.id}")
        sec.nseg = sec_def.nseg
        sec.diam = sec_def.diam
        h_sections[sec_def.id] = sec

        if sec_def.coords is not None:
            print("Setting coordinates for section", sec_def.id)
            h.pt3dclear(sec=sec)
            for pt in sec_def.coords:
                h.pt3dadd(pt.x, pt.y, pt.z, sec_def.diam, sec=sec)

        elif sec_def.length is not None:
            sec.L = sec_def.length
        else:
            raise ValueError(
                "Either coords or length must be provided for section geometry"
            )

    # Connect sections
    for sec_def in cell.topology.sections:
        for conn in sec_def.connections:
            logger.debug(
                f"Connecting {sec_def.id} to {conn.parent} at location {conn.location}"
            )
            parent = h_sections[conn.parent]
            child = h_sections[sec_def.id]
            child.connect(parent(conn.location))

    # Apply biophysics
    for sec_def in cell.topology.sections:
        logger.debug(f"Applying biophysics to section {sec_def}")
        sec = h_sections[sec_def.id]
        comp = cell.biophysics.compartment_for_id(sec_def.category)
        assert comp, (
            f"Compartment {sec_def.category} not found in cell {cell.id}. Available compartments: {cell.biophysics.compartment_ids}"
        )

        for mechanism in comp.mechanisms:
            try:
                sec.insert(mechanism)
            except Exception as e:
                raise ValueError(
                    f"Failed add mechanism {mechanism} based on {comp}"
                ) from e

        for param in comp.section_params:
            assert param.mechanism in comp.mechanisms, (
                f"Mechanism {param.mechanism} for Param {param} in Compartment not found in mechanisms list. Available mechanisms: {comp.mechanisms}"
            )

            value = param.value

            for seg in sec.allseg():
                try:
                    setattr(sec, param.param, value)
                except Exception as e:
                    raise ValueError(
                        f"Failed to set parameter {param.param} on {sec_def} based on {comp}"
                    ) from e

        for gparam in comp.global_params:
            try:
                setattr(sec, gparam.param, gparam.value)
            except Exception as e:
                raise ValueError(
                    f"Failed to set global parameter {gparam.param} on {sec} based on {comp}"
                ) from e

    return h_sections


@dataclass
class NeuronModelInstance:
    """
    Class to hold the NEURON model instance.
    """

    h: object
    cell_h_sections: Dict[str, Dict[str, Any]]
    net_stimulations: Dict[str, Any]
    net_connections: Dict[str, Any]
    net_synapses: Dict[str, Any]


@dataclass
class SimulationResults:
    """
    Class to hold the results of the simulation.
    """

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
    """
    Instantiate the model in NEURON.
    """

    # Create the cell sections
    cell_h_sections: Dict[str, Dict[str, Any]] = {}
    net_stimulations: Dict[str, Any] = {}
    net_connections: Dict[str, Any] = {}
    net_synapses: Dict[str, Any] = {}

    for cell in model.cells:
        try:
            cell_h_sections[cell.id] = instantiate_cell(h, cell)
        except Exception as e:
            raise ValueError(f"Failed to instantiate cell {cell.id}: {e}") from e

    h.define_shape()  # Define the shape of the sections

    if model.net_synapses:
        for synapse in model.net_synapses:
            if isinstance(synapse, ExpTwoSynapse):
                hsec = cell_h_sections[synapse.cell][synapse.location]
                hsyn = h.Exp2Syn(hsec(synapse.position))
                hsyn.tau1 = synapse.tau1
                hsyn.tau2 = synapse.tau2
                hsyn.e = synapse.e
                net_synapses[synapse.id] = hsyn
            else:
                raise ValueError(f"Unknown synapse type: {synapse}")

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
                # TODO: Check if is synaptic connection
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
    hmodel = instantiate_model(h, model.config)

    # 1. Validate units
    dt_obj = Millisecond.validate(dt)
    dt_ms = dt_obj.to("millisecond").magnitude

    requested_duration = Millisecond.validate(duration).to("millisecond").magnitude

    # --------------------------------------------------------
    # 2. SNAP TO GRID (The Fix)
    # --------------------------------------------------------
    # We calculate the exact integer number of steps closest to the requested duration
    print(f"Requested duration: {requested_duration} ms with dt={dt_ms} ms")
    n_steps = int(round(requested_duration / dt_ms))

    # We calculate the TRUE duration that perfectly fits these steps
    actual_dur_ms = n_steps * dt_ms

    if abs(actual_dur_ms - requested_duration) > 1e-9:
        print(
            f"Adjusting duration from {requested_duration} to {actual_dur_ms} ms to align with dt={dt_ms}"
        )

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
    # usage of linspace with n_steps + 1 guarantees exact array size matching NEURON
    times = np.linspace(0, actual_dur_ms, n_steps + 1)

    # NEURON Vector for playback
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

        # Use the aligned 'times' array here
        combined = np.zeros_like(times, dtype=np.float64)

        for stim_param in stim_list:
            if isinstance(stim_param, CurrentClampStimulus):
                delay = stim_param.delay.to("millisecond").magnitude
                # Duration handling: if not specified, use full simulation time
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
    # We record actual time to be safe, but it should now match 'times' exactly
    rec_t = h.Vector().record(h._ref_t)

    raw_results = {}
    for rec in records:
        sec = hmodel.cell_h_sections[rec.cell][rec.location]
        v_vec = h.Vector().record(sec(rec.position)._ref_v)
        raw_results[rec.id] = v_vec

    # 8. Run
    h.run()

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

        # Because we snapped to grid, len(waveform) should equal len(time_trace)
        # But we keep interp as a fallback for float precision edges
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
        duration=Millisecond(
            actual_dur_ms, "millisecond"
        ),  # Return the ACTUAL duration
        dt=dt_obj,
        name=name or f"Simulation for {model.name}",
        raw_results={},
        raw_stimulations={},
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

    Parameters
    - model: the NeuronModel to simulate
    - duration: total duration (milliseconds or coercible)
    - stims: stimuli definitions
    - records: recording definitions
    - name: optional run name
    - dt: simulation time-step (milliseconds). Smaller `dt` -> finer resolution.
    """

    # `dt` is the time-step (ms) that controls how small each integration step is.
    if process_pool is None:
        process_pool = ProcessPoolExecutor(max_workers=1)

    loop = asyncio.get_event_loop()

    if not name:
        name = f"Simulation for {model.name}"

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
    # Run the simulation in a separate process
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

    - `dt` is the simulation time-step in milliseconds. Use smaller values for
      higher temporal resolution at the cost of longer compute time.
    """

    # `dt` (ms) controls integration step size
    if process_pool is None:
        process_pool = ProcessPoolExecutor(max_workers=1)

    loop = asyncio.get_event_loop()

    if not name:
        name = f"Simulation for {model.name}"

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
    # Run the simulation in a separate process
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

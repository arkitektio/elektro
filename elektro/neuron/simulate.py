# The simulation function that applies the stimulation and records the outputs
import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
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

from rath.scalars import ID


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
    duration: float | None = None  # Duration of the stimulus (in ms)


class CurrentClampStimulus(StimulusBase):
    """Current clamp stimulus parameters."""

    kind: Literal[StimulusKind.VOLTAGE] = StimulusKind.VOLTAGE  # type: ignore[assignment]
    delay: float = 100.0  # ms
    amp: float = 0.1  # nA


def instantiate_cell(h: Any, cell: Cell):
    h_sections: Dict[str, Any] = {}

    # Create sections and set geometry
    for sec_def in cell.topology.sections:
        logger.debug(f"Creating section {sec_def} with geometry {sec_def}")
        sec = h.Section(name=f"{cell.id}_{sec_def.id}")
        sec.nseg = sec_def.nseg
        sec.diam = sec_def.diam
        h_sections[sec_def.id] = sec

        if sec_def.coords:
            h.pt3dclear(sec=sec)
            for pt in sec_def.coords:
                h.pt3dadd(pt.x, pt.y, pt.z, sec_def.diam, sec=sec)
        elif sec_def.length:
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
    duration: int
    dt: int
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
    duration: int,
    stims: List[Union[CurrentClampStimulus]],  # type: ignore[no-untyped-call]
    records: List[Union[VRecord]],  # type: ignore[no-untyped-call]
    name: str,
    dt: int = 1,
) -> SimulationResults:
    from neuron import h  # type: ignore[import]

    h.load_file("stdrun.hoc")  # type: ignore[no-untyped-call]

    hmodel = instantiate_model(h, model.config)

    h.dt = dt
    h.tstop = duration  # Define the stop time of the simulation
    h.v_init = model.config.v_init
    h.celsius = model.config.celsius
    h.finitialize(model.config.v_init)  # type: ignore[no-untyped-call]
    h.fcurrent()  # type: ignore[no-untyped-call]
    h.setdt()  # type: ignore[no-untyped-call]
    h.init()  # type: ignore[no-untyped-call]

    raw_stimulations: dict[str, Any] = {}

    # Apply the stimulations
    for stim_param in stims:
        logger.debug("Adding stimulus:", stim_param)
        if isinstance(stim_param, CurrentClampStimulus):  # type: ignore[no-untyped-call]
            stim_sec = hmodel.cell_h_sections[stim_param.cell][stim_param.location]
            print("Stimulus section:", stim_sec)
            stim = h.IClamp(stim_sec(stim_param.position))  # type: ignore[no-untyped-call]
            stim.delay = stim_param.delay
            stim.dur = stim_param.duration or duration
            stim.amp = stim_param.amp

            v_vec = h.Vector().record(stim._ref_i)  # type: ignore[no-untyped-call]
            raw_stimulations[stim_param.id] = v_vec

        else:
            raise ValueError(f"Unknown stimulus type: {stim_param}")

    # Prepare recordings
    raw_results: dict[str, Any] = {}
    t_vec = h.Vector().record(h._ref_t)  # type: ignore[no-untyped-call]

    for rec_param in records:
        logger.debug("Adding recording:", rec_param)
        sec = hmodel.cell_h_sections[rec_param.cell][rec_param.location]

        if isinstance(rec_param, VRecord):  # type: ignore[no-untyped-call]
            v_vec = h.Vector().record(sec(rec_param.position)._ref_v)  # type: ignore[no-untyped-call]
            raw_results[rec_param.id] = v_vec
        else:
            raise ValueError(f"Unknown recording type: {rec_param}")

    # Run the simulation
    h.run()  # type: ignore[no-untyped-call]

    time_trace = np.array(t_vec)  # type: ignore[no-untyped-call]
    recordings: list[RecordingInput] = []

    for rec_param in records:
        recordings.append(
            RecordingInput(
                cell=ID.validate(rec_param.cell),
                location=ID.validate(rec_param.location),
                kind=rec_param.kind,
                position=rec_param.position,
                trace=np.array(raw_results[rec_param.id]),  # type: ignore[no-untyped-call]
            )
        )  # type: ignore[no-untyped-call]

    stimuli: list[StimulusInput] = []
    for stim_param in stims:
        stimuli.append(
            StimulusInput(
                cell=ID.validate(stim_param.cell),
                location=ID.validate(stim_param.location),
                kind=stim_param.kind,
                position=stim_param.position,
                trace=np.array(raw_stimulations[stim_param.id]),  # type: ignore[no-untyped-call]
            )
        )

    return SimulationResults(
        time_trace=time_trace,  # type: ignore[no-untyped-call]
        recordings=recordings,
        stimuli=stimuli,
        model=model,
        duration=duration,
        dt=dt,
        name=name or f"Simulation for {model.name}",
        raw_results=raw_results,
        raw_stimulations=raw_stimulations,
    )


async def arun_simulation(
    model: NeuronModel,
    duration: int,
    stims: List[Union[CurrentClampStimulus]],  # type: ignore[no-untyped-call]
    records: List[Union[VRecord]],  # type: ignore[no-untyped-call]
    name: str | None = None,
    dt: int = 1,
    process_pool: ProcessPoolExecutor | None = None,
) -> Simulation:
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

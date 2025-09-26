from elektro.traits import (
    HasZarrStoreAccessor,
    TopologyTrait,
    ExperimentTrait,
    CompartmentTrait,
    ModelConfigInputTrait,
    HasZarrStoreTrait,
    TopologyInputTrait,
    HasDownloadAccessor,
    BiophysicsInputTrait,
    CompartmentInputTrait,
    SectionInputTrait,
    ModelConfigTrait,
    BiophysicsTrait,
    IsVectorizableTrait,
)
from typing import (
    Optional,
    Annotated,
    List,
    Union,
    Iterable,
    Literal,
    AsyncIterator,
    Iterator,
)
from elektro.funcs import subscribe, execute, asubscribe, aexecute
from rath.scalars import ID, IDCoercible
from elektro.scalars import FiveDVector, TraceCoercible, FileLike, TwoDVector, TraceLike
from pydantic import Field, ConfigDict, BaseModel
from elektro.rath import ElektroRath
from datetime import datetime
from enum import Enum


class RoiKind(str, Enum):
    """No documentation"""

    LINE = "LINE"
    POINT = "POINT"
    SPIKE = "SPIKE"
    SLICE = "SLICE"


class StimulusKind(str, Enum):
    """No documentation"""

    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"
    UNKNOWN = "UNKNOWN"


class RecordingKind(str, Enum):
    """No documentation"""

    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"
    TIME = "TIME"
    INA = "INA"
    UNKNOWN = "UNKNOWN"


class ConnectionKind(str, Enum):
    """No documentation"""

    SYNAPSE = "SYNAPSE"


class SynapseKind(str, Enum):
    """No documentation"""

    EXP2SYN = "EXP2SYN"
    GABAA = "GABAA"


class TraceFilter(BaseModel):
    """No documentation"""

    name: Optional["StrFilterLookup"] = None
    ids: Optional[List[ID]] = None
    dataset: Optional["DatasetFilter"] = None
    not_derived: Optional[bool] = Field(alias="notDerived", default=None)
    search: Optional[str] = None
    and_: Optional["TraceFilter"] = Field(alias="AND", default=None)
    or_: Optional["TraceFilter"] = Field(alias="OR", default=None)
    not_: Optional["TraceFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StrFilterLookup(BaseModel):
    """No documentation"""

    exact: Optional[str] = None
    i_exact: Optional[str] = Field(alias="iExact", default=None)
    contains: Optional[str] = None
    i_contains: Optional[str] = Field(alias="iContains", default=None)
    in_list: Optional[List[str]] = Field(alias="inList", default=None)
    gt: Optional[str] = None
    gte: Optional[str] = None
    lt: Optional[str] = None
    lte: Optional[str] = None
    starts_with: Optional[str] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[str] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[str] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[str] = Field(alias="iEndsWith", default=None)
    range: Optional[List[str]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DatasetFilter(BaseModel):
    """No documentation"""

    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    and_: Optional["DatasetFilter"] = Field(alias="AND", default=None)
    or_: Optional["DatasetFilter"] = Field(alias="OR", default=None)
    not_: Optional["DatasetFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OffsetPaginationInput(BaseModel):
    """No documentation"""

    offset: int
    limit: Optional[int] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class NeuronModelFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    and_: Optional["NeuronModelFilter"] = Field(alias="AND", default=None)
    or_: Optional["NeuronModelFilter"] = Field(alias="OR", default=None)
    not_: Optional["NeuronModelFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ModelCollectionFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    and_: Optional["ModelCollectionFilter"] = Field(alias="AND", default=None)
    or_: Optional["ModelCollectionFilter"] = Field(alias="OR", default=None)
    not_: Optional["ModelCollectionFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class SimulationFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    and_: Optional["SimulationFilter"] = Field(alias="AND", default=None)
    or_: Optional["SimulationFilter"] = Field(alias="OR", default=None)
    not_: Optional["SimulationFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StimulusFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    and_: Optional["StimulusFilter"] = Field(alias="AND", default=None)
    or_: Optional["StimulusFilter"] = Field(alias="OR", default=None)
    not_: Optional["StimulusFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RecordingFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    and_: Optional["RecordingFilter"] = Field(alias="AND", default=None)
    or_: Optional["RecordingFilter"] = Field(alias="OR", default=None)
    not_: Optional["RecordingFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ExperimentFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    and_: Optional["ExperimentFilter"] = Field(alias="AND", default=None)
    or_: Optional["ExperimentFilter"] = Field(alias="OR", default=None)
    not_: Optional["ExperimentFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestUploadInput(BaseModel):
    """No documentation"""

    key: str
    datalayer: str
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestAccessInput(BaseModel):
    """No documentation"""

    store: ID
    duration: Optional[int] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestFileUploadInput(BaseModel):
    """No documentation"""

    key: str
    datalayer: str
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestFileAccessInput(BaseModel):
    """No documentation"""

    store: ID
    duration: Optional[int] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateBlockInput(BaseModel):
    """No documentation"""

    file: Optional[ID] = None
    name: str
    recording_time: Optional[datetime] = Field(alias="recordingTime", default=None)
    segments: List["BlockSegmentInput"]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BlockSegmentInput(BaseModel):
    """No documentation"""

    name: Optional[str] = None
    description: Optional[str] = None
    analog_signals: List["AnalogSignalInput"] = Field(alias="analogSignals")
    irregularly_sampled_signals: List["IrregularlySampledSignalInput"] = Field(
        alias="irregularlySampledSignals"
    )
    spike_trains: List["SpikeTrainInput"] = Field(alias="spikeTrains")
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AnalogSignalInput(BaseModel):
    """No documentation"""

    time_trace: TraceLike = Field(alias="timeTrace")
    name: Optional[str] = None
    description: Optional[str] = None
    sampling_rate: float = Field(alias="samplingRate")
    t_start: float = Field(alias="tStart")
    unit: Optional[str] = None
    channels: List["AnalogSignalChannelInput"]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AnalogSignalChannelInput(BaseModel):
    """No documentation"""

    name: str
    index: int
    unit: Optional[str] = None
    description: Optional[str] = None
    color: Optional[List[int]] = None
    trace: TraceLike
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class IrregularlySampledSignalInput(BaseModel):
    """No documentation"""

    times: TraceLike
    trace: TraceLike
    name: Optional[str] = None
    unit: Optional[str] = None
    description: Optional[str] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class SpikeTrainInput(BaseModel):
    """No documentation"""

    times: TraceLike
    t_start: float = Field(alias="tStart")
    t_stop: float = Field(alias="tStop")
    waveforms: Optional[TraceLike] = None
    name: Optional[str] = None
    description: Optional[str] = None
    left_sweep: Optional[float] = Field(alias="leftSweep", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FromTraceLikeInput(BaseModel):
    """Input type for creating an image from an array-like object"""

    array: TraceLike
    "The array-like object to create the image from"
    name: str
    "The name of the image"
    dataset: Optional[ID] = None
    "Optional dataset ID to associate the image with"
    tags: Optional[List[str]] = None
    "Optional list of tags to associate with the image"
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateNeuronModelInput(BaseModel):
    """No documentation"""

    name: str
    parent: Optional[ID] = None
    config: "ModelConfigInput"
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ModelConfigInput(ModelConfigInputTrait, BaseModel):
    """No documentation"""

    cells: List["CellInput"]
    net_stimulators: Optional[List["NetStimulatorInput"]] = Field(
        alias="netStimulators", default=None
    )
    net_connections: Optional[List["NetConnectionInput"]] = Field(
        alias="netConnections", default=None
    )
    net_synapses: Optional[List["NetSynapseInput"]] = Field(
        alias="netSynapses", default=None
    )
    v_init: float = Field(alias="vInit")
    celsius: float
    label: Optional[str] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CellInput(BaseModel):
    """No documentation"""

    id: str
    biophysics: "BiophysicsInput"
    topology: "TopologyInput"
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BiophysicsInput(BiophysicsInputTrait, BaseModel):
    """No documentation"""

    compartments: List["CompartmentInput"]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CompartmentInput(CompartmentInputTrait, BaseModel):
    """No documentation"""

    id: str
    mechanisms: List[str]
    section_params: Optional[List["SectionParamMapInput"]] = Field(
        alias="sectionParams", default=None
    )
    global_params: Optional[List["GlobalParamMapInput"]] = Field(
        alias="globalParams", default=None
    )
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class SectionParamMapInput(BaseModel):
    """No documentation"""

    param: str
    mechanism: str
    "The governing mechanism"
    value: float
    "The value of the parameter"
    description: Optional[str] = None
    "Description of the parameter"
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class GlobalParamMapInput(BaseModel):
    """No documentation"""

    param: str
    value: float
    description: Optional[str] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class TopologyInput(TopologyInputTrait, BaseModel):
    """No documentation"""

    sections: List["SectionInput"]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class SectionInput(SectionInputTrait, BaseModel):
    """No documentation"""

    id: str
    category: Optional[str] = None
    nseg: int
    diam: float
    length: Optional[float] = None
    "Length of the section. Required if coords is not provided."
    coords: Optional[List["CoordInput"]] = None
    connections: Optional[List["ConnectionInput"]] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CoordInput(BaseModel):
    """No documentation"""

    x: float
    y: float
    z: float
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ConnectionInput(BaseModel):
    """No documentation"""

    parent: str
    location: float
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class NetStimulatorInput(BaseModel):
    """No documentation"""

    id: ID
    start: float
    number: int
    interval: Optional[float] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class NetConnectionInput(BaseModel):
    """No documentation"""

    kind: ConnectionKind
    id: ID
    weight: Optional[float] = None
    threshold: Optional[float] = None
    delay: Optional[float] = None
    net_stimulator: ID = Field(alias="netStimulator")
    synapse: ID
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class NetSynapseInput(BaseModel):
    """No documentation"""

    id: ID
    kind: SynapseKind
    e: float
    tau2: float
    tau1: float
    cell: ID
    location: ID
    position: float
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateSimulationInput(BaseModel):
    """No documentation"""

    name: str
    model: ID
    recordings: List["RecordingInput"]
    stimuli: List["StimulusInput"]
    time_trace: Optional[TraceLike] = Field(alias="timeTrace", default=None)
    duration: float
    dt: Optional[float] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RecordingInput(BaseModel):
    """No documentation"""

    trace: TraceLike
    kind: RecordingKind
    cell: Optional[ID] = None
    location: Optional[ID] = None
    position: Optional[float] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StimulusInput(BaseModel):
    """No documentation"""

    trace: TraceLike
    kind: StimulusKind
    cell: Optional[ID] = None
    location: Optional[ID] = None
    position: Optional[float] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FromFileLike(BaseModel):
    """No documentation"""

    name: str
    file: FileLike
    origins: Optional[List[ID]] = None
    dataset: Optional[ID] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateModelCollectionInput(BaseModel):
    """No documentation"""

    name: str
    models: List[ID]
    description: Optional[str] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateDatasetInput(BaseModel):
    """No documentation"""

    name: str
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ChangeDatasetInput(BaseModel):
    """No documentation"""

    name: str
    id: ID
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RevertInput(BaseModel):
    """No documentation"""

    id: ID
    history_id: ID = Field(alias="historyId")
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateExperimentInput(BaseModel):
    """No documentation"""

    name: str
    time_trace: Optional[ID] = Field(alias="timeTrace", default=None)
    stimulus_views: List["StimulusViewInput"] = Field(alias="stimulusViews")
    recording_views: List["RecordingViewInput"] = Field(alias="recordingViews")
    description: Optional[str] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StimulusViewInput(BaseModel):
    """No documentation"""

    stimulus: ID
    offset: Optional[float] = None
    duration: Optional[float] = None
    label: Optional[str] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RecordingViewInput(BaseModel):
    """No documentation"""

    recording: ID
    offset: Optional[float] = None
    duration: Optional[float] = None
    label: Optional[str] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RoiInput(BaseModel):
    """No documentation"""

    trace: ID
    "The image this ROI belongs to"
    vectors: List[TwoDVector]
    "The vector coordinates defining the as XY"
    kind: RoiKind
    "The type/kind of ROI"
    label: Optional[str] = None
    "The label of the ROI"
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateRoiInput(BaseModel):
    """No documentation"""

    roi: ID
    label: Optional[str] = None
    vectors: Optional[List[TwoDVector]] = None
    kind: Optional[RoiKind] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeleteRoiInput(BaseModel):
    """No documentation"""

    id: ID
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BlockGroup(BaseModel):
    """No documentation"""

    typename: Literal["BlockGroup"] = Field(
        alias="__typename", default="BlockGroup", exclude=True
    )
    id: ID
    name: str

    class Meta:
        """Meta class for BlockGroup"""

        document = "fragment BlockGroup on BlockGroup {\n  id\n  name\n  __typename\n}"
        name = "BlockGroup"
        type = "BlockGroup"


class Credentials(BaseModel):
    """Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)"""

    typename: Literal["Credentials"] = Field(
        alias="__typename", default="Credentials", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    status: str
    secret_key: str = Field(alias="secretKey")
    bucket: str
    key: str
    session_token: str = Field(alias="sessionToken")
    store: str

    class Meta:
        """Meta class for Credentials"""

        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n  __typename\n}"
        name = "Credentials"
        type = "Credentials"


class AccessCredentials(BaseModel):
    """Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)"""

    typename: Literal["AccessCredentials"] = Field(
        alias="__typename", default="AccessCredentials", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    bucket: str
    key: str
    session_token: str = Field(alias="sessionToken")
    path: str

    class Meta:
        """Meta class for AccessCredentials"""

        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n  __typename\n}"
        name = "AccessCredentials"
        type = "AccessCredentials"


class Dataset(BaseModel):
    """No documentation"""

    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    name: str
    description: Optional[str] = Field(default=None)

    class Meta:
        """Meta class for Dataset"""

        document = (
            "fragment Dataset on Dataset {\n  name\n  description\n  __typename\n}"
        )
        name = "Dataset"
        type = "Dataset"


class ModelCollectionModels(BaseModel):
    """No documentation"""

    typename: Literal["NeuronModel"] = Field(
        alias="__typename", default="NeuronModel", exclude=True
    )
    id: ID
    name: str


class ModelCollection(BaseModel):
    """No documentation"""

    typename: Literal["ModelCollection"] = Field(
        alias="__typename", default="ModelCollection", exclude=True
    )
    name: str
    id: ID
    models: List[ModelCollectionModels]

    class Meta:
        """Meta class for ModelCollection"""

        document = "fragment ModelCollection on ModelCollection {\n  name\n  id\n  models {\n    id\n    name\n    __typename\n  }\n  __typename\n}"
        name = "ModelCollection"
        type = "ModelCollection"


class ExpTwoSynapse(BaseModel):
    """No documentation"""

    typename: Literal["Exp2Synapse"] = Field(
        alias="__typename", default="Exp2Synapse", exclude=True
    )
    id: ID
    tau1: float
    tau2: float
    e: float
    cell: str
    location: str
    position: float

    class Meta:
        """Meta class for ExpTwoSynapse"""

        document = "fragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}"
        name = "ExpTwoSynapse"
        type = "Exp2Synapse"


class SynapticConnection(BaseModel):
    """No documentation"""

    typename: Literal["SynapticConnection"] = Field(
        alias="__typename", default="SynapticConnection", exclude=True
    )
    id: ID
    net_stimulator: ID = Field(alias="netStimulator")
    synapse: ID
    weight: Optional[float] = Field(default=None)
    threshold: Optional[float] = Field(default=None)
    delay: Optional[float] = Field(default=None)

    class Meta:
        """Meta class for SynapticConnection"""

        document = "fragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}"
        name = "SynapticConnection"
        type = "SynapticConnection"


class SectionCoords(BaseModel):
    """No documentation"""

    typename: Literal["Coord"] = Field(
        alias="__typename", default="Coord", exclude=True
    )
    x: float
    y: float
    z: float


class SectionConnections(BaseModel):
    """No documentation"""

    typename: Literal["Connection"] = Field(
        alias="__typename", default="Connection", exclude=True
    )
    parent: str
    location: float


class Section(BaseModel):
    """No documentation"""

    typename: Literal["Section"] = Field(
        alias="__typename", default="Section", exclude=True
    )
    id: str
    length: Optional[float] = Field(default=None)
    "Length of the section. Required if coords is not provided."
    diam: float
    coords: Optional[List[SectionCoords]] = Field(default=None)
    category: str
    nseg: int
    connections: List[SectionConnections]

    class Meta:
        """Meta class for Section"""

        document = "fragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}"
        name = "Section"
        type = "Section"


class SectionParamMap(BaseModel):
    """No documentation"""

    typename: Literal["SectionParamMap"] = Field(
        alias="__typename", default="SectionParamMap", exclude=True
    )
    param: str
    mechanism: str
    "The governing mechanism"
    value: float
    "The value of the parameter"

    class Meta:
        """Meta class for SectionParamMap"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}"
        name = "SectionParamMap"
        type = "SectionParamMap"


class GlobalParamMap(BaseModel):
    """No documentation"""

    typename: Literal["GlobalParamMap"] = Field(
        alias="__typename", default="GlobalParamMap", exclude=True
    )
    param: str
    value: float

    class Meta:
        """Meta class for GlobalParamMap"""

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}"
        name = "GlobalParamMap"
        type = "GlobalParamMap"


class NetStimulator(BaseModel):
    """No documentation"""

    typename: Literal["NetStimulator"] = Field(
        alias="__typename", default="NetStimulator", exclude=True
    )
    id: ID
    interval: Optional[float] = Field(default=None)
    number: int
    start: float

    class Meta:
        """Meta class for NetStimulator"""

        document = "fragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}"
        name = "NetStimulator"
        type = "NetStimulator"


class ROITrace(HasZarrStoreTrait, BaseModel):
    """No documentation"""

    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID


class ROI(IsVectorizableTrait, BaseModel):
    """No documentation"""

    typename: Literal["ROI"] = Field(alias="__typename", default="ROI", exclude=True)
    id: ID
    trace: ROITrace
    vectors: List[FiveDVector]
    kind: RoiKind

    class Meta:
        """Meta class for ROI"""

        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}"
        name = "ROI"
        type = "ROI"


class ZarrStore(HasZarrStoreAccessor, BaseModel):
    """No documentation"""

    typename: Literal["ZarrStore"] = Field(
        alias="__typename", default="ZarrStore", exclude=True
    )
    id: ID
    key: str
    "The key where the data is stored."
    bucket: str
    "The bucket where the data is stored."
    path: Optional[str] = Field(default=None)
    "The path to the data. Relative to the bucket."

    class Meta:
        """Meta class for ZarrStore"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}"
        name = "ZarrStore"
        type = "ZarrStore"


class BigFileStore(HasDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["BigFileStore"] = Field(
        alias="__typename", default="BigFileStore", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str
    presigned_url: str = Field(alias="presignedUrl")

    class Meta:
        """Meta class for BigFileStore"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}"
        name = "BigFileStore"
        type = "BigFileStore"


class Compartment(CompartmentTrait, BaseModel):
    """No documentation"""

    typename: Literal["Compartment"] = Field(
        alias="__typename", default="Compartment", exclude=True
    )
    id: str
    mechanisms: List[str]
    global_params: List[GlobalParamMap] = Field(alias="globalParams")
    section_params: List[SectionParamMap] = Field(alias="sectionParams")

    class Meta:
        """Meta class for Compartment"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}"
        name = "Compartment"
        type = "Compartment"


class RecordingTrace(HasZarrStoreTrait, BaseModel):
    """No documentation"""

    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID
    store: ZarrStore
    "The store where the image data is stored."


class Recording(BaseModel):
    """No documentation"""

    typename: Literal["Recording"] = Field(
        alias="__typename", default="Recording", exclude=True
    )
    id: ID
    label: str
    cell: str
    trace: RecordingTrace

    class Meta:
        """Meta class for Recording"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
        name = "Recording"
        type = "Recording"


class StimulusTrace(HasZarrStoreTrait, BaseModel):
    """No documentation"""

    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID
    store: ZarrStore
    "The store where the image data is stored."


class Stimulus(BaseModel):
    """No documentation"""

    typename: Literal["Stimulus"] = Field(
        alias="__typename", default="Stimulus", exclude=True
    )
    id: ID
    label: str
    cell: str
    kind: StimulusKind
    trace: StimulusTrace

    class Meta:
        """Meta class for Stimulus"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
        name = "Stimulus"
        type = "Stimulus"


class Trace(HasZarrStoreTrait, BaseModel):
    """No documentation"""

    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID
    name: str
    "The name of the image"
    store: ZarrStore
    "The store where the image data is stored."

    class Meta:
        """Meta class for Trace"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}"
        name = "Trace"
        type = "Trace"


class FileOrigins(HasZarrStoreTrait, BaseModel):
    """No documentation"""

    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID


class File(BaseModel):
    """No documentation"""

    typename: Literal["File"] = Field(alias="__typename", default="File", exclude=True)
    origins: List[FileOrigins]
    id: ID
    name: str
    store: BigFileStore

    class Meta:
        """Meta class for File"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}"
        name = "File"
        type = "File"


class CellBiophysics(BiophysicsTrait, BaseModel):
    """No documentation"""

    typename: Literal["Biophysics"] = Field(
        alias="__typename", default="Biophysics", exclude=True
    )
    compartments: List[Compartment]


class CellTopology(TopologyTrait, BaseModel):
    """No documentation"""

    typename: Literal["Topology"] = Field(
        alias="__typename", default="Topology", exclude=True
    )
    sections: List[Section]


class Cell(BaseModel):
    """No documentation"""

    typename: Literal["Cell"] = Field(alias="__typename", default="Cell", exclude=True)
    id: str
    biophysics: CellBiophysics
    topology: CellTopology

    class Meta:
        """Meta class for Cell"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
        name = "Cell"
        type = "Cell"


class AnalogSignalChannel(BaseModel):
    """No documentation"""

    typename: Literal["AnalogSignalChannel"] = Field(
        alias="__typename", default="AnalogSignalChannel", exclude=True
    )
    id: ID
    index: int
    trace: Trace

    class Meta:
        """Meta class for AnalogSignalChannel"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignalChannel on AnalogSignalChannel {\n  id\n  index\n  trace {\n    ...Trace\n    __typename\n  }\n  __typename\n}"
        name = "AnalogSignalChannel"
        type = "AnalogSignalChannel"


class ExperimentRecordingviews(BaseModel):
    """No documentation"""

    typename: Literal["ExperimentRecordingView"] = Field(
        alias="__typename", default="ExperimentRecordingView", exclude=True
    )
    label: Optional[str] = Field(default=None)
    recording: Recording


class ExperimentStimulusviews(BaseModel):
    """No documentation"""

    typename: Literal["ExperimentStimulusView"] = Field(
        alias="__typename", default="ExperimentStimulusView", exclude=True
    )
    label: Optional[str] = Field(default=None)
    stimulus: Stimulus


class Experiment(ExperimentTrait, BaseModel):
    """No documentation"""

    typename: Literal["Experiment"] = Field(
        alias="__typename", default="Experiment", exclude=True
    )
    name: str
    id: ID
    time_trace: Trace = Field(alias="timeTrace")
    recording_views: List[ExperimentRecordingviews] = Field(alias="recordingViews")
    stimulus_views: List[ExperimentStimulusviews] = Field(alias="stimulusViews")

    class Meta:
        """Meta class for Experiment"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Experiment on Experiment {\n  name\n  id\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  recordingViews {\n    label\n    recording {\n      ...Recording\n      __typename\n    }\n    __typename\n  }\n  stimulusViews {\n    label\n    stimulus {\n      ...Stimulus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
        name = "Experiment"
        type = "Experiment"


class NeuronModelConfigNetsynapsesBase(BaseModel):
    """No documentation"""


class NeuronModelConfigNetsynapsesBaseExp2Synapse(
    ExpTwoSynapse, NeuronModelConfigNetsynapsesBase, BaseModel
):
    """No documentation"""

    typename: Literal["Exp2Synapse"] = Field(
        alias="__typename", default="Exp2Synapse", exclude=True
    )


class NeuronModelConfigNetsynapsesBaseCatchAll(
    NeuronModelConfigNetsynapsesBase, BaseModel
):
    """Catch all class for NeuronModelConfigNetsynapsesBase"""

    typename: str = Field(alias="__typename", exclude=True)


class NeuronModelConfigNetconnectionsBase(BaseModel):
    """No documentation"""


class NeuronModelConfigNetconnectionsBaseSynapticConnection(
    SynapticConnection, NeuronModelConfigNetconnectionsBase, BaseModel
):
    """No documentation"""

    typename: Literal["SynapticConnection"] = Field(
        alias="__typename", default="SynapticConnection", exclude=True
    )


class NeuronModelConfigNetconnectionsBaseCatchAll(
    NeuronModelConfigNetconnectionsBase, BaseModel
):
    """Catch all class for NeuronModelConfigNetconnectionsBase"""

    typename: str = Field(alias="__typename", exclude=True)


class NeuronModelConfig(ModelConfigTrait, BaseModel):
    """No documentation"""

    typename: Literal["ModelConfig"] = Field(
        alias="__typename", default="ModelConfig", exclude=True
    )
    v_init: float = Field(alias="vInit")
    celsius: float
    cells: List[Cell]
    net_synapses: Optional[
        List[
            Union[
                Annotated[
                    Union[NeuronModelConfigNetsynapsesBaseExp2Synapse,],
                    Field(discriminator="typename"),
                ],
                NeuronModelConfigNetsynapsesBaseCatchAll,
            ]
        ]
    ] = Field(default=None, alias="netSynapses")
    net_connections: Optional[
        List[
            Union[
                Annotated[
                    Union[NeuronModelConfigNetconnectionsBaseSynapticConnection,],
                    Field(discriminator="typename"),
                ],
                NeuronModelConfigNetconnectionsBaseCatchAll,
            ]
        ]
    ] = Field(default=None, alias="netConnections")
    net_stimulators: Optional[List[NetStimulator]] = Field(
        default=None, alias="netStimulators"
    )


class NeuronModel(BaseModel):
    """No documentation"""

    typename: Literal["NeuronModel"] = Field(
        alias="__typename", default="NeuronModel", exclude=True
    )
    id: ID
    name: str
    config: NeuronModelConfig

    class Meta:
        """Meta class for NeuronModel"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
        name = "NeuronModel"
        type = "NeuronModel"


class AnalogSignal(BaseModel):
    """No documentation"""

    typename: Literal["AnalogSignal"] = Field(
        alias="__typename", default="AnalogSignal", exclude=True
    )
    id: ID
    unit: Optional[str] = Field(default=None)
    channels: List[AnalogSignalChannel]

    class Meta:
        """Meta class for AnalogSignal"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignalChannel on AnalogSignalChannel {\n  id\n  index\n  trace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignal on AnalogSignal {\n  id\n  unit\n  channels {\n    ...AnalogSignalChannel\n    __typename\n  }\n  __typename\n}"
        name = "AnalogSignal"
        type = "AnalogSignal"


class Simulation(BaseModel):
    """No documentation"""

    typename: Literal["Simulation"] = Field(
        alias="__typename", default="Simulation", exclude=True
    )
    id: ID
    model: NeuronModel
    duration: int
    recordings: List[Recording]
    stimuli: List[Stimulus]
    time_trace: Trace = Field(alias="timeTrace")

    class Meta:
        """Meta class for Simulation"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}"
        name = "Simulation"
        type = "Simulation"


class BlockSegment(BaseModel):
    """No documentation"""

    typename: Literal["BlockSegment"] = Field(
        alias="__typename", default="BlockSegment", exclude=True
    )
    id: ID
    analog_signals: List[AnalogSignal] = Field(alias="analogSignals")
    "The analog signals in this group"

    class Meta:
        """Meta class for BlockSegment"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignalChannel on AnalogSignalChannel {\n  id\n  index\n  trace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignal on AnalogSignal {\n  id\n  unit\n  channels {\n    ...AnalogSignalChannel\n    __typename\n  }\n  __typename\n}\n\nfragment BlockSegment on BlockSegment {\n  id\n  analogSignals {\n    ...AnalogSignal\n    __typename\n  }\n  __typename\n}"
        name = "BlockSegment"
        type = "BlockSegment"


class Block(BaseModel):
    """No documentation"""

    typename: Literal["Block"] = Field(
        alias="__typename", default="Block", exclude=True
    )
    id: ID
    segments: List[BlockSegment]
    "The segments in this recording session"
    groups: List[BlockGroup]
    "The groups in this recording session"

    class Meta:
        """Meta class for Block"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignalChannel on AnalogSignalChannel {\n  id\n  index\n  trace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignal on AnalogSignal {\n  id\n  unit\n  channels {\n    ...AnalogSignalChannel\n    __typename\n  }\n  __typename\n}\n\nfragment BlockGroup on BlockGroup {\n  id\n  name\n  __typename\n}\n\nfragment BlockSegment on BlockSegment {\n  id\n  analogSignals {\n    ...AnalogSignal\n    __typename\n  }\n  __typename\n}\n\nfragment Block on Block {\n  id\n  segments {\n    ...BlockSegment\n    __typename\n  }\n  groups {\n    ...BlockGroup\n    __typename\n  }\n  __typename\n}"
        name = "Block"
        type = "Block"


class CreateBlockMutation(BaseModel):
    """No documentation found for this operation."""

    create_block: Block = Field(alias="createBlock")
    "Create a new block"

    class Arguments(BaseModel):
        """Arguments for CreateBlock"""

        input: CreateBlockInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateBlock"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignalChannel on AnalogSignalChannel {\n  id\n  index\n  trace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignal on AnalogSignal {\n  id\n  unit\n  channels {\n    ...AnalogSignalChannel\n    __typename\n  }\n  __typename\n}\n\nfragment BlockGroup on BlockGroup {\n  id\n  name\n  __typename\n}\n\nfragment BlockSegment on BlockSegment {\n  id\n  analogSignals {\n    ...AnalogSignal\n    __typename\n  }\n  __typename\n}\n\nfragment Block on Block {\n  id\n  segments {\n    ...BlockSegment\n    __typename\n  }\n  groups {\n    ...BlockGroup\n    __typename\n  }\n  __typename\n}\n\nmutation CreateBlock($input: CreateBlockInput!) {\n  createBlock(input: $input) {\n    ...Block\n    __typename\n  }\n}"


class CreateDatasetMutationCreatedataset(BaseModel):
    """No documentation"""

    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    id: ID
    name: str


class CreateDatasetMutation(BaseModel):
    """No documentation found for this operation."""

    create_dataset: CreateDatasetMutationCreatedataset = Field(alias="createDataset")
    "Create a new dataset to organize data"

    class Arguments(BaseModel):
        """Arguments for CreateDataset"""

        input: CreateDatasetInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateDataset"""

        document = "mutation CreateDataset($input: CreateDatasetInput!) {\n  createDataset(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class UpdateDatasetMutationUpdatedataset(BaseModel):
    """No documentation"""

    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    id: ID
    name: str


class UpdateDatasetMutation(BaseModel):
    """No documentation found for this operation."""

    update_dataset: UpdateDatasetMutationUpdatedataset = Field(alias="updateDataset")
    "Update dataset metadata"

    class Arguments(BaseModel):
        """Arguments for UpdateDataset"""

        input: ChangeDatasetInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateDataset"""

        document = "mutation UpdateDataset($input: ChangeDatasetInput!) {\n  updateDataset(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class RevertDatasetMutationRevertdataset(BaseModel):
    """No documentation"""

    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    id: ID
    name: str
    description: Optional[str] = Field(default=None)


class RevertDatasetMutation(BaseModel):
    """No documentation found for this operation."""

    revert_dataset: RevertDatasetMutationRevertdataset = Field(alias="revertDataset")
    "Revert dataset to a previous version"

    class Arguments(BaseModel):
        """Arguments for RevertDataset"""

        input: RevertInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RevertDataset"""

        document = "mutation RevertDataset($input: RevertInput!) {\n  revertDataset(input: $input) {\n    id\n    name\n    description\n    __typename\n  }\n}"


class CreateExperimentMutation(BaseModel):
    """No documentation found for this operation."""

    create_experiment: Experiment = Field(alias="createExperiment")
    "Create a new experiment"

    class Arguments(BaseModel):
        """Arguments for CreateExperiment"""

        input: CreateExperimentInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateExperiment"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Experiment on Experiment {\n  name\n  id\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  recordingViews {\n    label\n    recording {\n      ...Recording\n      __typename\n    }\n    __typename\n  }\n  stimulusViews {\n    label\n    stimulus {\n      ...Stimulus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation CreateExperiment($input: CreateExperimentInput!) {\n  createExperiment(input: $input) {\n    ...Experiment\n    __typename\n  }\n}"


class From_file_likeMutation(BaseModel):
    """No documentation found for this operation."""

    from_file_like: File = Field(alias="fromFileLike")
    "Create a file from file-like data"

    class Arguments(BaseModel):
        """Arguments for from_file_like"""

        input: FromFileLike
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for from_file_like"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nmutation from_file_like($input: FromFileLike!) {\n  fromFileLike(input: $input) {\n    ...File\n    __typename\n  }\n}"


class RequestFileUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_file_upload: Credentials = Field(alias="requestFileUpload")
    "Request credentials to upload a new file"

    class Arguments(BaseModel):
        """Arguments for RequestFileUpload"""

        input: RequestFileUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestFileUpload"""

        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n  __typename\n}\n\nmutation RequestFileUpload($input: RequestFileUploadInput!) {\n  requestFileUpload(input: $input) {\n    ...Credentials\n    __typename\n  }\n}"


class RequestFileAccessMutation(BaseModel):
    """No documentation found for this operation."""

    request_file_access: AccessCredentials = Field(alias="requestFileAccess")
    "Request credentials to access a file"

    class Arguments(BaseModel):
        """Arguments for RequestFileAccess"""

        input: RequestFileAccessInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestFileAccess"""

        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n  __typename\n}\n\nmutation RequestFileAccess($input: RequestFileAccessInput!) {\n  requestFileAccess(input: $input) {\n    ...AccessCredentials\n    __typename\n  }\n}"


class CreateModelCollectionMutation(BaseModel):
    """No documentation found for this operation."""

    create_model_collection: ModelCollection = Field(alias="createModelCollection")
    "Create a new model collection"

    class Arguments(BaseModel):
        """Arguments for CreateModelCollection"""

        input: CreateModelCollectionInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateModelCollection"""

        document = "fragment ModelCollection on ModelCollection {\n  name\n  id\n  models {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nmutation CreateModelCollection($input: CreateModelCollectionInput!) {\n  createModelCollection(input: $input) {\n    ...ModelCollection\n    __typename\n  }\n}"


class CreateNeuronmodelMutation(BaseModel):
    """No documentation found for this operation."""

    create_neuron_model: NeuronModel = Field(alias="createNeuronModel")
    "Create a new neuron model"

    class Arguments(BaseModel):
        """Arguments for CreateNeuronmodel"""

        input: CreateNeuronModelInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateNeuronmodel"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation CreateNeuronmodel($input: CreateNeuronModelInput!) {\n  createNeuronModel(input: $input) {\n    ...NeuronModel\n    __typename\n  }\n}"


class CreateRoiMutation(BaseModel):
    """No documentation found for this operation."""

    create_roi: ROI = Field(alias="createRoi")
    "Create a new region of interest"

    class Arguments(BaseModel):
        """Arguments for CreateRoi"""

        input: RoiInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateRoi"""

        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nmutation CreateRoi($input: RoiInput!) {\n  createRoi(input: $input) {\n    ...ROI\n    __typename\n  }\n}"


class DeleteRoiMutation(BaseModel):
    """No documentation found for this operation."""

    delete_roi: ID = Field(alias="deleteRoi")
    "Delete an existing region of interest"

    class Arguments(BaseModel):
        """Arguments for DeleteRoi"""

        input: DeleteRoiInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DeleteRoi"""

        document = "mutation DeleteRoi($input: DeleteRoiInput!) {\n  deleteRoi(input: $input)\n}"


class UpdateRoiMutation(BaseModel):
    """No documentation found for this operation."""

    update_roi: ROI = Field(alias="updateRoi")
    "Update an existing region of interest"

    class Arguments(BaseModel):
        """Arguments for UpdateRoi"""

        input: UpdateRoiInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateRoi"""

        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nmutation UpdateRoi($input: UpdateRoiInput!) {\n  updateRoi(input: $input) {\n    ...ROI\n    __typename\n  }\n}"


class CreateSimulationMutation(BaseModel):
    """No documentation found for this operation."""

    create_simulation: Simulation = Field(alias="createSimulation")
    "Create a new simulsation"

    class Arguments(BaseModel):
        """Arguments for CreateSimulation"""

        input: CreateSimulationInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateSimulation"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nmutation CreateSimulation($input: CreateSimulationInput!) {\n  createSimulation(input: $input) {\n    ...Simulation\n    __typename\n  }\n}"


class FromTraceLikeMutation(BaseModel):
    """No documentation found for this operation."""

    from_trace_like: Trace = Field(alias="fromTraceLike")
    "Create an image from array-like data"

    class Arguments(BaseModel):
        """Arguments for FromTraceLike"""

        input: FromTraceLikeInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for FromTraceLike"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nmutation FromTraceLike($input: FromTraceLikeInput!) {\n  fromTraceLike(input: $input) {\n    ...Trace\n    __typename\n  }\n}"


class RequestUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_upload: Credentials = Field(alias="requestUpload")
    "Request credentials to upload a new image"

    class Arguments(BaseModel):
        """Arguments for RequestUpload"""

        input: RequestUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestUpload"""

        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n  __typename\n}\n\nmutation RequestUpload($input: RequestUploadInput!) {\n  requestUpload(input: $input) {\n    ...Credentials\n    __typename\n  }\n}"


class RequestAccessMutation(BaseModel):
    """No documentation found for this operation."""

    request_access: AccessCredentials = Field(alias="requestAccess")
    "Request credentials to access an image"

    class Arguments(BaseModel):
        """Arguments for RequestAccess"""

        input: RequestAccessInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestAccess"""

        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n  __typename\n}\n\nmutation RequestAccess($input: RequestAccessInput!) {\n  requestAccess(input: $input) {\n    ...AccessCredentials\n    __typename\n  }\n}"


class GetDatasetQuery(BaseModel):
    """No documentation found for this operation."""

    dataset: Dataset

    class Arguments(BaseModel):
        """Arguments for GetDataset"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetDataset"""

        document = "fragment Dataset on Dataset {\n  name\n  description\n  __typename\n}\n\nquery GetDataset($id: ID!) {\n  dataset(id: $id) {\n    ...Dataset\n    __typename\n  }\n}"


class GetExperimentQuery(BaseModel):
    """No documentation found for this operation."""

    experiment: Experiment

    class Arguments(BaseModel):
        """Arguments for GetExperiment"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetExperiment"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Experiment on Experiment {\n  name\n  id\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  recordingViews {\n    label\n    recording {\n      ...Recording\n      __typename\n    }\n    __typename\n  }\n  stimulusViews {\n    label\n    stimulus {\n      ...Stimulus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetExperiment($id: ID!) {\n  experiment(id: $id) {\n    ...Experiment\n    __typename\n  }\n}"


class SearchExperimentsQueryOptions(ExperimentTrait, BaseModel):
    """No documentation"""

    typename: Literal["Experiment"] = Field(
        alias="__typename", default="Experiment", exclude=True
    )
    value: ID
    label: str


class SearchExperimentsQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchExperimentsQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchExperiments"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchExperiments"""

        document = "query SearchExperiments($search: String, $values: [ID!]) {\n  options: experiments(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListExperimentsQuery(BaseModel):
    """No documentation found for this operation."""

    experiments: List[Experiment]

    class Arguments(BaseModel):
        """Arguments for ListExperiments"""

        filter: Optional[ExperimentFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListExperiments"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Experiment on Experiment {\n  name\n  id\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  recordingViews {\n    label\n    recording {\n      ...Recording\n      __typename\n    }\n    __typename\n  }\n  stimulusViews {\n    label\n    stimulus {\n      ...Stimulus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery ListExperiments($filter: ExperimentFilter, $pagination: OffsetPaginationInput) {\n  experiments(filters: $filter, pagination: $pagination) {\n    ...Experiment\n    __typename\n  }\n}"


class GetFileQuery(BaseModel):
    """No documentation found for this operation."""

    file: File

    class Arguments(BaseModel):
        """Arguments for GetFile"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetFile"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nquery GetFile($id: ID!) {\n  file(id: $id) {\n    ...File\n    __typename\n  }\n}"


class SearchFilesQueryOptions(BaseModel):
    """No documentation"""

    typename: Literal["File"] = Field(alias="__typename", default="File", exclude=True)
    value: ID
    label: str


class SearchFilesQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchFilesQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchFiles"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchFiles"""

        document = "query SearchFiles($search: String, $values: [ID!], $pagination: OffsetPaginationInput) {\n  options: files(\n    filters: {search: $search, ids: $values}\n    pagination: $pagination\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetModelCollectionQuery(BaseModel):
    """No documentation found for this operation."""

    model_collection: ModelCollection = Field(alias="modelCollection")

    class Arguments(BaseModel):
        """Arguments for GetModelCollection"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetModelCollection"""

        document = "fragment ModelCollection on ModelCollection {\n  name\n  id\n  models {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nquery GetModelCollection($id: ID!) {\n  modelCollection(id: $id) {\n    ...ModelCollection\n    __typename\n  }\n}"


class SearchModelCollectionQueryOptions(BaseModel):
    """No documentation"""

    typename: Literal["ModelCollection"] = Field(
        alias="__typename", default="ModelCollection", exclude=True
    )
    value: ID
    label: str


class SearchModelCollectionQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchModelCollectionQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchModelCollection"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchModelCollection"""

        document = "query SearchModelCollection($search: String, $values: [ID!]) {\n  options: modelCollections(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListModelCollectionsQuery(BaseModel):
    """No documentation found for this operation."""

    model_collections: List[ModelCollection] = Field(alias="modelCollections")

    class Arguments(BaseModel):
        """Arguments for ListModelCollections"""

        filter: Optional[ModelCollectionFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListModelCollections"""

        document = "fragment ModelCollection on ModelCollection {\n  name\n  id\n  models {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nquery ListModelCollections($filter: ModelCollectionFilter, $pagination: OffsetPaginationInput) {\n  modelCollections(filters: $filter, pagination: $pagination) {\n    ...ModelCollection\n    __typename\n  }\n}"


class GetNeuronModelQuery(BaseModel):
    """No documentation found for this operation."""

    neuron_model: NeuronModel = Field(alias="neuronModel")
    "Returns a single image by ID"

    class Arguments(BaseModel):
        """Arguments for GetNeuronModel"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetNeuronModel"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetNeuronModel($id: ID!) {\n  neuronModel(id: $id) {\n    ...NeuronModel\n    __typename\n  }\n}"


class SearchNeuronModelsQueryOptions(BaseModel):
    """No documentation"""

    typename: Literal["NeuronModel"] = Field(
        alias="__typename", default="NeuronModel", exclude=True
    )
    value: ID
    label: str


class SearchNeuronModelsQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchNeuronModelsQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchNeuronModels"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchNeuronModels"""

        document = "query SearchNeuronModels($search: String, $values: [ID!]) {\n  options: neuronModels(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListNeuronModelsQuery(BaseModel):
    """No documentation found for this operation."""

    neuron_models: List[NeuronModel] = Field(alias="neuronModels")

    class Arguments(BaseModel):
        """Arguments for ListNeuronModels"""

        filter: Optional[NeuronModelFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListNeuronModels"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery ListNeuronModels($filter: NeuronModelFilter, $pagination: OffsetPaginationInput) {\n  neuronModels(filters: $filter, pagination: $pagination) {\n    ...NeuronModel\n    __typename\n  }\n}"


class GetRecordingQuery(BaseModel):
    """No documentation found for this operation."""

    recording: Recording
    "Returns a list of images"

    class Arguments(BaseModel):
        """Arguments for GetRecording"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetRecording"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetRecording($id: ID!) {\n  recording(id: $id) {\n    ...Recording\n    __typename\n  }\n}"


class SearchRecordingsQueryOptions(BaseModel):
    """No documentation"""

    typename: Literal["Recording"] = Field(
        alias="__typename", default="Recording", exclude=True
    )
    value: ID
    label: str


class SearchRecordingsQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchRecordingsQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchRecordings"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchRecordings"""

        document = "query SearchRecordings($search: String, $values: [ID!]) {\n  options: recordings(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListRecordingsQuery(BaseModel):
    """No documentation found for this operation."""

    recordings: List[Recording]

    class Arguments(BaseModel):
        """Arguments for ListRecordings"""

        filter: Optional[RecordingFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListRecordings"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery ListRecordings($filter: RecordingFilter, $pagination: OffsetPaginationInput) {\n  recordings(filters: $filter, pagination: $pagination) {\n    ...Recording\n    __typename\n  }\n}"


class GetRoisQuery(BaseModel):
    """No documentation found for this operation."""

    rois: List[ROI]

    class Arguments(BaseModel):
        """Arguments for GetRois"""

        trace: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetRois"""

        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nquery GetRois($trace: ID!) {\n  rois(filters: {trace: $trace}) {\n    ...ROI\n    __typename\n  }\n}"


class GetRoiQuery(BaseModel):
    """No documentation found for this operation."""

    roi: ROI

    class Arguments(BaseModel):
        """Arguments for GetRoi"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetRoi"""

        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nquery GetRoi($id: ID!) {\n  roi(id: $id) {\n    ...ROI\n    __typename\n  }\n}"


class SearchRoisQueryOptions(IsVectorizableTrait, BaseModel):
    """No documentation"""

    typename: Literal["ROI"] = Field(alias="__typename", default="ROI", exclude=True)
    value: ID
    label: str


class SearchRoisQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchRoisQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchRois"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchRois"""

        document = "query SearchRois($search: String, $values: [ID!]) {\n  options: rois(filters: {search: $search, ids: $values}, pagination: {limit: 10}) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetSimulationQuery(BaseModel):
    """No documentation found for this operation."""

    simulation: Simulation

    class Arguments(BaseModel):
        """Arguments for GetSimulation"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetSimulation"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nquery GetSimulation($id: ID!) {\n  simulation(id: $id) {\n    ...Simulation\n    __typename\n  }\n}"


class SearchSimulationsQueryOptions(BaseModel):
    """No documentation"""

    typename: Literal["Simulation"] = Field(
        alias="__typename", default="Simulation", exclude=True
    )
    value: ID
    label: str


class SearchSimulationsQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchSimulationsQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchSimulations"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchSimulations"""

        document = "query SearchSimulations($search: String, $values: [ID!]) {\n  options: simulations(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListSimulationsQuery(BaseModel):
    """No documentation found for this operation."""

    simulations: List[Simulation]

    class Arguments(BaseModel):
        """Arguments for ListSimulations"""

        filter: Optional[SimulationFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListSimulations"""

        document = "fragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nquery ListSimulations($filter: SimulationFilter, $pagination: OffsetPaginationInput) {\n  simulations(filters: $filter, pagination: $pagination) {\n    ...Simulation\n    __typename\n  }\n}"


class GetStimulusQuery(BaseModel):
    """No documentation found for this operation."""

    stimulus: Stimulus
    "Returns a list of images"

    class Arguments(BaseModel):
        """Arguments for GetStimulus"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetStimulus"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetStimulus($id: ID!) {\n  stimulus(id: $id) {\n    ...Stimulus\n    __typename\n  }\n}"


class SearchStimuliQueryOptions(BaseModel):
    """No documentation"""

    typename: Literal["Stimulus"] = Field(
        alias="__typename", default="Stimulus", exclude=True
    )
    value: ID
    label: str


class SearchStimuliQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchStimuliQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchStimuli"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchStimuli"""

        document = "query SearchStimuli($search: String, $values: [ID!]) {\n  options: stimuli(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n    __typename\n  }\n}"


class ListStimuliQuery(BaseModel):
    """No documentation found for this operation."""

    stimuli: List[Stimulus]

    class Arguments(BaseModel):
        """Arguments for ListStimuli"""

        filter: Optional[StimulusFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListStimuli"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery ListStimuli($filter: StimulusFilter, $pagination: OffsetPaginationInput) {\n  stimuli(filters: $filter, pagination: $pagination) {\n    ...Stimulus\n    __typename\n  }\n}"


class GetTraceQuery(BaseModel):
    """No documentation found for this operation."""

    trace: Trace
    "Returns a single image by ID"

    class Arguments(BaseModel):
        """Arguments for GetTrace"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetTrace"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nquery GetTrace($id: ID!) {\n  trace(id: $id) {\n    ...Trace\n    __typename\n  }\n}"


class GetRandomTraceQuery(BaseModel):
    """No documentation found for this operation."""

    random_trace: Trace = Field(alias="randomTrace")

    class Arguments(BaseModel):
        """Arguments for GetRandomTrace"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetRandomTrace"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nquery GetRandomTrace {\n  randomTrace {\n    ...Trace\n    __typename\n  }\n}"


class SearchTracesQueryOptions(HasZarrStoreTrait, BaseModel):
    """No documentation"""

    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    value: ID
    label: str
    "The name of the image"


class SearchTracesQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchTracesQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchTraces"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchTraces"""

        document = "query SearchTraces($search: String, $values: [ID!]) {\n  options: traces(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListTracesQuery(BaseModel):
    """No documentation found for this operation."""

    traces: List[Trace]

    class Arguments(BaseModel):
        """Arguments for ListTraces"""

        filter: Optional[TraceFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListTraces"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nquery ListTraces($filter: TraceFilter, $pagination: OffsetPaginationInput) {\n  traces(filters: $filter, pagination: $pagination) {\n    ...Trace\n    __typename\n  }\n}"


class WatchFilesSubscriptionFiles(BaseModel):
    """No documentation"""

    typename: Literal["FileEvent"] = Field(
        alias="__typename", default="FileEvent", exclude=True
    )
    create: Optional[File] = Field(default=None)
    delete: Optional[ID] = Field(default=None)
    update: Optional[File] = Field(default=None)


class WatchFilesSubscription(BaseModel):
    """No documentation found for this operation."""

    files: WatchFilesSubscriptionFiles
    "Subscribe to real-time file updates"

    class Arguments(BaseModel):
        """Arguments for WatchFiles"""

        dataset: Optional[ID] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for WatchFiles"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nsubscription WatchFiles($dataset: ID) {\n  files(dataset: $dataset) {\n    create {\n      ...File\n      __typename\n    }\n    delete\n    update {\n      ...File\n      __typename\n    }\n    __typename\n  }\n}"


class WatchRoisSubscriptionRois(BaseModel):
    """No documentation"""

    typename: Literal["RoiEvent"] = Field(
        alias="__typename", default="RoiEvent", exclude=True
    )
    create: Optional[ROI] = Field(default=None)
    delete: Optional[ID] = Field(default=None)
    update: Optional[ROI] = Field(default=None)


class WatchRoisSubscription(BaseModel):
    """No documentation found for this operation."""

    rois: WatchRoisSubscriptionRois
    "Subscribe to real-time ROI updates"

    class Arguments(BaseModel):
        """Arguments for WatchRois"""

        trace: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for WatchRois"""

        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nsubscription WatchRois($trace: ID!) {\n  rois(trace: $trace) {\n    create {\n      ...ROI\n      __typename\n    }\n    delete\n    update {\n      ...ROI\n      __typename\n    }\n    __typename\n  }\n}"


class WatchTracesSubscriptionTraces(BaseModel):
    """No documentation"""

    typename: Literal["TraceEvent"] = Field(
        alias="__typename", default="TraceEvent", exclude=True
    )
    create: Optional[Trace] = Field(default=None)
    delete: Optional[ID] = Field(default=None)
    update: Optional[Trace] = Field(default=None)


class WatchTracesSubscription(BaseModel):
    """No documentation found for this operation."""

    traces: WatchTracesSubscriptionTraces
    "Subscribe to real-time image updates"

    class Arguments(BaseModel):
        """Arguments for WatchTraces"""

        dataset: Optional[ID] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for WatchTraces"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nsubscription WatchTraces($dataset: ID) {\n  traces(dataset: $dataset) {\n    create {\n      ...Trace\n      __typename\n    }\n    delete\n    update {\n      ...Trace\n      __typename\n    }\n    __typename\n  }\n}"


async def acreate_block(
    name: str,
    segments: Iterable[BlockSegmentInput],
    file: Optional[IDCoercible] = None,
    recording_time: Optional[datetime] = None,
    rath: Optional[ElektroRath] = None,
) -> Block:
    """CreateBlock

    Create a new block

    Args:
        file: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        recording_time: Date with time (isoformat)
        segments:  (required) (list) (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Block
    """
    return (
        await aexecute(
            CreateBlockMutation,
            {
                "input": {
                    "file": file,
                    "name": name,
                    "recordingTime": recording_time,
                    "segments": segments,
                }
            },
            rath=rath,
        )
    ).create_block


def create_block(
    name: str,
    segments: Iterable[BlockSegmentInput],
    file: Optional[IDCoercible] = None,
    recording_time: Optional[datetime] = None,
    rath: Optional[ElektroRath] = None,
) -> Block:
    """CreateBlock

    Create a new block

    Args:
        file: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        recording_time: Date with time (isoformat)
        segments:  (required) (list) (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Block
    """
    return execute(
        CreateBlockMutation,
        {
            "input": {
                "file": file,
                "name": name,
                "recordingTime": recording_time,
                "segments": segments,
            }
        },
        rath=rath,
    ).create_block


async def acreate_dataset(
    name: str, rath: Optional[ElektroRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset

    Create a new dataset to organize data

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        CreateDatasetMutationCreatedataset
    """
    return (
        await aexecute(CreateDatasetMutation, {"input": {"name": name}}, rath=rath)
    ).create_dataset


def create_dataset(
    name: str, rath: Optional[ElektroRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset

    Create a new dataset to organize data

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        CreateDatasetMutationCreatedataset
    """
    return execute(
        CreateDatasetMutation, {"input": {"name": name}}, rath=rath
    ).create_dataset


async def aupdate_dataset(
    name: str, id: IDCoercible, rath: Optional[ElektroRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset

    Update dataset metadata

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        UpdateDatasetMutationUpdatedataset
    """
    return (
        await aexecute(
            UpdateDatasetMutation, {"input": {"name": name, "id": id}}, rath=rath
        )
    ).update_dataset


def update_dataset(
    name: str, id: IDCoercible, rath: Optional[ElektroRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset

    Update dataset metadata

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        UpdateDatasetMutationUpdatedataset
    """
    return execute(
        UpdateDatasetMutation, {"input": {"name": name, "id": id}}, rath=rath
    ).update_dataset


async def arevert_dataset(
    id: IDCoercible, history_id: IDCoercible, rath: Optional[ElektroRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset

    Revert dataset to a previous version

    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        history_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        RevertDatasetMutationRevertdataset
    """
    return (
        await aexecute(
            RevertDatasetMutation,
            {"input": {"id": id, "historyId": history_id}},
            rath=rath,
        )
    ).revert_dataset


def revert_dataset(
    id: IDCoercible, history_id: IDCoercible, rath: Optional[ElektroRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset

    Revert dataset to a previous version

    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        history_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        RevertDatasetMutationRevertdataset
    """
    return execute(
        RevertDatasetMutation, {"input": {"id": id, "historyId": history_id}}, rath=rath
    ).revert_dataset


async def acreate_experiment(
    name: str,
    stimulus_views: Iterable[StimulusViewInput],
    recording_views: Iterable[RecordingViewInput],
    time_trace: Optional[IDCoercible] = None,
    description: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> Experiment:
    """CreateExperiment

    Create a new experiment

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        time_trace: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        stimulus_views:  (required) (list) (required)
        recording_views:  (required) (list) (required)
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Experiment
    """
    return (
        await aexecute(
            CreateExperimentMutation,
            {
                "input": {
                    "name": name,
                    "timeTrace": time_trace,
                    "stimulusViews": stimulus_views,
                    "recordingViews": recording_views,
                    "description": description,
                }
            },
            rath=rath,
        )
    ).create_experiment


def create_experiment(
    name: str,
    stimulus_views: Iterable[StimulusViewInput],
    recording_views: Iterable[RecordingViewInput],
    time_trace: Optional[IDCoercible] = None,
    description: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> Experiment:
    """CreateExperiment

    Create a new experiment

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        time_trace: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        stimulus_views:  (required) (list) (required)
        recording_views:  (required) (list) (required)
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Experiment
    """
    return execute(
        CreateExperimentMutation,
        {
            "input": {
                "name": name,
                "timeTrace": time_trace,
                "stimulusViews": stimulus_views,
                "recordingViews": recording_views,
                "description": description,
            }
        },
        rath=rath,
    ).create_experiment


async def afrom_file_like(
    name: str,
    file: FileLike,
    origins: Optional[Iterable[IDCoercible]] = None,
    dataset: Optional[IDCoercible] = None,
    rath: Optional[ElektroRath] = None,
) -> File:
    """from_file_like

    Create a file from file-like data

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        file: The `FileLike` scalar type represents a reference to a big file storage previously created by the user n a datalayer (required)
        origins: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        dataset: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        File
    """
    return (
        await aexecute(
            From_file_likeMutation,
            {
                "input": {
                    "name": name,
                    "file": file,
                    "origins": origins,
                    "dataset": dataset,
                }
            },
            rath=rath,
        )
    ).from_file_like


def from_file_like(
    name: str,
    file: FileLike,
    origins: Optional[Iterable[IDCoercible]] = None,
    dataset: Optional[IDCoercible] = None,
    rath: Optional[ElektroRath] = None,
) -> File:
    """from_file_like

    Create a file from file-like data

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        file: The `FileLike` scalar type represents a reference to a big file storage previously created by the user n a datalayer (required)
        origins: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        dataset: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        File
    """
    return execute(
        From_file_likeMutation,
        {"input": {"name": name, "file": file, "origins": origins, "dataset": dataset}},
        rath=rath,
    ).from_file_like


async def arequest_file_upload(
    key: str, datalayer: str, rath: Optional[ElektroRath] = None
) -> Credentials:
    """RequestFileUpload

    Request credentials to upload a new file

    Args:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Credentials
    """
    return (
        await aexecute(
            RequestFileUploadMutation,
            {"input": {"key": key, "datalayer": datalayer}},
            rath=rath,
        )
    ).request_file_upload


def request_file_upload(
    key: str, datalayer: str, rath: Optional[ElektroRath] = None
) -> Credentials:
    """RequestFileUpload

    Request credentials to upload a new file

    Args:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Credentials
    """
    return execute(
        RequestFileUploadMutation,
        {"input": {"key": key, "datalayer": datalayer}},
        rath=rath,
    ).request_file_upload


async def arequest_file_access(
    store: IDCoercible,
    duration: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> AccessCredentials:
    """RequestFileAccess

    Request credentials to access a file

    Args:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        AccessCredentials
    """
    return (
        await aexecute(
            RequestFileAccessMutation,
            {"input": {"store": store, "duration": duration}},
            rath=rath,
        )
    ).request_file_access


def request_file_access(
    store: IDCoercible,
    duration: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> AccessCredentials:
    """RequestFileAccess

    Request credentials to access a file

    Args:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        AccessCredentials
    """
    return execute(
        RequestFileAccessMutation,
        {"input": {"store": store, "duration": duration}},
        rath=rath,
    ).request_file_access


async def acreate_model_collection(
    name: str,
    models: Iterable[IDCoercible],
    description: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> ModelCollection:
    """CreateModelCollection

    Create a new model collection

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        models: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ModelCollection
    """
    return (
        await aexecute(
            CreateModelCollectionMutation,
            {"input": {"name": name, "models": models, "description": description}},
            rath=rath,
        )
    ).create_model_collection


def create_model_collection(
    name: str,
    models: Iterable[IDCoercible],
    description: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> ModelCollection:
    """CreateModelCollection

    Create a new model collection

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        models: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list) (required)
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ModelCollection
    """
    return execute(
        CreateModelCollectionMutation,
        {"input": {"name": name, "models": models, "description": description}},
        rath=rath,
    ).create_model_collection


async def acreate_neuronmodel(
    name: str,
    config: ModelConfigInput,
    parent: Optional[IDCoercible] = None,
    rath: Optional[ElektroRath] = None,
) -> NeuronModel:
    """CreateNeuronmodel

    Create a new neuron model

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        parent: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        config:  (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        NeuronModel
    """
    return (
        await aexecute(
            CreateNeuronmodelMutation,
            {"input": {"name": name, "parent": parent, "config": config}},
            rath=rath,
        )
    ).create_neuron_model


def create_neuronmodel(
    name: str,
    config: ModelConfigInput,
    parent: Optional[IDCoercible] = None,
    rath: Optional[ElektroRath] = None,
) -> NeuronModel:
    """CreateNeuronmodel

    Create a new neuron model

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        parent: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        config:  (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        NeuronModel
    """
    return execute(
        CreateNeuronmodelMutation,
        {"input": {"name": name, "parent": parent, "config": config}},
        rath=rath,
    ).create_neuron_model


async def acreate_roi(
    trace: IDCoercible,
    vectors: Iterable[TwoDVector],
    kind: RoiKind,
    label: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> ROI:
    """CreateRoi

    Create a new region of interest

    Args:
        trace: The image this ROI belongs to
        vectors: The vector coordinates defining the as XY
        kind: The type/kind of ROI
        label: The label of the ROI
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ROI
    """
    return (
        await aexecute(
            CreateRoiMutation,
            {
                "input": {
                    "trace": trace,
                    "vectors": vectors,
                    "kind": kind,
                    "label": label,
                }
            },
            rath=rath,
        )
    ).create_roi


def create_roi(
    trace: IDCoercible,
    vectors: Iterable[TwoDVector],
    kind: RoiKind,
    label: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> ROI:
    """CreateRoi

    Create a new region of interest

    Args:
        trace: The image this ROI belongs to
        vectors: The vector coordinates defining the as XY
        kind: The type/kind of ROI
        label: The label of the ROI
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ROI
    """
    return execute(
        CreateRoiMutation,
        {"input": {"trace": trace, "vectors": vectors, "kind": kind, "label": label}},
        rath=rath,
    ).create_roi


async def adelete_roi(id: IDCoercible, rath: Optional[ElektroRath] = None) -> ID:
    """DeleteRoi

    Delete an existing region of interest

    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ID
    """
    return (
        await aexecute(DeleteRoiMutation, {"input": {"id": id}}, rath=rath)
    ).delete_roi


def delete_roi(id: IDCoercible, rath: Optional[ElektroRath] = None) -> ID:
    """DeleteRoi

    Delete an existing region of interest

    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ID
    """
    return execute(DeleteRoiMutation, {"input": {"id": id}}, rath=rath).delete_roi


async def aupdate_roi(
    roi: IDCoercible,
    label: Optional[str] = None,
    vectors: Optional[Iterable[TwoDVector]] = None,
    kind: Optional[RoiKind] = None,
    rath: Optional[ElektroRath] = None,
) -> ROI:
    """UpdateRoi

    Update an existing region of interest

    Args:
        roi: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        label: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        vectors: The `Vector` scalar type represents a matrix values as specified by (required) (list)
        kind: RoiKind
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ROI
    """
    return (
        await aexecute(
            UpdateRoiMutation,
            {"input": {"roi": roi, "label": label, "vectors": vectors, "kind": kind}},
            rath=rath,
        )
    ).update_roi


def update_roi(
    roi: IDCoercible,
    label: Optional[str] = None,
    vectors: Optional[Iterable[TwoDVector]] = None,
    kind: Optional[RoiKind] = None,
    rath: Optional[ElektroRath] = None,
) -> ROI:
    """UpdateRoi

    Update an existing region of interest

    Args:
        roi: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        label: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        vectors: The `Vector` scalar type represents a matrix values as specified by (required) (list)
        kind: RoiKind
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ROI
    """
    return execute(
        UpdateRoiMutation,
        {"input": {"roi": roi, "label": label, "vectors": vectors, "kind": kind}},
        rath=rath,
    ).update_roi


async def acreate_simulation(
    name: str,
    model: IDCoercible,
    recordings: Iterable[RecordingInput],
    stimuli: Iterable[StimulusInput],
    duration: float,
    time_trace: Optional[TraceCoercible] = None,
    dt: Optional[float] = None,
    rath: Optional[ElektroRath] = None,
) -> Simulation:
    """CreateSimulation

    Create a new simulsation

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        model: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        recordings:  (required) (list) (required)
        stimuli:  (required) (list) (required)
        time_trace: The `ArrayLike` scalar type represents a reference to a store previously created by the user n a datalayer
        duration: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point). (required)
        dt: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Simulation
    """
    return (
        await aexecute(
            CreateSimulationMutation,
            {
                "input": {
                    "name": name,
                    "model": model,
                    "recordings": recordings,
                    "stimuli": stimuli,
                    "timeTrace": time_trace,
                    "duration": duration,
                    "dt": dt,
                }
            },
            rath=rath,
        )
    ).create_simulation


def create_simulation(
    name: str,
    model: IDCoercible,
    recordings: Iterable[RecordingInput],
    stimuli: Iterable[StimulusInput],
    duration: float,
    time_trace: Optional[TraceCoercible] = None,
    dt: Optional[float] = None,
    rath: Optional[ElektroRath] = None,
) -> Simulation:
    """CreateSimulation

    Create a new simulsation

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        model: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        recordings:  (required) (list) (required)
        stimuli:  (required) (list) (required)
        time_trace: The `ArrayLike` scalar type represents a reference to a store previously created by the user n a datalayer
        duration: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point). (required)
        dt: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Simulation
    """
    return execute(
        CreateSimulationMutation,
        {
            "input": {
                "name": name,
                "model": model,
                "recordings": recordings,
                "stimuli": stimuli,
                "timeTrace": time_trace,
                "duration": duration,
                "dt": dt,
            }
        },
        rath=rath,
    ).create_simulation


async def afrom_trace_like(
    array: TraceCoercible,
    name: str,
    dataset: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    rath: Optional[ElektroRath] = None,
) -> Trace:
    """FromTraceLike

    Create an image from array-like data

    Args:
        array: The array-like object to create the image from
        name: The name of the image
        dataset: Optional dataset ID to associate the image with
        tags: Optional list of tags to associate with the image
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return (
        await aexecute(
            FromTraceLikeMutation,
            {"input": {"array": array, "name": name, "dataset": dataset, "tags": tags}},
            rath=rath,
        )
    ).from_trace_like


def from_trace_like(
    array: TraceCoercible,
    name: str,
    dataset: Optional[IDCoercible] = None,
    tags: Optional[Iterable[str]] = None,
    rath: Optional[ElektroRath] = None,
) -> Trace:
    """FromTraceLike

    Create an image from array-like data

    Args:
        array: The array-like object to create the image from
        name: The name of the image
        dataset: Optional dataset ID to associate the image with
        tags: Optional list of tags to associate with the image
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return execute(
        FromTraceLikeMutation,
        {"input": {"array": array, "name": name, "dataset": dataset, "tags": tags}},
        rath=rath,
    ).from_trace_like


async def arequest_upload(
    key: str, datalayer: str, rath: Optional[ElektroRath] = None
) -> Credentials:
    """RequestUpload

    Request credentials to upload a new image

    Args:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Credentials
    """
    return (
        await aexecute(
            RequestUploadMutation,
            {"input": {"key": key, "datalayer": datalayer}},
            rath=rath,
        )
    ).request_upload


def request_upload(
    key: str, datalayer: str, rath: Optional[ElektroRath] = None
) -> Credentials:
    """RequestUpload

    Request credentials to upload a new image

    Args:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Credentials
    """
    return execute(
        RequestUploadMutation,
        {"input": {"key": key, "datalayer": datalayer}},
        rath=rath,
    ).request_upload


async def arequest_access(
    store: IDCoercible,
    duration: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> AccessCredentials:
    """RequestAccess

    Request credentials to access an image

    Args:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        AccessCredentials
    """
    return (
        await aexecute(
            RequestAccessMutation,
            {"input": {"store": store, "duration": duration}},
            rath=rath,
        )
    ).request_access


def request_access(
    store: IDCoercible,
    duration: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> AccessCredentials:
    """RequestAccess

    Request credentials to access an image

    Args:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        AccessCredentials
    """
    return execute(
        RequestAccessMutation,
        {"input": {"store": store, "duration": duration}},
        rath=rath,
    ).request_access


async def aget_dataset(id: ID, rath: Optional[ElektroRath] = None) -> Dataset:
    """GetDataset


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Dataset
    """
    return (await aexecute(GetDatasetQuery, {"id": id}, rath=rath)).dataset


def get_dataset(id: ID, rath: Optional[ElektroRath] = None) -> Dataset:
    """GetDataset


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Dataset
    """
    return execute(GetDatasetQuery, {"id": id}, rath=rath).dataset


async def aget_experiment(id: ID, rath: Optional[ElektroRath] = None) -> Experiment:
    """GetExperiment


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Experiment
    """
    return (await aexecute(GetExperimentQuery, {"id": id}, rath=rath)).experiment


def get_experiment(id: ID, rath: Optional[ElektroRath] = None) -> Experiment:
    """GetExperiment


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Experiment
    """
    return execute(GetExperimentQuery, {"id": id}, rath=rath).experiment


async def asearch_experiments(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchExperimentsQueryOptions]:
    """SearchExperiments


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchExperimentsQueryExperiments]
    """
    return (
        await aexecute(
            SearchExperimentsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_experiments(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchExperimentsQueryOptions]:
    """SearchExperiments


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchExperimentsQueryExperiments]
    """
    return execute(
        SearchExperimentsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_experiments(
    filter: Optional[ExperimentFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Experiment]:
    """ListExperiments


    Args:
        filter (Optional[ExperimentFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Experiment]
    """
    return (
        await aexecute(
            ListExperimentsQuery,
            {"filter": filter, "pagination": pagination},
            rath=rath,
        )
    ).experiments


def list_experiments(
    filter: Optional[ExperimentFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Experiment]:
    """ListExperiments


    Args:
        filter (Optional[ExperimentFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Experiment]
    """
    return execute(
        ListExperimentsQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).experiments


async def aget_file(id: ID, rath: Optional[ElektroRath] = None) -> File:
    """GetFile


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        File
    """
    return (await aexecute(GetFileQuery, {"id": id}, rath=rath)).file


def get_file(id: ID, rath: Optional[ElektroRath] = None) -> File:
    """GetFile


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        File
    """
    return execute(GetFileQuery, {"id": id}, rath=rath).file


async def asearch_files(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchFilesQueryOptions]:
    """SearchFiles


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchFilesQueryFiles]
    """
    return (
        await aexecute(
            SearchFilesQuery,
            {"search": search, "values": values, "pagination": pagination},
            rath=rath,
        )
    ).options


def search_files(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchFilesQueryOptions]:
    """SearchFiles


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchFilesQueryFiles]
    """
    return execute(
        SearchFilesQuery,
        {"search": search, "values": values, "pagination": pagination},
        rath=rath,
    ).options


async def aget_model_collection(
    id: ID, rath: Optional[ElektroRath] = None
) -> ModelCollection:
    """GetModelCollection


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ModelCollection
    """
    return (
        await aexecute(GetModelCollectionQuery, {"id": id}, rath=rath)
    ).model_collection


def get_model_collection(id: ID, rath: Optional[ElektroRath] = None) -> ModelCollection:
    """GetModelCollection


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ModelCollection
    """
    return execute(GetModelCollectionQuery, {"id": id}, rath=rath).model_collection


async def asearch_model_collection(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchModelCollectionQueryOptions]:
    """SearchModelCollection


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchModelCollectionQueryModelcollections]
    """
    return (
        await aexecute(
            SearchModelCollectionQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_model_collection(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchModelCollectionQueryOptions]:
    """SearchModelCollection


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchModelCollectionQueryModelcollections]
    """
    return execute(
        SearchModelCollectionQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_model_collections(
    filter: Optional[ModelCollectionFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[ModelCollection]:
    """ListModelCollections


    Args:
        filter (Optional[ModelCollectionFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[ModelCollection]
    """
    return (
        await aexecute(
            ListModelCollectionsQuery,
            {"filter": filter, "pagination": pagination},
            rath=rath,
        )
    ).model_collections


def list_model_collections(
    filter: Optional[ModelCollectionFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[ModelCollection]:
    """ListModelCollections


    Args:
        filter (Optional[ModelCollectionFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[ModelCollection]
    """
    return execute(
        ListModelCollectionsQuery,
        {"filter": filter, "pagination": pagination},
        rath=rath,
    ).model_collections


async def aget_neuron_model(id: ID, rath: Optional[ElektroRath] = None) -> NeuronModel:
    """GetNeuronModel

    Returns a single image by ID

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        NeuronModel
    """
    return (await aexecute(GetNeuronModelQuery, {"id": id}, rath=rath)).neuron_model


def get_neuron_model(id: ID, rath: Optional[ElektroRath] = None) -> NeuronModel:
    """GetNeuronModel

    Returns a single image by ID

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        NeuronModel
    """
    return execute(GetNeuronModelQuery, {"id": id}, rath=rath).neuron_model


async def asearch_neuron_models(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchNeuronModelsQueryOptions]:
    """SearchNeuronModels


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchNeuronModelsQueryNeuronmodels]
    """
    return (
        await aexecute(
            SearchNeuronModelsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_neuron_models(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchNeuronModelsQueryOptions]:
    """SearchNeuronModels


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchNeuronModelsQueryNeuronmodels]
    """
    return execute(
        SearchNeuronModelsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_neuron_models(
    filter: Optional[NeuronModelFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[NeuronModel]:
    """ListNeuronModels


    Args:
        filter (Optional[NeuronModelFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[NeuronModel]
    """
    return (
        await aexecute(
            ListNeuronModelsQuery,
            {"filter": filter, "pagination": pagination},
            rath=rath,
        )
    ).neuron_models


def list_neuron_models(
    filter: Optional[NeuronModelFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[NeuronModel]:
    """ListNeuronModels


    Args:
        filter (Optional[NeuronModelFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[NeuronModel]
    """
    return execute(
        ListNeuronModelsQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).neuron_models


async def aget_recording(id: ID, rath: Optional[ElektroRath] = None) -> Recording:
    """GetRecording

    Returns a list of images

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Recording
    """
    return (await aexecute(GetRecordingQuery, {"id": id}, rath=rath)).recording


def get_recording(id: ID, rath: Optional[ElektroRath] = None) -> Recording:
    """GetRecording

    Returns a list of images

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Recording
    """
    return execute(GetRecordingQuery, {"id": id}, rath=rath).recording


async def asearch_recordings(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchRecordingsQueryOptions]:
    """SearchRecordings


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchRecordingsQueryRecordings]
    """
    return (
        await aexecute(
            SearchRecordingsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_recordings(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchRecordingsQueryOptions]:
    """SearchRecordings


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchRecordingsQueryRecordings]
    """
    return execute(
        SearchRecordingsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_recordings(
    filter: Optional[RecordingFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Recording]:
    """ListRecordings


    Args:
        filter (Optional[RecordingFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Recording]
    """
    return (
        await aexecute(
            ListRecordingsQuery, {"filter": filter, "pagination": pagination}, rath=rath
        )
    ).recordings


def list_recordings(
    filter: Optional[RecordingFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Recording]:
    """ListRecordings


    Args:
        filter (Optional[RecordingFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Recording]
    """
    return execute(
        ListRecordingsQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).recordings


async def aget_rois(trace: ID, rath: Optional[ElektroRath] = None) -> List[ROI]:
    """GetRois


    Args:
        trace (ID): No description
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[ROI]
    """
    return (await aexecute(GetRoisQuery, {"trace": trace}, rath=rath)).rois


def get_rois(trace: ID, rath: Optional[ElektroRath] = None) -> List[ROI]:
    """GetRois


    Args:
        trace (ID): No description
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[ROI]
    """
    return execute(GetRoisQuery, {"trace": trace}, rath=rath).rois


async def aget_roi(id: ID, rath: Optional[ElektroRath] = None) -> ROI:
    """GetRoi


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ROI
    """
    return (await aexecute(GetRoiQuery, {"id": id}, rath=rath)).roi


def get_roi(id: ID, rath: Optional[ElektroRath] = None) -> ROI:
    """GetRoi


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ROI
    """
    return execute(GetRoiQuery, {"id": id}, rath=rath).roi


async def asearch_rois(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchRoisQueryOptions]:
    """SearchRois


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchRoisQueryRois]
    """
    return (
        await aexecute(SearchRoisQuery, {"search": search, "values": values}, rath=rath)
    ).options


def search_rois(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchRoisQueryOptions]:
    """SearchRois


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchRoisQueryRois]
    """
    return execute(
        SearchRoisQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_simulation(id: ID, rath: Optional[ElektroRath] = None) -> Simulation:
    """GetSimulation


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Simulation
    """
    return (await aexecute(GetSimulationQuery, {"id": id}, rath=rath)).simulation


def get_simulation(id: ID, rath: Optional[ElektroRath] = None) -> Simulation:
    """GetSimulation


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Simulation
    """
    return execute(GetSimulationQuery, {"id": id}, rath=rath).simulation


async def asearch_simulations(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchSimulationsQueryOptions]:
    """SearchSimulations


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchSimulationsQuerySimulations]
    """
    return (
        await aexecute(
            SearchSimulationsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_simulations(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchSimulationsQueryOptions]:
    """SearchSimulations


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchSimulationsQuerySimulations]
    """
    return execute(
        SearchSimulationsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_simulations(
    filter: Optional[SimulationFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Simulation]:
    """ListSimulations


    Args:
        filter (Optional[SimulationFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Simulation]
    """
    return (
        await aexecute(
            ListSimulationsQuery,
            {"filter": filter, "pagination": pagination},
            rath=rath,
        )
    ).simulations


def list_simulations(
    filter: Optional[SimulationFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Simulation]:
    """ListSimulations


    Args:
        filter (Optional[SimulationFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Simulation]
    """
    return execute(
        ListSimulationsQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).simulations


async def aget_stimulus(id: ID, rath: Optional[ElektroRath] = None) -> Stimulus:
    """GetStimulus

    Returns a list of images

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Stimulus
    """
    return (await aexecute(GetStimulusQuery, {"id": id}, rath=rath)).stimulus


def get_stimulus(id: ID, rath: Optional[ElektroRath] = None) -> Stimulus:
    """GetStimulus

    Returns a list of images

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Stimulus
    """
    return execute(GetStimulusQuery, {"id": id}, rath=rath).stimulus


async def asearch_stimuli(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchStimuliQueryOptions]:
    """SearchStimuli


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchStimuliQueryStimuli]
    """
    return (
        await aexecute(
            SearchStimuliQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_stimuli(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchStimuliQueryOptions]:
    """SearchStimuli


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchStimuliQueryStimuli]
    """
    return execute(
        SearchStimuliQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_stimuli(
    filter: Optional[StimulusFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Stimulus]:
    """ListStimuli


    Args:
        filter (Optional[StimulusFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Stimulus]
    """
    return (
        await aexecute(
            ListStimuliQuery, {"filter": filter, "pagination": pagination}, rath=rath
        )
    ).stimuli


def list_stimuli(
    filter: Optional[StimulusFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Stimulus]:
    """ListStimuli


    Args:
        filter (Optional[StimulusFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Stimulus]
    """
    return execute(
        ListStimuliQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).stimuli


async def aget_trace(id: ID, rath: Optional[ElektroRath] = None) -> Trace:
    """GetTrace

    Returns a single image by ID

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return (await aexecute(GetTraceQuery, {"id": id}, rath=rath)).trace


def get_trace(id: ID, rath: Optional[ElektroRath] = None) -> Trace:
    """GetTrace

    Returns a single image by ID

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return execute(GetTraceQuery, {"id": id}, rath=rath).trace


async def aget_random_trace(rath: Optional[ElektroRath] = None) -> Trace:
    """GetRandomTrace


    Args:
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return (await aexecute(GetRandomTraceQuery, {}, rath=rath)).random_trace


def get_random_trace(rath: Optional[ElektroRath] = None) -> Trace:
    """GetRandomTrace


    Args:
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return execute(GetRandomTraceQuery, {}, rath=rath).random_trace


async def asearch_traces(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchTracesQueryOptions]:
    """SearchTraces


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchTracesQueryTraces]
    """
    return (
        await aexecute(
            SearchTracesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_traces(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchTracesQueryOptions]:
    """SearchTraces


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchTracesQueryTraces]
    """
    return execute(
        SearchTracesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def alist_traces(
    filter: Optional[TraceFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Trace]:
    """ListTraces


    Args:
        filter (Optional[TraceFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Trace]
    """
    return (
        await aexecute(
            ListTracesQuery, {"filter": filter, "pagination": pagination}, rath=rath
        )
    ).traces


def list_traces(
    filter: Optional[TraceFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[ElektroRath] = None,
) -> List[Trace]:
    """ListTraces


    Args:
        filter (Optional[TraceFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Trace]
    """
    return execute(
        ListTracesQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).traces


async def awatch_files(
    dataset: Optional[ID] = None, rath: Optional[ElektroRath] = None
) -> AsyncIterator[WatchFilesSubscriptionFiles]:
    """WatchFiles

    Subscribe to real-time file updates

    Args:
        dataset (Optional[ID], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchFilesSubscriptionFiles
    """
    async for event in asubscribe(
        WatchFilesSubscription, {"dataset": dataset}, rath=rath
    ):
        yield event.files


def watch_files(
    dataset: Optional[ID] = None, rath: Optional[ElektroRath] = None
) -> Iterator[WatchFilesSubscriptionFiles]:
    """WatchFiles

    Subscribe to real-time file updates

    Args:
        dataset (Optional[ID], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchFilesSubscriptionFiles
    """
    for event in subscribe(WatchFilesSubscription, {"dataset": dataset}, rath=rath):
        yield event.files


async def awatch_rois(
    trace: ID, rath: Optional[ElektroRath] = None
) -> AsyncIterator[WatchRoisSubscriptionRois]:
    """WatchRois

    Subscribe to real-time ROI updates

    Args:
        trace (ID): No description
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchRoisSubscriptionRois
    """
    async for event in asubscribe(WatchRoisSubscription, {"trace": trace}, rath=rath):
        yield event.rois


def watch_rois(
    trace: ID, rath: Optional[ElektroRath] = None
) -> Iterator[WatchRoisSubscriptionRois]:
    """WatchRois

    Subscribe to real-time ROI updates

    Args:
        trace (ID): No description
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchRoisSubscriptionRois
    """
    for event in subscribe(WatchRoisSubscription, {"trace": trace}, rath=rath):
        yield event.rois


async def awatch_traces(
    dataset: Optional[ID] = None, rath: Optional[ElektroRath] = None
) -> AsyncIterator[WatchTracesSubscriptionTraces]:
    """WatchTraces

    Subscribe to real-time image updates

    Args:
        dataset (Optional[ID], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchTracesSubscriptionTraces
    """
    async for event in asubscribe(
        WatchTracesSubscription, {"dataset": dataset}, rath=rath
    ):
        yield event.traces


def watch_traces(
    dataset: Optional[ID] = None, rath: Optional[ElektroRath] = None
) -> Iterator[WatchTracesSubscriptionTraces]:
    """WatchTraces

    Subscribe to real-time image updates

    Args:
        dataset (Optional[ID], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchTracesSubscriptionTraces
    """
    for event in subscribe(WatchTracesSubscription, {"dataset": dataset}, rath=rath):
        yield event.traces


AnalogSignalInput.model_rebuild()
BiophysicsInput.model_rebuild()
BlockSegmentInput.model_rebuild()
CellInput.model_rebuild()
CompartmentInput.model_rebuild()
CreateBlockInput.model_rebuild()
CreateExperimentInput.model_rebuild()
CreateNeuronModelInput.model_rebuild()
CreateSimulationInput.model_rebuild()
DatasetFilter.model_rebuild()
ExperimentFilter.model_rebuild()
ModelCollectionFilter.model_rebuild()
ModelConfigInput.model_rebuild()
NeuronModelFilter.model_rebuild()
RecordingFilter.model_rebuild()
SectionInput.model_rebuild()
SimulationFilter.model_rebuild()
StimulusFilter.model_rebuild()
TopologyInput.model_rebuild()
TraceFilter.model_rebuild()

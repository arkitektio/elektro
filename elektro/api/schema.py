from elektro.funcs import subscribe, aexecute, execute, asubscribe
from elektro.traits import (
    IsVectorizableTrait,
    CompartmentTrait,
    BiophysicsTrait,
    ModelConfigTrait,
    BiophysicsInputTrait,
    TopologyInputTrait,
    ModelConfigInputTrait,
    SectionInputTrait,
    TopologyTrait,
    SimulationTrait,
    HasZarrStoreAccessor,
    ExperimentTrait,
    HasDownloadAccessor,
    HasZarrStoreTrait,
    HasPresignedDownloadAccessor,
    CompartmentInputTrait,
)
from typing import (
    List,
    Any,
    Union,
    AsyncIterator,
    Literal,
    Annotated,
    Iterable,
    Iterator,
    Optional,
)
from enum import Enum
from elektro.rath import ElektroRath
from pydantic import BaseModel, ConfigDict, Field
from kanne.scalars import Millisecond
from rath.scalars import IDCoercible, ID
from elektro.scalars import (
    ArrayLike,
    BigFileLike,
    FileLike,
    TwoDVector,
    FiveDVector,
    TraceLike,
)
from datetime import datetime


class AssignWidgetKind(str, Enum):
    """The kind of assign widget."""

    SEARCH = "SEARCH"
    CHOICE = "CHOICE"
    SLIDER = "SLIDER"
    CUSTOM = "CUSTOM"
    STRING = "STRING"
    STATE_CHOICE = "STATE_CHOICE"
    PROXY = "PROXY"


class ConnectionKind(str, Enum):
    """No documentation"""

    SYNAPSE = "SYNAPSE"


class EffectKind(str, Enum):
    """The kind of effect."""

    MESSAGE = "MESSAGE"
    HIDE = "HIDE"
    CUSTOM = "CUSTOM"


class OptionKey(str, Enum):
    """No documentation"""

    LABEL = "LABEL"
    DESCRIPTION = "DESCRIPTION"
    LOGO = "LOGO"
    VALUE = "VALUE"


class PortKind(str, Enum):
    """The kind of port."""

    INT = "INT"
    STRING = "STRING"
    STRUCTURE = "STRUCTURE"
    LIST = "LIST"
    BOOL = "BOOL"
    DICT = "DICT"
    FLOAT = "FLOAT"
    DATE = "DATE"
    UNION = "UNION"
    ENUM = "ENUM"
    MODEL = "MODEL"
    MEMORY_STRUCTURE = "MEMORY_STRUCTURE"
    INTERFACE = "INTERFACE"


class RecordingKind(str, Enum):
    """No documentation"""

    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"
    TIME = "TIME"
    INA = "INA"
    UNKNOWN = "UNKNOWN"


class RequiresOperator(str, Enum):
    """The operator for matching descriptors."""

    MATCHES = "MATCHES"
    EXISTS = "EXISTS"
    LTE = "LTE"
    GTE = "GTE"
    EQUALS = "EQUALS"
    CONTAINS = "CONTAINS"
    NOT_EQUALS = "NOT_EQUALS"
    IN = "IN"
    NOT_IN = "NOT_IN"


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


class SynapseKind(str, Enum):
    """No documentation"""

    EXP2SYN = "EXP2SYN"
    GABAA = "GABAA"


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


class AnalogSignalInput(BaseModel):
    """No documentation"""

    time_trace: TraceLike = Field(alias="timeTrace")
    name: Optional[str] = None
    description: Optional[str] = None
    sampling_rate: float = Field(alias="samplingRate")
    t_start: float = Field(alias="tStart")
    unit: Optional[str] = None
    channels: List[AnalogSignalChannelInput]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ArgPortInput(BaseModel):
    """Port

    A Port is a single input or output of a action. It is composed of a key and a kind
    which are used to uniquely identify the port.

    If the Port is a structure, we need to define a identifier and scope,
    Identifiers uniquely identify a specific type of model for the scopes (e.g
    all the ports that have the identifier "@mikro/image" are of the same type, and
    are hence compatible with each other). Scopes are used to define in which context
    the identifier is valid (e.g. a port with the identifier "@mikro/image" and the
    scope "local", can only be wired to other ports that have the same identifier and
    are running in the same app). Global ports are ports that have the scope "global",
    and can be wired to any other port that has the same identifier, as there exists a
    mechanism to resolve and retrieve the object for each app. Please check the rekuest
    documentation for more information on how this works.


    """

    validators: Optional[List["ValidatorInput"]] = None
    key: str
    label: Optional[str] = None
    kind: PortKind
    description: Optional[str] = None
    identifier: Optional[str] = None
    nullable: bool
    effects: Optional[List["EffectInput"]] = None
    default: Optional[Any] = None
    children: Optional[List["ArgPortInput"]] = None
    choices: Optional[List["ChoiceInput"]] = None
    widget: Optional["AssignWidgetInput"] = None
    requires: Optional[List["RequiresInput"]] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AssignWidgetInput(BaseModel):
    """No documentation"""

    as_paragraph: Optional[bool] = Field(alias="asParagraph", default=None)
    "Whether to display the input as a paragraph or not. This is used for text inputs and dropdowns"
    kind: AssignWidgetKind
    query: Optional[str] = None
    choices: Optional[List["ChoiceInput"]] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    placeholder: Optional[str] = None
    hook: Optional[str] = None
    ward: Optional[str] = None
    fallback: Optional["AssignWidgetInput"] = None
    filters: Optional[List[ArgPortInput]] = None
    dependencies: Optional[List[str]] = None
    dependency: Optional[str] = None
    target_dependency: Optional[str] = Field(alias="targetDependency", default=None)
    target_action: Optional[str] = Field(alias="targetAction", default=None)
    target_port: Optional[str] = Field(alias="targetPort", default=None)
    state_path: Optional[str] = Field(alias="statePath", default=None)
    state_accessors: Optional[List["StateAccessorInput"]] = Field(
        alias="stateAccessors", default=None
    )
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BiophysicsInput(BiophysicsInputTrait, BaseModel):
    """No documentation"""

    compartments: List["CompartmentInput"]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class BlockSegmentInput(BaseModel):
    """No documentation"""

    name: Optional[str] = None
    description: Optional[str] = None
    analog_signals: List[AnalogSignalInput] = Field(alias="analogSignals")
    irregularly_sampled_signals: List["IrregularlySampledSignalInput"] = Field(
        alias="irregularlySampledSignals"
    )
    spike_trains: List["SpikeTrainInput"] = Field(alias="spikeTrains")
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CellInput(BaseModel):
    """No documentation"""

    id: str
    biophysics: BiophysicsInput
    topology: "TopologyInput"
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


class ChoiceInput(BaseModel):
    """
    A choice is a value that can be selected in a dropdown.

    It is composed of a value, a label, and a description. The value is the
    value that is returned when the choice is selected. The label is the
    text that is displayed in the dropdown. The description is the text
    that is displayed when the user hovers over the choice.

    """

    value: Any
    label: str
    image: Optional[str] = None
    description: Optional[str] = None
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


class ConnectionInput(BaseModel):
    """No documentation"""

    parent: str
    location: float
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


class CreateBlockInput(BaseModel):
    """No documentation"""

    file: Optional[ID] = None
    name: str
    recording_time: Optional[datetime] = Field(alias="recordingTime", default=None)
    segments: List[BlockSegmentInput]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateDatasetInput(BaseModel):
    """No documentation"""

    name: str
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


class CreateModEnvironmentInput(BaseModel):
    """Input for creating a mod environment"""

    name: str
    description: Optional[str] = None
    zip_file: BigFileLike = Field(alias="zipFile")
    mechanisms: List["MechanismInput"]
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


class CreateNeuronModelInput(BaseModel):
    """No documentation"""

    name: str
    environment: Optional[ID] = None
    parent: Optional[ID] = None
    description: Optional[str] = None
    config: "ModelConfigInput"
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateSimulationInput(BaseModel):
    """No documentation"""

    name: str
    model: ID
    recordings: List["RecordingInput"]
    stimuli: List["StimulusInput"]
    time_trace: Optional[ArrayLike] = Field(alias="timeTrace", default=None)
    duration: Millisecond
    dt: Optional[Millisecond] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DatasetFilter(BaseModel):
    """No documentation"""

    id: Optional[ID] = None
    name: Optional["StrFilterLookup"] = None
    and_: Optional["DatasetFilter"] = Field(alias="AND", default=None)
    or_: Optional["DatasetFilter"] = Field(alias="OR", default=None)
    not_: Optional["DatasetFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeleteRoiInput(BaseModel):
    """No documentation"""

    id: ID
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EffectInput(BaseModel):
    """
                 An effect is a way to modify a port based on a condition. For example,
    you could have an effect that sets a port to null if another port is null.

    Or, you could have an effect that hides the port if another port meets a condition.
    E.g when the user selects a certain option in a dropdown, another port is hidden.


    """

    function: str
    dependencies: Optional[List[str]] = None
    message: Optional[str] = None
    kind: EffectKind
    fade: Optional[bool] = None
    hook: Optional[str] = None
    ward: Optional[str] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ExperimentFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    created_before: Optional[datetime] = Field(alias="createdBefore", default=None)
    created_after: Optional[datetime] = Field(alias="createdAfter", default=None)
    id: Optional[ID] = None
    name: Optional["StrFilterLookup"] = None
    and_: Optional["ExperimentFilter"] = Field(alias="AND", default=None)
    or_: Optional["ExperimentFilter"] = Field(alias="OR", default=None)
    not_: Optional["ExperimentFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FinishBigFileUploadInput(BaseModel):
    """No documentation"""

    store_id: str = Field(alias="storeId")
    valid: bool
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FinishMediaUploadInput(BaseModel):
    """No documentation"""

    store_id: str = Field(alias="storeId")
    valid: bool
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FinishParquetUploadInput(BaseModel):
    """No documentation"""

    store_id: str = Field(alias="storeId")
    valid: bool
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FinishZarrUploadInput(BaseModel):
    """No documentation"""

    store_id: str = Field(alias="storeId")
    valid: bool
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


class FromTraceLikeInput(BaseModel):
    """Input type for creating an image from an array-like object"""

    array: ArrayLike
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


class GlobalParamMapInput(BaseModel):
    """No documentation"""

    param: str
    value: float
    description: Optional[str] = None
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


class MechanismInput(BaseModel):
    """Input for creating a mechanism"""

    name: str
    description: Optional[str] = None
    parameters: List[ArgPortInput]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ModelCollectionFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    created_before: Optional[datetime] = Field(alias="createdBefore", default=None)
    created_after: Optional[datetime] = Field(alias="createdAfter", default=None)
    id: Optional[ID] = None
    name: Optional["StrFilterLookup"] = None
    and_: Optional["ModelCollectionFilter"] = Field(alias="AND", default=None)
    or_: Optional["ModelCollectionFilter"] = Field(alias="OR", default=None)
    not_: Optional["ModelCollectionFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ModelConfigInput(ModelConfigInputTrait, BaseModel):
    """No documentation"""

    cells: List[CellInput]
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
    environments: List[str]
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


class NetStimulatorInput(BaseModel):
    """No documentation"""

    id: ID
    start: float
    number: int
    interval: Optional[float] = None
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


class NeuronModelFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    created_before: Optional[datetime] = Field(alias="createdBefore", default=None)
    created_after: Optional[datetime] = Field(alias="createdAfter", default=None)
    id: Optional[ID] = None
    name: Optional["StrFilterLookup"] = None
    and_: Optional["NeuronModelFilter"] = Field(alias="AND", default=None)
    or_: Optional["NeuronModelFilter"] = Field(alias="OR", default=None)
    not_: Optional["NeuronModelFilter"] = Field(alias="NOT", default=None)
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


class RecordingFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    created_before: Optional[datetime] = Field(alias="createdBefore", default=None)
    created_after: Optional[datetime] = Field(alias="createdAfter", default=None)
    id: Optional[ID] = None
    name: Optional["StrFilterLookup"] = None
    and_: Optional["RecordingFilter"] = Field(alias="AND", default=None)
    or_: Optional["RecordingFilter"] = Field(alias="OR", default=None)
    not_: Optional["RecordingFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RecordingInput(BaseModel):
    """No documentation"""

    trace: ArrayLike
    kind: RecordingKind
    cell: Optional[ID] = None
    location: Optional[ID] = None
    position: Optional[float] = None
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


class RequestBigFileAccessInput(BaseModel):
    """No documentation"""

    store_id: str = Field(alias="storeId")
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestBigFileUploadInput(BaseModel):
    """No documentation"""

    original_file_name: str = Field(alias="originalFileName")
    file_size: Optional[int] = Field(alias="fileSize", default=None)
    content_type: Optional[str] = Field(alias="contentType", default=None)
    host: Optional[str] = None
    port: Optional[int] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestMediaAccessInput(BaseModel):
    """No documentation"""

    store_id: str = Field(alias="storeId")
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestMediaUploadInput(BaseModel):
    """No documentation"""

    original_file_name: str = Field(alias="originalFileName")
    file_size: Optional[int] = Field(alias="fileSize", default=None)
    content_type: Optional[str] = Field(alias="contentType", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestParquetAccessInput(BaseModel):
    """No documentation"""

    store_id: str = Field(alias="storeId")
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestParquetUploadInput(BaseModel):
    """No documentation"""

    original_file_name: str = Field(alias="originalFileName")
    content_type: Optional[str] = Field(alias="contentType", default=None)
    host: Optional[str] = None
    port: Optional[int] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestZarrAccessInput(BaseModel):
    """No documentation"""

    store_id: str = Field(alias="storeId")
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestZarrUploadInput(BaseModel):
    """No documentation"""

    shape: Optional[List[int]] = None
    chunks: Optional[List[int]] = None
    version: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequiresInput(BaseModel):
    """No documentation"""

    key: str
    operator: RequiresOperator
    value: Any
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


class SectionInput(SectionInputTrait, BaseModel):
    """No documentation"""

    id: str
    category: Optional[str] = None
    nseg: int
    diam: float
    length: Optional[float] = None
    "Length of the section. Required if coords is not provided."
    coords: Optional[List[CoordInput]] = None
    connections: Optional[List[ConnectionInput]] = None
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


class SimulationFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    created_before: Optional[datetime] = Field(alias="createdBefore", default=None)
    created_after: Optional[datetime] = Field(alias="createdAfter", default=None)
    id: Optional[ID] = None
    name: Optional["StrFilterLookup"] = None
    and_: Optional["SimulationFilter"] = Field(alias="AND", default=None)
    or_: Optional["SimulationFilter"] = Field(alias="OR", default=None)
    not_: Optional["SimulationFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
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


class StateAccessorInput(BaseModel):
    """No documentation"""

    option_key: OptionKey = Field(alias="optionKey")
    sub_path: Optional[str] = Field(alias="subPath", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StimulusFilter(BaseModel):
    """No documentation"""

    ids: Optional[List[ID]] = None
    search: Optional[str] = None
    created_before: Optional[datetime] = Field(alias="createdBefore", default=None)
    created_after: Optional[datetime] = Field(alias="createdAfter", default=None)
    id: Optional[ID] = None
    name: Optional["StrFilterLookup"] = None
    and_: Optional["StimulusFilter"] = Field(alias="AND", default=None)
    or_: Optional["StimulusFilter"] = Field(alias="OR", default=None)
    not_: Optional["StimulusFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StimulusInput(BaseModel):
    """No documentation"""

    trace: ArrayLike
    kind: StimulusKind
    cell: Optional[ID] = None
    location: Optional[ID] = None
    position: Optional[float] = None
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


class TopologyInput(TopologyInputTrait, BaseModel):
    """No documentation"""

    sections: List[SectionInput]
    model_config = ConfigDict(
        extra="forbid", populate_by_name=True, use_enum_values=True
    )


class TraceFilter(BaseModel):
    """No documentation"""

    name: Optional[StrFilterLookup] = None
    ids: Optional[List[ID]] = None
    dataset: Optional[DatasetFilter] = None
    not_derived: Optional[bool] = Field(alias="notDerived", default=None)
    search: Optional[str] = None
    and_: Optional["TraceFilter"] = Field(alias="AND", default=None)
    or_: Optional["TraceFilter"] = Field(alias="OR", default=None)
    not_: Optional["TraceFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
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


class ValidatorInput(BaseModel):
    """
    A validating function for a port. Can specify a function that will run when validating values of the port.
    If outside dependencies are needed they need to be specified in the dependencies field. With the .. syntax
    when transversing the tree of ports.

    """

    function: str
    dependencies: Optional[List[str]] = None
    label: Optional[str] = None
    error_message: Optional[str] = Field(alias="errorMessage", default=None)
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


class BigFileUploadGrant(BaseModel):
    """Temporary S3 credentials for uploading a big file."""

    typename: Literal["BigFileUploadGrant"] = Field(
        alias="__typename", default="BigFileUploadGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    path: str
    key: str
    bucket: str
    expires_in: int = Field(alias="expiresIn")
    store: str

    class Meta:
        """Meta class for BigFileUploadGrant"""

        document = "fragment BigFileUploadGrant on BigFileUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  expiresIn\n  store\n  __typename\n}"
        name = "BigFileUploadGrant"
        type = "BigFileUploadGrant"


class MediaUploadGrant(BaseModel):
    """A presigned PUT grant for uploading a media object."""

    typename: Literal["MediaUploadGrant"] = Field(
        alias="__typename", default="MediaUploadGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    path: str
    key: str
    bucket: str
    expires_in: int = Field(alias="expiresIn")
    max_bytes: int = Field(alias="maxBytes")
    store: str

    class Meta:
        """Meta class for MediaUploadGrant"""

        document = "fragment MediaUploadGrant on MediaUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  expiresIn\n  maxBytes\n  store\n  __typename\n}"
        name = "MediaUploadGrant"
        type = "MediaUploadGrant"


class ZarrUploadGrant(BaseModel):
    """Temporary S3 credentials for uploading a Zarr store."""

    typename: Literal["ZarrUploadGrant"] = Field(
        alias="__typename", default="ZarrUploadGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    path: str
    key: str
    bucket: str
    expires_in: int = Field(alias="expiresIn")
    max_bytes: int = Field(alias="maxBytes")
    store: str

    class Meta:
        """Meta class for ZarrUploadGrant"""

        document = "fragment ZarrUploadGrant on ZarrUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  expiresIn\n  maxBytes\n  store\n  __typename\n}"
        name = "ZarrUploadGrant"
        type = "ZarrUploadGrant"


class ParquetUploadGrant(BaseModel):
    """Temporary S3 credentials for uploading a parquet store."""

    typename: Literal["ParquetUploadGrant"] = Field(
        alias="__typename", default="ParquetUploadGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    path: str
    key: str
    bucket: str
    expires_in: int = Field(alias="expiresIn")
    max_bytes: int = Field(alias="maxBytes")
    store: str

    class Meta:
        """Meta class for ParquetUploadGrant"""

        document = "fragment ParquetUploadGrant on ParquetUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  expiresIn\n  maxBytes\n  store\n  __typename\n}"
        name = "ParquetUploadGrant"
        type = "ParquetUploadGrant"


class BigFileAccessGrant(BaseModel):
    """Temporary S3 credentials for reading a big file."""

    typename: Literal["BigFileAccessGrant"] = Field(
        alias="__typename", default="BigFileAccessGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    expires_in: int = Field(alias="expiresIn")
    path: str
    key: str
    bucket: str

    class Meta:
        """Meta class for BigFileAccessGrant"""

        document = "fragment BigFileAccessGrant on BigFileAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  expiresIn\n  path\n  key\n  bucket\n  __typename\n}"
        name = "BigFileAccessGrant"
        type = "BigFileAccessGrant"


class MediaAccessGrant(BaseModel):
    """Temporary S3 credentials for reading a media object."""

    typename: Literal["MediaAccessGrant"] = Field(
        alias="__typename", default="MediaAccessGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    expires_in: int = Field(alias="expiresIn")
    path: str
    key: str
    bucket: str

    class Meta:
        """Meta class for MediaAccessGrant"""

        document = "fragment MediaAccessGrant on MediaAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  expiresIn\n  path\n  key\n  bucket\n  __typename\n}"
        name = "MediaAccessGrant"
        type = "MediaAccessGrant"


class ZarrAccessGrant(BaseModel):
    """Temporary S3 credentials for reading a Zarr store."""

    typename: Literal["ZarrAccessGrant"] = Field(
        alias="__typename", default="ZarrAccessGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    expires_in: int = Field(alias="expiresIn")
    path: str
    key: str
    bucket: str

    class Meta:
        """Meta class for ZarrAccessGrant"""

        document = "fragment ZarrAccessGrant on ZarrAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  expiresIn\n  path\n  key\n  bucket\n  __typename\n}"
        name = "ZarrAccessGrant"
        type = "ZarrAccessGrant"


class ParquetAccessGrant(BaseModel):
    """Temporary S3 credentials for reading a parquet object."""

    typename: Literal["ParquetAccessGrant"] = Field(
        alias="__typename", default="ParquetAccessGrant", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    session_token: str = Field(alias="sessionToken")
    expires_in: int = Field(alias="expiresIn")
    path: str
    key: str
    bucket: str

    class Meta:
        """Meta class for ParquetAccessGrant"""

        document = "fragment ParquetAccessGrant on ParquetAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  expiresIn\n  path\n  key\n  bucket\n  __typename\n}"
        name = "ParquetAccessGrant"
        type = "ParquetAccessGrant"


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


class MechanismParameters(BaseModel):
    """No documentation"""

    typename: Literal["ArgPort"] = Field(
        alias="__typename", default="ArgPort", exclude=True
    )
    key: str
    kind: PortKind


class Mechanism(BaseModel):
    """No documentation"""

    typename: Literal["Mechanism"] = Field(
        alias="__typename", default="Mechanism", exclude=True
    )
    id: ID
    name: str
    parameters: List[MechanismParameters]
    "The parameter ports of the mechanism"

    class Meta:
        """Meta class for Mechanism"""

        document = "fragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}"
        name = "Mechanism"
        type = "Mechanism"


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
    bucket: str
    path: str

    class Meta:
        """Meta class for ZarrStore"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}"
        name = "ZarrStore"
        type = "ZarrStore"


class ParquetStore(BaseModel):
    """No documentation"""

    typename: Literal["ParquetStore"] = Field(
        alias="__typename", default="ParquetStore", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str

    class Meta:
        """Meta class for ParquetStore"""

        document = "fragment ParquetStore on ParquetStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}"
        name = "ParquetStore"
        type = "ParquetStore"


class BigFileStore(HasDownloadAccessor, BaseModel):
    """A BigFileStore represents a large object stored behind the S3 datalayer."""

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


class MediaStore(HasPresignedDownloadAccessor, BaseModel):
    """No documentation"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str

    class Meta:
        """Meta class for MediaStore"""

        document = "fragment MediaStore on MediaStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}"
        name = "MediaStore"
        type = "MediaStore"


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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}"
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
    position: float
    location: str

    class Meta:
        """Meta class for Recording"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}"
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
    position: float
    location: str

    class Meta:
        """Meta class for Stimulus"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}"
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


class ModEnvironment(BaseModel):
    """No documentation"""

    typename: Literal["ModEnvironment"] = Field(
        alias="__typename", default="ModEnvironment", exclude=True
    )
    id: ID
    name: str
    store: BigFileStore
    mechanisms: List[Mechanism]

    class Meta:
        """Meta class for ModEnvironment"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}"
        name = "ModEnvironment"
        type = "ModEnvironment"


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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
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

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Experiment on Experiment {\n  name\n  id\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  recordingViews {\n    label\n    recording {\n      ...Recording\n      __typename\n    }\n    __typename\n  }\n  stimulusViews {\n    label\n    stimulus {\n      ...Stimulus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
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
    environment: ModEnvironment
    config: NeuronModelConfig

    class Meta:
        """Meta class for NeuronModel"""

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
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


class Simulation(SimulationTrait, BaseModel):
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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}"
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


class DetailRecordingTrace(HasZarrStoreTrait, BaseModel):
    """No documentation"""

    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID
    store: ZarrStore
    "The store where the image data is stored."


class DetailRecording(BaseModel):
    """No documentation"""

    typename: Literal["Recording"] = Field(
        alias="__typename", default="Recording", exclude=True
    )
    id: ID
    label: str
    cell: str
    trace: DetailRecordingTrace
    simulation: Simulation

    class Meta:
        """Meta class for DetailRecording"""

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment DetailRecording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  simulation {\n    ...Simulation\n    __typename\n  }\n  __typename\n}"
        name = "DetailRecording"
        type = "Recording"


class DetailStimulusTrace(HasZarrStoreTrait, BaseModel):
    """No documentation"""

    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID
    store: ZarrStore
    "The store where the image data is stored."


class DetailStimulus(BaseModel):
    """No documentation"""

    typename: Literal["Stimulus"] = Field(
        alias="__typename", default="Stimulus", exclude=True
    )
    id: ID
    label: str
    cell: str
    kind: StimulusKind
    trace: DetailStimulusTrace
    simulation: Simulation

    class Meta:
        """Meta class for DetailStimulus"""

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment DetailStimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  simulation {\n    ...Simulation\n    __typename\n  }\n  __typename\n}"
        name = "DetailStimulus"
        type = "Stimulus"


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


class RequestBigfileUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_bigfile_upload: BigFileUploadGrant = Field(alias="requestBigfileUpload")
    "Request an upload grant for a big file store"

    class Arguments(BaseModel):
        """Arguments for RequestBigfileUpload"""

        input: RequestBigFileUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestBigfileUpload"""

        document = "fragment BigFileUploadGrant on BigFileUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  expiresIn\n  store\n  __typename\n}\n\nmutation RequestBigfileUpload($input: RequestBigFileUploadInput!) {\n  requestBigfileUpload(input: $input) {\n    ...BigFileUploadGrant\n    __typename\n  }\n}"


class FinishBigfileUploadMutation(BaseModel):
    """No documentation found for this operation."""

    finish_bigfile_upload: BigFileStore = Field(alias="finishBigfileUpload")
    "Finalize a big file upload after the client has written the object"

    class Arguments(BaseModel):
        """Arguments for FinishBigfileUpload"""

        input: FinishBigFileUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for FinishBigfileUpload"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nmutation FinishBigfileUpload($input: FinishBigFileUploadInput!) {\n  finishBigfileUpload(input: $input) {\n    ...BigFileStore\n    __typename\n  }\n}"


class RequestBigfileAccessMutation(BaseModel):
    """No documentation found for this operation."""

    request_bigfile_access: BigFileAccessGrant = Field(alias="requestBigfileAccess")
    "Request temporary S3 read credentials for a big file"

    class Arguments(BaseModel):
        """Arguments for RequestBigfileAccess"""

        input: RequestBigFileAccessInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestBigfileAccess"""

        document = "fragment BigFileAccessGrant on BigFileAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  expiresIn\n  path\n  key\n  bucket\n  __typename\n}\n\nmutation RequestBigfileAccess($input: RequestBigFileAccessInput!) {\n  requestBigfileAccess(input: $input) {\n    ...BigFileAccessGrant\n    __typename\n  }\n}"


class RequestMediaUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_media_upload: MediaUploadGrant = Field(alias="requestMediaUpload")
    "Upload media and return a URL for access"

    class Arguments(BaseModel):
        """Arguments for RequestMediaUpload"""

        input: RequestMediaUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestMediaUpload"""

        document = "fragment MediaUploadGrant on MediaUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  expiresIn\n  maxBytes\n  store\n  __typename\n}\n\nmutation RequestMediaUpload($input: RequestMediaUploadInput!) {\n  requestMediaUpload(input: $input) {\n    ...MediaUploadGrant\n    __typename\n  }\n}"


class FinishMediaUploadMutation(BaseModel):
    """No documentation found for this operation."""

    finish_media_upload: MediaStore = Field(alias="finishMediaUpload")
    "Finalize a media upload after the client has written the object"

    class Arguments(BaseModel):
        """Arguments for FinishMediaUpload"""

        input: FinishMediaUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for FinishMediaUpload"""

        document = "fragment MediaStore on MediaStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nmutation FinishMediaUpload($input: FinishMediaUploadInput!) {\n  finishMediaUpload(input: $input) {\n    ...MediaStore\n    __typename\n  }\n}"


class RequestMediaAccessMutation(BaseModel):
    """No documentation found for this operation."""

    request_media_access: MediaAccessGrant = Field(alias="requestMediaAccess")
    "Request temporary S3 read credentials for a media file"

    class Arguments(BaseModel):
        """Arguments for RequestMediaAccess"""

        input: RequestMediaAccessInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestMediaAccess"""

        document = "fragment MediaAccessGrant on MediaAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  expiresIn\n  path\n  key\n  bucket\n  __typename\n}\n\nmutation RequestMediaAccess($input: RequestMediaAccessInput!) {\n  requestMediaAccess(input: $input) {\n    ...MediaAccessGrant\n    __typename\n  }\n}"


class RequestParquetUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_parquet_upload: ParquetUploadGrant = Field(alias="requestParquetUpload")
    "Request an upload grant for a Parquet store"

    class Arguments(BaseModel):
        """Arguments for RequestParquetUpload"""

        input: RequestParquetUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestParquetUpload"""

        document = "fragment ParquetUploadGrant on ParquetUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  expiresIn\n  maxBytes\n  store\n  __typename\n}\n\nmutation RequestParquetUpload($input: RequestParquetUploadInput!) {\n  requestParquetUpload(input: $input) {\n    ...ParquetUploadGrant\n    __typename\n  }\n}"


class FinishParquetUploadMutation(BaseModel):
    """No documentation found for this operation."""

    finish_parquet_upload: ParquetStore = Field(alias="finishParquetUpload")
    "Finalize a Parquet upload after the client has written the object"

    class Arguments(BaseModel):
        """Arguments for FinishParquetUpload"""

        input: FinishParquetUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for FinishParquetUpload"""

        document = "fragment ParquetStore on ParquetStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nmutation FinishParquetUpload($input: FinishParquetUploadInput!) {\n  finishParquetUpload(input: $input) {\n    ...ParquetStore\n    __typename\n  }\n}"


class RequestParquetAccessMutation(BaseModel):
    """No documentation found for this operation."""

    request_parquet_access: ParquetAccessGrant = Field(alias="requestParquetAccess")
    "Request temporary S3 read credentials for a Parquet file"

    class Arguments(BaseModel):
        """Arguments for RequestParquetAccess"""

        input: RequestParquetAccessInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestParquetAccess"""

        document = "fragment ParquetAccessGrant on ParquetAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  expiresIn\n  path\n  key\n  bucket\n  __typename\n}\n\nmutation RequestParquetAccess($input: RequestParquetAccessInput!) {\n  requestParquetAccess(input: $input) {\n    ...ParquetAccessGrant\n    __typename\n  }\n}"


class RequestZarrUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_zarr_upload: ZarrUploadGrant = Field(alias="requestZarrUpload")
    "Request an upload grant for a Zarr store"

    class Arguments(BaseModel):
        """Arguments for RequestZarrUpload"""

        input: RequestZarrUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestZarrUpload"""

        document = "fragment ZarrUploadGrant on ZarrUploadGrant {\n  accessKey\n  secretKey\n  sessionToken\n  path\n  key\n  bucket\n  expiresIn\n  maxBytes\n  store\n  __typename\n}\n\nmutation RequestZarrUpload($input: RequestZarrUploadInput!) {\n  requestZarrUpload(input: $input) {\n    ...ZarrUploadGrant\n    __typename\n  }\n}"


class FinishZarrUploadMutation(BaseModel):
    """No documentation found for this operation."""

    finish_zarr_upload: ZarrStore = Field(alias="finishZarrUpload")
    "Finalize a Zarr upload after the client has written the object"

    class Arguments(BaseModel):
        """Arguments for FinishZarrUpload"""

        input: FinishZarrUploadInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for FinishZarrUpload"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nmutation FinishZarrUpload($input: FinishZarrUploadInput!) {\n  finishZarrUpload(input: $input) {\n    ...ZarrStore\n    __typename\n  }\n}"


class RequestZarrAccessMutation(BaseModel):
    """No documentation found for this operation."""

    request_zarr_access: ZarrAccessGrant = Field(alias="requestZarrAccess")
    "Request temporary S3 read credentials for a Zarr store"

    class Arguments(BaseModel):
        """Arguments for RequestZarrAccess"""

        input: RequestZarrAccessInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestZarrAccess"""

        document = "fragment ZarrAccessGrant on ZarrAccessGrant {\n  accessKey\n  secretKey\n  sessionToken\n  expiresIn\n  path\n  key\n  bucket\n  __typename\n}\n\nmutation RequestZarrAccess($input: RequestZarrAccessInput!) {\n  requestZarrAccess(input: $input) {\n    ...ZarrAccessGrant\n    __typename\n  }\n}"


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


class CreateModEnvironmentMutation(BaseModel):
    """No documentation found for this operation."""

    create_mod_environment: ModEnvironment = Field(alias="createModEnvironment")
    "Create a mechanism from a mod file"

    class Arguments(BaseModel):
        """Arguments for CreateModEnvironment"""

        input: CreateModEnvironmentInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateModEnvironment"""

        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nmutation CreateModEnvironment($input: CreateModEnvironmentInput!) {\n  createModEnvironment(input: $input) {\n    ...ModEnvironment\n    __typename\n  }\n}"


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

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Experiment on Experiment {\n  name\n  id\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  recordingViews {\n    label\n    recording {\n      ...Recording\n      __typename\n    }\n    __typename\n  }\n  stimulusViews {\n    label\n    stimulus {\n      ...Stimulus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation CreateExperiment($input: CreateExperimentInput!) {\n  createExperiment(input: $input) {\n    ...Experiment\n    __typename\n  }\n}"


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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation CreateNeuronmodel($input: CreateNeuronModelInput!) {\n  createNeuronModel(input: $input) {\n    ...NeuronModel\n    __typename\n  }\n}"


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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nmutation CreateSimulation($input: CreateSimulationInput!) {\n  createSimulation(input: $input) {\n    ...Simulation\n    __typename\n  }\n}"


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


class GetBlockQuery(BaseModel):
    """No documentation found for this operation."""

    block: Block

    class Arguments(BaseModel):
        """Arguments for GetBlock"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetBlock"""

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignalChannel on AnalogSignalChannel {\n  id\n  index\n  trace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment AnalogSignal on AnalogSignal {\n  id\n  unit\n  channels {\n    ...AnalogSignalChannel\n    __typename\n  }\n  __typename\n}\n\nfragment BlockGroup on BlockGroup {\n  id\n  name\n  __typename\n}\n\nfragment BlockSegment on BlockSegment {\n  id\n  analogSignals {\n    ...AnalogSignal\n    __typename\n  }\n  __typename\n}\n\nfragment Block on Block {\n  id\n  segments {\n    ...BlockSegment\n    __typename\n  }\n  groups {\n    ...BlockGroup\n    __typename\n  }\n  __typename\n}\n\nquery GetBlock($id: ID!) {\n  block(id: $id) {\n    ...Block\n    __typename\n  }\n}"


class SearchBlocksQueryOptions(BaseModel):
    """No documentation"""

    typename: Literal["Block"] = Field(
        alias="__typename", default="Block", exclude=True
    )
    value: ID
    label: str


class SearchBlocksQuery(BaseModel):
    """No documentation found for this operation."""

    options: List[SearchBlocksQueryOptions]

    class Arguments(BaseModel):
        """Arguments for SearchBlocks"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for SearchBlocks"""

        document = "query SearchBlocks($search: String, $values: [ID!]) {\n  options: blocks(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


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

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Experiment on Experiment {\n  name\n  id\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  recordingViews {\n    label\n    recording {\n      ...Recording\n      __typename\n    }\n    __typename\n  }\n  stimulusViews {\n    label\n    stimulus {\n      ...Stimulus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetExperiment($id: ID!) {\n  experiment(id: $id) {\n    ...Experiment\n    __typename\n  }\n}"


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

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Experiment on Experiment {\n  name\n  id\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  recordingViews {\n    label\n    recording {\n      ...Recording\n      __typename\n    }\n    __typename\n  }\n  stimulusViews {\n    label\n    stimulus {\n      ...Stimulus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery ListExperiments($filter: ExperimentFilter, $pagination: OffsetPaginationInput) {\n  experiments(filters: $filter, pagination: $pagination) {\n    ...Experiment\n    __typename\n  }\n}"


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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetNeuronModel($id: ID!) {\n  neuronModel(id: $id) {\n    ...NeuronModel\n    __typename\n  }\n}"


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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery ListNeuronModels($filter: NeuronModelFilter, $pagination: OffsetPaginationInput) {\n  neuronModels(filters: $filter, pagination: $pagination) {\n    ...NeuronModel\n    __typename\n  }\n}"


class GetRecordingQuery(BaseModel):
    """No documentation found for this operation."""

    recording: DetailRecording
    "Returns a list of images"

    class Arguments(BaseModel):
        """Arguments for GetRecording"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetRecording"""

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment DetailRecording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  simulation {\n    ...Simulation\n    __typename\n  }\n  __typename\n}\n\nquery GetRecording($id: ID!) {\n  recording(id: $id) {\n    ...DetailRecording\n    __typename\n  }\n}"


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

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nquery ListRecordings($filter: RecordingFilter, $pagination: OffsetPaginationInput) {\n  recordings(filters: $filter, pagination: $pagination) {\n    ...Recording\n    __typename\n  }\n}"


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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nquery GetSimulation($id: ID!) {\n  simulation(id: $id) {\n    ...Simulation\n    __typename\n  }\n}"


class SearchSimulationsQueryOptions(SimulationTrait, BaseModel):
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

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nquery ListSimulations($filter: SimulationFilter, $pagination: OffsetPaginationInput) {\n  simulations(filters: $filter, pagination: $pagination) {\n    ...Simulation\n    __typename\n  }\n}"


class GetStimulusQuery(BaseModel):
    """No documentation found for this operation."""

    stimulus: DetailStimulus
    "Returns a list of images"

    class Arguments(BaseModel):
        """Arguments for GetStimulus"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetStimulus"""

        document = "fragment GlobalParamMap on GlobalParamMap {\n  param\n  value\n  __typename\n}\n\nfragment SectionParamMap on SectionParamMap {\n  param\n  mechanism\n  value\n  __typename\n}\n\nfragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment Compartment on Compartment {\n  id\n  mechanisms\n  globalParams {\n    ...GlobalParamMap\n    __typename\n  }\n  sectionParams {\n    ...SectionParamMap\n    __typename\n  }\n  __typename\n}\n\nfragment Mechanism on Mechanism {\n  id\n  name\n  parameters {\n    key\n    kind\n    __typename\n  }\n  __typename\n}\n\nfragment Section on Section {\n  id\n  length\n  diam\n  coords {\n    x\n    y\n    z\n    __typename\n  }\n  category\n  nseg\n  connections {\n    parent\n    location\n    __typename\n  }\n  __typename\n}\n\nfragment Cell on Cell {\n  id\n  biophysics {\n    compartments {\n      ...Compartment\n      __typename\n    }\n    __typename\n  }\n  topology {\n    sections {\n      ...Section\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ExpTwoSynapse on Exp2Synapse {\n  id\n  tau1\n  tau2\n  e\n  cell\n  location\n  position\n  __typename\n}\n\nfragment ModEnvironment on ModEnvironment {\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  mechanisms {\n    ...Mechanism\n    __typename\n  }\n  __typename\n}\n\nfragment NetStimulator on NetStimulator {\n  id\n  interval\n  number\n  start\n  __typename\n}\n\nfragment SynapticConnection on SynapticConnection {\n  id\n  netStimulator\n  synapse\n  weight\n  threshold\n  delay\n  __typename\n}\n\nfragment NeuronModel on NeuronModel {\n  id\n  name\n  environment {\n    ...ModEnvironment\n    __typename\n  }\n  config {\n    vInit\n    celsius\n    cells {\n      ...Cell\n      __typename\n    }\n    netSynapses {\n      ...ExpTwoSynapse\n      __typename\n    }\n    netConnections {\n      ...SynapticConnection\n      __typename\n    }\n    netStimulators {\n      ...NetStimulator\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment Recording on Recording {\n  id\n  label\n  cell\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nfragment Simulation on Simulation {\n  id\n  model {\n    ...NeuronModel\n    __typename\n  }\n  duration\n  recordings {\n    ...Recording\n    __typename\n  }\n  stimuli {\n    ...Stimulus\n    __typename\n  }\n  timeTrace {\n    ...Trace\n    __typename\n  }\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment DetailStimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  simulation {\n    ...Simulation\n    __typename\n  }\n  __typename\n}\n\nquery GetStimulus($id: ID!) {\n  stimulus(id: $id) {\n    ...DetailStimulus\n    __typename\n  }\n}"


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

        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Stimulus on Stimulus {\n  id\n  label\n  cell\n  kind\n  trace {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  position\n  location\n  __typename\n}\n\nquery ListStimuli($filter: StimulusFilter, $pagination: OffsetPaginationInput) {\n  stimuli(filters: $filter, pagination: $pagination) {\n    ...Stimulus\n    __typename\n  }\n}"


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


async def arequest_bigfile_upload(
    original_file_name: str,
    file_size: Optional[int] = None,
    content_type: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> BigFileUploadGrant:
    """RequestBigfileUpload

    Request an upload grant for a big file store

    Args:
        original_file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        file_size: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        content_type: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        host: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        port: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        BigFileUploadGrant
    """
    return (
        await aexecute(
            RequestBigfileUploadMutation,
            {
                "input": {
                    "originalFileName": original_file_name,
                    "fileSize": file_size,
                    "contentType": content_type,
                    "host": host,
                    "port": port,
                }
            },
            rath=rath,
        )
    ).request_bigfile_upload


def request_bigfile_upload(
    original_file_name: str,
    file_size: Optional[int] = None,
    content_type: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> BigFileUploadGrant:
    """RequestBigfileUpload

    Request an upload grant for a big file store

    Args:
        original_file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        file_size: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        content_type: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        host: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        port: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        BigFileUploadGrant
    """
    return execute(
        RequestBigfileUploadMutation,
        {
            "input": {
                "originalFileName": original_file_name,
                "fileSize": file_size,
                "contentType": content_type,
                "host": host,
                "port": port,
            }
        },
        rath=rath,
    ).request_bigfile_upload


async def afinish_bigfile_upload(
    store_id: str, valid: bool, rath: Optional[ElektroRath] = None
) -> BigFileStore:
    """FinishBigfileUpload

    Finalize a big file upload after the client has written the object

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        valid: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        BigFileStore
    """
    return (
        await aexecute(
            FinishBigfileUploadMutation,
            {"input": {"storeId": store_id, "valid": valid}},
            rath=rath,
        )
    ).finish_bigfile_upload


def finish_bigfile_upload(
    store_id: str, valid: bool, rath: Optional[ElektroRath] = None
) -> BigFileStore:
    """FinishBigfileUpload

    Finalize a big file upload after the client has written the object

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        valid: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        BigFileStore
    """
    return execute(
        FinishBigfileUploadMutation,
        {"input": {"storeId": store_id, "valid": valid}},
        rath=rath,
    ).finish_bigfile_upload


async def arequest_bigfile_access(
    store_id: str, rath: Optional[ElektroRath] = None
) -> BigFileAccessGrant:
    """RequestBigfileAccess

    Request temporary S3 read credentials for a big file

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        BigFileAccessGrant
    """
    return (
        await aexecute(
            RequestBigfileAccessMutation, {"input": {"storeId": store_id}}, rath=rath
        )
    ).request_bigfile_access


def request_bigfile_access(
    store_id: str, rath: Optional[ElektroRath] = None
) -> BigFileAccessGrant:
    """RequestBigfileAccess

    Request temporary S3 read credentials for a big file

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        BigFileAccessGrant
    """
    return execute(
        RequestBigfileAccessMutation, {"input": {"storeId": store_id}}, rath=rath
    ).request_bigfile_access


async def arequest_media_upload(
    original_file_name: str,
    file_size: Optional[int] = None,
    content_type: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> MediaUploadGrant:
    """RequestMediaUpload

    Upload media and return a URL for access

    Args:
        original_file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        file_size: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        content_type: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        MediaUploadGrant
    """
    return (
        await aexecute(
            RequestMediaUploadMutation,
            {
                "input": {
                    "originalFileName": original_file_name,
                    "fileSize": file_size,
                    "contentType": content_type,
                }
            },
            rath=rath,
        )
    ).request_media_upload


def request_media_upload(
    original_file_name: str,
    file_size: Optional[int] = None,
    content_type: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> MediaUploadGrant:
    """RequestMediaUpload

    Upload media and return a URL for access

    Args:
        original_file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        file_size: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        content_type: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        MediaUploadGrant
    """
    return execute(
        RequestMediaUploadMutation,
        {
            "input": {
                "originalFileName": original_file_name,
                "fileSize": file_size,
                "contentType": content_type,
            }
        },
        rath=rath,
    ).request_media_upload


async def afinish_media_upload(
    store_id: str, valid: bool, rath: Optional[ElektroRath] = None
) -> MediaStore:
    """FinishMediaUpload

    Finalize a media upload after the client has written the object

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        valid: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        MediaStore
    """
    return (
        await aexecute(
            FinishMediaUploadMutation,
            {"input": {"storeId": store_id, "valid": valid}},
            rath=rath,
        )
    ).finish_media_upload


def finish_media_upload(
    store_id: str, valid: bool, rath: Optional[ElektroRath] = None
) -> MediaStore:
    """FinishMediaUpload

    Finalize a media upload after the client has written the object

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        valid: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        MediaStore
    """
    return execute(
        FinishMediaUploadMutation,
        {"input": {"storeId": store_id, "valid": valid}},
        rath=rath,
    ).finish_media_upload


async def arequest_media_access(
    store_id: str, rath: Optional[ElektroRath] = None
) -> MediaAccessGrant:
    """RequestMediaAccess

    Request temporary S3 read credentials for a media file

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        MediaAccessGrant
    """
    return (
        await aexecute(
            RequestMediaAccessMutation, {"input": {"storeId": store_id}}, rath=rath
        )
    ).request_media_access


def request_media_access(
    store_id: str, rath: Optional[ElektroRath] = None
) -> MediaAccessGrant:
    """RequestMediaAccess

    Request temporary S3 read credentials for a media file

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        MediaAccessGrant
    """
    return execute(
        RequestMediaAccessMutation, {"input": {"storeId": store_id}}, rath=rath
    ).request_media_access


async def arequest_parquet_upload(
    original_file_name: str,
    content_type: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> ParquetUploadGrant:
    """RequestParquetUpload

    Request an upload grant for a Parquet store

    Args:
        original_file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        content_type: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        host: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        port: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ParquetUploadGrant
    """
    return (
        await aexecute(
            RequestParquetUploadMutation,
            {
                "input": {
                    "originalFileName": original_file_name,
                    "contentType": content_type,
                    "host": host,
                    "port": port,
                }
            },
            rath=rath,
        )
    ).request_parquet_upload


def request_parquet_upload(
    original_file_name: str,
    content_type: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> ParquetUploadGrant:
    """RequestParquetUpload

    Request an upload grant for a Parquet store

    Args:
        original_file_name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        content_type: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        host: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        port: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ParquetUploadGrant
    """
    return execute(
        RequestParquetUploadMutation,
        {
            "input": {
                "originalFileName": original_file_name,
                "contentType": content_type,
                "host": host,
                "port": port,
            }
        },
        rath=rath,
    ).request_parquet_upload


async def afinish_parquet_upload(
    store_id: str, valid: bool, rath: Optional[ElektroRath] = None
) -> ParquetStore:
    """FinishParquetUpload

    Finalize a Parquet upload after the client has written the object

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        valid: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ParquetStore
    """
    return (
        await aexecute(
            FinishParquetUploadMutation,
            {"input": {"storeId": store_id, "valid": valid}},
            rath=rath,
        )
    ).finish_parquet_upload


def finish_parquet_upload(
    store_id: str, valid: bool, rath: Optional[ElektroRath] = None
) -> ParquetStore:
    """FinishParquetUpload

    Finalize a Parquet upload after the client has written the object

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        valid: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ParquetStore
    """
    return execute(
        FinishParquetUploadMutation,
        {"input": {"storeId": store_id, "valid": valid}},
        rath=rath,
    ).finish_parquet_upload


async def arequest_parquet_access(
    store_id: str, rath: Optional[ElektroRath] = None
) -> ParquetAccessGrant:
    """RequestParquetAccess

    Request temporary S3 read credentials for a Parquet file

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ParquetAccessGrant
    """
    return (
        await aexecute(
            RequestParquetAccessMutation, {"input": {"storeId": store_id}}, rath=rath
        )
    ).request_parquet_access


def request_parquet_access(
    store_id: str, rath: Optional[ElektroRath] = None
) -> ParquetAccessGrant:
    """RequestParquetAccess

    Request temporary S3 read credentials for a Parquet file

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ParquetAccessGrant
    """
    return execute(
        RequestParquetAccessMutation, {"input": {"storeId": store_id}}, rath=rath
    ).request_parquet_access


async def arequest_zarr_upload(
    shape: Optional[Iterable[int]] = None,
    chunks: Optional[Iterable[int]] = None,
    version: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> ZarrUploadGrant:
    """RequestZarrUpload

    Request an upload grant for a Zarr store

    Args:
        shape: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required) (list)
        chunks: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required) (list)
        version: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        host: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        port: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ZarrUploadGrant
    """
    return (
        await aexecute(
            RequestZarrUploadMutation,
            {
                "input": {
                    "shape": shape,
                    "chunks": chunks,
                    "version": version,
                    "host": host,
                    "port": port,
                }
            },
            rath=rath,
        )
    ).request_zarr_upload


def request_zarr_upload(
    shape: Optional[Iterable[int]] = None,
    chunks: Optional[Iterable[int]] = None,
    version: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    rath: Optional[ElektroRath] = None,
) -> ZarrUploadGrant:
    """RequestZarrUpload

    Request an upload grant for a Zarr store

    Args:
        shape: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required) (list)
        chunks: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. (required) (list)
        version: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        host: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        port: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ZarrUploadGrant
    """
    return execute(
        RequestZarrUploadMutation,
        {
            "input": {
                "shape": shape,
                "chunks": chunks,
                "version": version,
                "host": host,
                "port": port,
            }
        },
        rath=rath,
    ).request_zarr_upload


async def afinish_zarr_upload(
    store_id: str, valid: bool, rath: Optional[ElektroRath] = None
) -> ZarrStore:
    """FinishZarrUpload

    Finalize a Zarr upload after the client has written the object

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        valid: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ZarrStore
    """
    return (
        await aexecute(
            FinishZarrUploadMutation,
            {"input": {"storeId": store_id, "valid": valid}},
            rath=rath,
        )
    ).finish_zarr_upload


def finish_zarr_upload(
    store_id: str, valid: bool, rath: Optional[ElektroRath] = None
) -> ZarrStore:
    """FinishZarrUpload

    Finalize a Zarr upload after the client has written the object

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        valid: The `Boolean` scalar type represents `true` or `false`. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ZarrStore
    """
    return execute(
        FinishZarrUploadMutation,
        {"input": {"storeId": store_id, "valid": valid}},
        rath=rath,
    ).finish_zarr_upload


async def arequest_zarr_access(
    store_id: str, rath: Optional[ElektroRath] = None
) -> ZarrAccessGrant:
    """RequestZarrAccess

    Request temporary S3 read credentials for a Zarr store

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ZarrAccessGrant
    """
    return (
        await aexecute(
            RequestZarrAccessMutation, {"input": {"storeId": store_id}}, rath=rath
        )
    ).request_zarr_access


def request_zarr_access(
    store_id: str, rath: Optional[ElektroRath] = None
) -> ZarrAccessGrant:
    """RequestZarrAccess

    Request temporary S3 read credentials for a Zarr store

    Args:
        store_id: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ZarrAccessGrant
    """
    return execute(
        RequestZarrAccessMutation, {"input": {"storeId": store_id}}, rath=rath
    ).request_zarr_access


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


async def acreate_mod_environment(
    name: str,
    zip_file: BigFileLike,
    mechanisms: Iterable[MechanismInput],
    description: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> ModEnvironment:
    """CreateModEnvironment

    Create a mechanism from a mod file

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        zip_file: A type representing a big file store reference, which can be either a string ID or a more complex object. (required)
        mechanisms: Input for creating a mechanism (required) (list) (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ModEnvironment
    """
    return (
        await aexecute(
            CreateModEnvironmentMutation,
            {
                "input": {
                    "name": name,
                    "description": description,
                    "zipFile": zip_file,
                    "mechanisms": mechanisms,
                }
            },
            rath=rath,
        )
    ).create_mod_environment


def create_mod_environment(
    name: str,
    zip_file: BigFileLike,
    mechanisms: Iterable[MechanismInput],
    description: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> ModEnvironment:
    """CreateModEnvironment

    Create a mechanism from a mod file

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        zip_file: A type representing a big file store reference, which can be either a string ID or a more complex object. (required)
        mechanisms: Input for creating a mechanism (required) (list) (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ModEnvironment
    """
    return execute(
        CreateModEnvironmentMutation,
        {
            "input": {
                "name": name,
                "description": description,
                "zipFile": zip_file,
                "mechanisms": mechanisms,
            }
        },
        rath=rath,
    ).create_mod_environment


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
    environment: Optional[IDCoercible] = None,
    parent: Optional[IDCoercible] = None,
    description: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> NeuronModel:
    """CreateNeuronmodel

    Create a new neuron model

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        environment: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        parent: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        config:  (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        NeuronModel
    """
    return (
        await aexecute(
            CreateNeuronmodelMutation,
            {
                "input": {
                    "name": name,
                    "environment": environment,
                    "parent": parent,
                    "description": description,
                    "config": config,
                }
            },
            rath=rath,
        )
    ).create_neuron_model


def create_neuronmodel(
    name: str,
    config: ModelConfigInput,
    environment: Optional[IDCoercible] = None,
    parent: Optional[IDCoercible] = None,
    description: Optional[str] = None,
    rath: Optional[ElektroRath] = None,
) -> NeuronModel:
    """CreateNeuronmodel

    Create a new neuron model

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        environment: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        parent: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        description: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        config:  (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        NeuronModel
    """
    return execute(
        CreateNeuronmodelMutation,
        {
            "input": {
                "name": name,
                "environment": environment,
                "parent": parent,
                "description": description,
                "config": config,
            }
        },
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
    duration: Millisecond,
    time_trace: Optional[ArrayLike] = None,
    dt: Optional[Millisecond] = None,
    rath: Optional[ElektroRath] = None,
) -> Simulation:
    """CreateSimulation

    Create a new simulsation

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        model: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        recordings:  (required) (list) (required)
        stimuli:  (required) (list) (required)
        time_trace: A type representing an array-like store reference, which can be either a string ID or a more complex object.
        duration: The `Matrix` scalar type represents a matrix values as specified by (required)
        dt: The `Matrix` scalar type represents a matrix values as specified by
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
    duration: Millisecond,
    time_trace: Optional[ArrayLike] = None,
    dt: Optional[Millisecond] = None,
    rath: Optional[ElektroRath] = None,
) -> Simulation:
    """CreateSimulation

    Create a new simulsation

    Args:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        model: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        recordings:  (required) (list) (required)
        stimuli:  (required) (list) (required)
        time_trace: A type representing an array-like store reference, which can be either a string ID or a more complex object.
        duration: The `Matrix` scalar type represents a matrix values as specified by (required)
        dt: The `Matrix` scalar type represents a matrix values as specified by
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
    array: ArrayLike,
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
    array: ArrayLike,
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


async def aget_block(id: ID, rath: Optional[ElektroRath] = None) -> Block:
    """GetBlock


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Block
    """
    return (await aexecute(GetBlockQuery, {"id": id}, rath=rath)).block


def get_block(id: ID, rath: Optional[ElektroRath] = None) -> Block:
    """GetBlock


    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Block
    """
    return execute(GetBlockQuery, {"id": id}, rath=rath).block


async def asearch_blocks(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchBlocksQueryOptions]:
    """SearchBlocks


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchBlocksQueryBlocks]
    """
    return (
        await aexecute(
            SearchBlocksQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_blocks(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> List[SearchBlocksQueryOptions]:
    """SearchBlocks


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchBlocksQueryBlocks]
    """
    return execute(
        SearchBlocksQuery, {"search": search, "values": values}, rath=rath
    ).options


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


async def aget_recording(id: ID, rath: Optional[ElektroRath] = None) -> DetailRecording:
    """GetRecording

    Returns a list of images

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        DetailRecording
    """
    return (await aexecute(GetRecordingQuery, {"id": id}, rath=rath)).recording


def get_recording(id: ID, rath: Optional[ElektroRath] = None) -> DetailRecording:
    """GetRecording

    Returns a list of images

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        DetailRecording
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


async def aget_stimulus(id: ID, rath: Optional[ElektroRath] = None) -> DetailStimulus:
    """GetStimulus

    Returns a list of images

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        DetailStimulus
    """
    return (await aexecute(GetStimulusQuery, {"id": id}, rath=rath)).stimulus


def get_stimulus(id: ID, rath: Optional[ElektroRath] = None) -> DetailStimulus:
    """GetStimulus

    Returns a list of images

    Args:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        DetailStimulus
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


ArgPortInput.model_rebuild()
AssignWidgetInput.model_rebuild()
BiophysicsInput.model_rebuild()
BlockSegmentInput.model_rebuild()
CellInput.model_rebuild()
CompartmentInput.model_rebuild()
CreateExperimentInput.model_rebuild()
CreateModEnvironmentInput.model_rebuild()
CreateNeuronModelInput.model_rebuild()
CreateSimulationInput.model_rebuild()
DatasetFilter.model_rebuild()
ExperimentFilter.model_rebuild()
ModelCollectionFilter.model_rebuild()
ModelConfigInput.model_rebuild()
NeuronModelFilter.model_rebuild()
RecordingFilter.model_rebuild()
SimulationFilter.model_rebuild()
StimulusFilter.model_rebuild()
TraceFilter.model_rebuild()

from typing import (
    AsyncIterator,
    Tuple,
    Any,
    Union,
    Optional,
    Annotated,
    Literal,
    List,
    Iterator,
    Iterable,
)
from elektro.traits import (
    HasParquestStoreTrait,
    HasDownloadAccessor,
    HasZarrStoreTrait,
    HasZarrStoreAccessor,
    HasParquetStoreAccesor,
    IsVectorizableTrait,
    HasPresignedDownloadAccessor,
)
from elektro.scalars import (
    FiveDVector,
    FourByFourMatrix,
    MeshLike,
    Micrometers,
    Milliseconds,
    ParquetLike,
    FileLike,
    Upload,
    ArrayLike,
)
from pydantic import ConfigDict, BaseModel, Field
from enum import Enum
from rath.scalars import ID
from elektro.funcs import execute, subscribe, asubscribe, aexecute
from datetime import datetime
from elektro.rath import MikroNextRath


class RoiKind(str, Enum):
    ELLIPSIS = "ELLIPSIS"
    POLYGON = "POLYGON"
    LINE = "LINE"
    RECTANGLE = "RECTANGLE"
    SPECTRAL_RECTANGLE = "SPECTRAL_RECTANGLE"
    TEMPORAL_RECTANGLE = "TEMPORAL_RECTANGLE"
    CUBE = "CUBE"
    SPECTRAL_CUBE = "SPECTRAL_CUBE"
    TEMPORAL_CUBE = "TEMPORAL_CUBE"
    HYPERCUBE = "HYPERCUBE"
    SPECTRAL_HYPERCUBE = "SPECTRAL_HYPERCUBE"
    PATH = "PATH"
    FRAME = "FRAME"
    SLICE = "SLICE"
    POINT = "POINT"


class ColorMap(str, Enum):
    VIRIDIS = "VIRIDIS"
    PLASMA = "PLASMA"
    INFERNO = "INFERNO"
    MAGMA = "MAGMA"
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    INTENSITY = "INTENSITY"


class Blending(str, Enum):
    ADDITIVE = "ADDITIVE"
    MULTIPLICATIVE = "MULTIPLICATIVE"


class ScanDirection(str, Enum):
    ROW_COLUMN_SLICE = "ROW_COLUMN_SLICE"
    COLUMN_ROW_SLICE = "COLUMN_ROW_SLICE"
    SLICE_ROW_COLUMN = "SLICE_ROW_COLUMN"
    ROW_COLUMN_SLICE_SNAKE = "ROW_COLUMN_SLICE_SNAKE"
    COLUMN_ROW_SLICE_SNAKE = "COLUMN_ROW_SLICE_SNAKE"
    SLICE_ROW_COLUMN_SNAKE = "SLICE_ROW_COLUMN_SNAKE"


class RenderNodeKind(str, Enum):
    CONTEXT = "CONTEXT"
    OVERLAY = "OVERLAY"
    GRID = "GRID"
    SPIT = "SPIT"


class ViewFilter(BaseModel):
    is_global: Optional[bool] = Field(alias="isGlobal", default=None)
    provenance: Optional["ProvenanceFilter"] = None
    and_: Optional["ViewFilter"] = Field(alias="AND", default=None)
    or_: Optional["ViewFilter"] = Field(alias="OR", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ProvenanceFilter(BaseModel):
    during: Optional[str] = None
    and_: Optional["ProvenanceFilter"] = Field(alias="AND", default=None)
    or_: Optional["ProvenanceFilter"] = Field(alias="OR", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StrFilterLookup(BaseModel):
    exact: Optional[str] = None
    i_exact: Optional[str] = Field(alias="iExact", default=None)
    contains: Optional[str] = None
    i_contains: Optional[str] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[str, ...]] = Field(alias="inList", default=None)
    gt: Optional[str] = None
    gte: Optional[str] = None
    lt: Optional[str] = None
    lte: Optional[str] = None
    starts_with: Optional[str] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[str] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[str] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[str] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[str, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[str] = Field(alias="nExact", default=None)
    n_i_exact: Optional[str] = Field(alias="nIExact", default=None)
    n_contains: Optional[str] = Field(alias="nContains", default=None)
    n_i_contains: Optional[str] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[str, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[str] = Field(alias="nGt", default=None)
    n_gte: Optional[str] = Field(alias="nGte", default=None)
    n_lt: Optional[str] = Field(alias="nLt", default=None)
    n_lte: Optional[str] = Field(alias="nLte", default=None)
    n_starts_with: Optional[str] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[str] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[str] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[str] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[str, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OffsetPaginationInput(BaseModel):
    offset: int
    limit: int
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ImageFilter(BaseModel):
    name: Optional[StrFilterLookup] = None
    ids: Optional[Tuple[ID, ...]] = None
    store: Optional["ZarrStoreFilter"] = None
    dataset: Optional["DatasetFilter"] = None
    transformation_views: Optional["AffineTransformationViewFilter"] = Field(
        alias="transformationViews", default=None
    )
    timepoint_views: Optional["TimepointViewFilter"] = Field(
        alias="timepointViews", default=None
    )
    not_derived: Optional[bool] = Field(alias="notDerived", default=None)
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["ImageFilter"] = Field(alias="AND", default=None)
    or_: Optional["ImageFilter"] = Field(alias="OR", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ZarrStoreFilter(BaseModel):
    shape: Optional["IntFilterLookup"] = None
    and_: Optional["ZarrStoreFilter"] = Field(alias="AND", default=None)
    or_: Optional["ZarrStoreFilter"] = Field(alias="OR", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class IntFilterLookup(BaseModel):
    exact: Optional[int] = None
    i_exact: Optional[int] = Field(alias="iExact", default=None)
    contains: Optional[int] = None
    i_contains: Optional[int] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[int, ...]] = Field(alias="inList", default=None)
    gt: Optional[int] = None
    gte: Optional[int] = None
    lt: Optional[int] = None
    lte: Optional[int] = None
    starts_with: Optional[int] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[int] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[int] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[int] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[int, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[int] = Field(alias="nExact", default=None)
    n_i_exact: Optional[int] = Field(alias="nIExact", default=None)
    n_contains: Optional[int] = Field(alias="nContains", default=None)
    n_i_contains: Optional[int] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[int, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[int] = Field(alias="nGt", default=None)
    n_gte: Optional[int] = Field(alias="nGte", default=None)
    n_lt: Optional[int] = Field(alias="nLt", default=None)
    n_lte: Optional[int] = Field(alias="nLte", default=None)
    n_starts_with: Optional[int] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[int] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[int] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[int] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[int, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DatasetFilter(BaseModel):
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["DatasetFilter"] = Field(alias="AND", default=None)
    or_: Optional["DatasetFilter"] = Field(alias="OR", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AffineTransformationViewFilter(BaseModel):
    is_global: Optional[bool] = Field(alias="isGlobal", default=None)
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["AffineTransformationViewFilter"] = Field(alias="AND", default=None)
    or_: Optional["AffineTransformationViewFilter"] = Field(alias="OR", default=None)
    stage: Optional["StageFilter"] = None
    pixel_size: Optional["FloatFilterLookup"] = Field(alias="pixelSize", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StageFilter(BaseModel):
    ids: Optional[Tuple[ID, ...]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    kind: Optional[str] = None
    name: Optional[StrFilterLookup] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["StageFilter"] = Field(alias="AND", default=None)
    or_: Optional["StageFilter"] = Field(alias="OR", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FloatFilterLookup(BaseModel):
    exact: Optional[float] = None
    i_exact: Optional[float] = Field(alias="iExact", default=None)
    contains: Optional[float] = None
    i_contains: Optional[float] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[float, ...]] = Field(alias="inList", default=None)
    gt: Optional[float] = None
    gte: Optional[float] = None
    lt: Optional[float] = None
    lte: Optional[float] = None
    starts_with: Optional[float] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[float] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[float] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[float] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[float, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[float] = Field(alias="nExact", default=None)
    n_i_exact: Optional[float] = Field(alias="nIExact", default=None)
    n_contains: Optional[float] = Field(alias="nContains", default=None)
    n_i_contains: Optional[float] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[float, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[float] = Field(alias="nGt", default=None)
    n_gte: Optional[float] = Field(alias="nGte", default=None)
    n_lt: Optional[float] = Field(alias="nLt", default=None)
    n_lte: Optional[float] = Field(alias="nLte", default=None)
    n_starts_with: Optional[float] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[float] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[float] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[float] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[float, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class TimepointViewFilter(BaseModel):
    is_global: Optional[bool] = Field(alias="isGlobal", default=None)
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["TimepointViewFilter"] = Field(alias="AND", default=None)
    or_: Optional["TimepointViewFilter"] = Field(alias="OR", default=None)
    era: Optional["EraFilter"] = None
    ms_since_start: Optional[float] = Field(alias="msSinceStart", default=None)
    index_since_start: Optional[int] = Field(alias="indexSinceStart", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EraFilter(BaseModel):
    id: Optional[ID] = None
    begin: Optional[datetime] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["EraFilter"] = Field(alias="AND", default=None)
    or_: Optional["EraFilter"] = Field(alias="OR", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestUploadInput(BaseModel):
    key: str
    datalayer: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestAccessInput(BaseModel):
    store: ID
    duration: Optional[int] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestTableUploadInput(BaseModel):
    key: str
    datalayer: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestTableAccessInput(BaseModel):
    store: ID
    duration: Optional[int] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestMeshUploadInput(BaseModel):
    key: str
    datalayer: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestFileUploadInput(BaseModel):
    key: str
    datalayer: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RequestFileAccessInput(BaseModel):
    store: ID
    duration: Optional[int] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FromArrayLikeInput(BaseModel):
    """Input type for creating an image from an array-like object"""

    array: ArrayLike
    "The array-like object to create the image from"
    name: str
    "The name of the image"
    dataset: Optional[ID] = None
    "Optional dataset ID to associate the image with"
    channel_views: Optional[Tuple["PartialChannelViewInput", ...]] = Field(
        alias="channelViews", default=None
    )
    "Optional list of channel views"
    transformation_views: Optional[
        Tuple["PartialAffineTransformationViewInput", ...]
    ] = Field(alias="transformationViews", default=None)
    "Optional list of affine transformation views"
    acquisition_views: Optional[Tuple["PartialAcquisitionViewInput", ...]] = Field(
        alias="acquisitionViews", default=None
    )
    "Optional list of acquisition views"
    pixel_views: Optional[Tuple["PartialPixelViewInput", ...]] = Field(
        alias="pixelViews", default=None
    )
    "Optional list of pixel views"
    structure_views: Optional[Tuple["PartialStructureViewInput", ...]] = Field(
        alias="structureViews", default=None
    )
    "Optional list of structure views"
    rgb_views: Optional[Tuple["PartialRGBViewInput", ...]] = Field(
        alias="rgbViews", default=None
    )
    "Optional list of RGB views"
    timepoint_views: Optional[Tuple["PartialTimepointViewInput", ...]] = Field(
        alias="timepointViews", default=None
    )
    "Optional list of timepoint views"
    optics_views: Optional[Tuple["PartialOpticsViewInput", ...]] = Field(
        alias="opticsViews", default=None
    )
    "Optional list of optics views"
    scale_views: Optional[Tuple["PartialScaleViewInput", ...]] = Field(
        alias="scaleViews", default=None
    )
    "Optional list of scale views"
    tags: Optional[Tuple[str, ...]] = None
    "Optional list of tags to associate with the image"
    roi_views: Optional[Tuple["PartialROIViewInput", ...]] = Field(
        alias="roiViews", default=None
    )
    "Optional list of ROI views"
    file_views: Optional[Tuple["PartialFileViewInput", ...]] = Field(
        alias="fileViews", default=None
    )
    "Optional list of file views"
    derived_views: Optional[Tuple["PartialDerivedViewInput", ...]] = Field(
        alias="derivedViews", default=None
    )
    "Optional list of derived views"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialChannelViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    channel: ID
    "The ID of the channel this view is for"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialAffineTransformationViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    stage: Optional[ID] = None
    affine_matrix: FourByFourMatrix = Field(alias="affineMatrix")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialAcquisitionViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    description: Optional[str] = None
    acquired_at: Optional[datetime] = Field(alias="acquiredAt", default=None)
    operator: Optional[ID] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialPixelViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    linked_view: Optional[ID] = Field(alias="linkedView", default=None)
    range_labels: Optional[Tuple["RangePixelLabel", ...]] = Field(
        alias="rangeLabels", default=None
    )
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RangePixelLabel(BaseModel):
    group: Optional[ID] = None
    entity_kind: ID = Field(alias="entityKind")
    min: int
    max: int
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialStructureViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    structure: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialRGBViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    context: Optional[ID] = None
    gamma: Optional[float] = None
    contrast_limit_min: Optional[float] = Field(alias="contrastLimitMin", default=None)
    contrast_limit_max: Optional[float] = Field(alias="contrastLimitMax", default=None)
    rescale: Optional[bool] = None
    scale: Optional[float] = None
    active: Optional[bool] = None
    color_map: Optional[ColorMap] = Field(alias="colorMap", default=None)
    base_color: Optional[Tuple[float, ...]] = Field(alias="baseColor", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialTimepointViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    era: Optional[ID] = None
    ms_since_start: Optional[Milliseconds] = Field(alias="msSinceStart", default=None)
    index_since_start: Optional[int] = Field(alias="indexSinceStart", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialOpticsViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    instrument: Optional[ID] = None
    objective: Optional[ID] = None
    camera: Optional[ID] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialScaleViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    parent: Optional[ID] = None
    scale_x: Optional[float] = Field(alias="scaleX", default=None)
    scale_y: Optional[float] = Field(alias="scaleY", default=None)
    scale_z: Optional[float] = Field(alias="scaleZ", default=None)
    scale_t: Optional[float] = Field(alias="scaleT", default=None)
    scale_c: Optional[float] = Field(alias="scaleC", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialROIViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    roi: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialFileViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    file: ID
    series_identifier: Optional[str] = Field(alias="seriesIdentifier", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialDerivedViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    origin_image: ID = Field(alias="originImage")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RenderTreeInput(BaseModel):
    tree: "TreeInput"
    name: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class TreeInput(BaseModel):
    id: Optional[str] = None
    children: Tuple["TreeNodeInput", ...]
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class TreeNodeInput(BaseModel):
    kind: RenderNodeKind
    label: Optional[str] = None
    context: Optional[str] = None
    gap: Optional[int] = None
    children: Optional[Tuple["TreeNodeInput", ...]] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FromParquetLike(BaseModel):
    dataframe: ParquetLike
    "The parquet dataframe to create the table from"
    name: str
    "The name of the table"
    origins: Optional[Tuple[ID, ...]] = None
    "The IDs of tables this table was derived from"
    dataset: Optional[ID] = None
    "The dataset ID this table belongs to"
    label_accessors: Optional[Tuple["PartialLabelAccessorInput", ...]] = Field(
        alias="labelAccessors", default=None
    )
    "Label accessors to create for this table"
    image_accessors: Optional[Tuple["PartialImageAccessorInput", ...]] = Field(
        alias="imageAccessors", default=None
    )
    "Image accessors to create for this table"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialLabelAccessorInput(BaseModel):
    keys: Tuple[str, ...]
    min_index: Optional[int] = Field(alias="minIndex", default=None)
    max_index: Optional[int] = Field(alias="maxIndex", default=None)
    pixel_view: ID = Field(alias="pixelView")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PartialImageAccessorInput(BaseModel):
    keys: Tuple[str, ...]
    min_index: Optional[int] = Field(alias="minIndex", default=None)
    max_index: Optional[int] = Field(alias="maxIndex", default=None)
    image: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class MeshInput(BaseModel):
    mesh: MeshLike
    name: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class FromFileLike(BaseModel):
    name: str
    file: FileLike
    origins: Optional[Tuple[ID, ...]] = None
    dataset: Optional[ID] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RenderedPlotInput(BaseModel):
    name: str
    plot: Upload
    overlays: Optional[Tuple["OverlayInput", ...]] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OverlayInput(BaseModel):
    object: str
    identifier: str
    color: str
    x: int
    y: int
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ChannelInput(BaseModel):
    name: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StageInput(BaseModel):
    name: str
    instrument: Optional[ID] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateRGBContextInput(BaseModel):
    name: Optional[str] = None
    thumbnail: Optional[ID] = None
    image: ID
    views: Optional[Tuple[PartialRGBViewInput, ...]] = None
    z: Optional[int] = None
    t: Optional[int] = None
    c: Optional[int] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateRGBContextInput(BaseModel):
    id: ID
    name: Optional[str] = None
    thumbnail: Optional[ID] = None
    views: Optional[Tuple[PartialRGBViewInput, ...]] = None
    z: Optional[int] = None
    t: Optional[int] = None
    c: Optional[int] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateDatasetInput(BaseModel):
    name: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ChangeDatasetInput(BaseModel):
    name: str
    id: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RevertInput(BaseModel):
    id: ID
    history_id: ID = Field(alias="historyId")
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ViewCollectionInput(BaseModel):
    name: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class EraInput(BaseModel):
    name: str
    begin: Optional[datetime] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class LabelViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    label: str
    image: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RGBViewInput(BaseModel):
    collection: Optional[ID] = None
    "The collection this view belongs to"
    z_min: Optional[int] = Field(alias="zMin", default=None)
    "The minimum z coordinate of the view"
    z_max: Optional[int] = Field(alias="zMax", default=None)
    "The maximum z coordinate of the view"
    x_min: Optional[int] = Field(alias="xMin", default=None)
    "The minimum x coordinate of the view"
    x_max: Optional[int] = Field(alias="xMax", default=None)
    "The maximum x coordinate of the view"
    y_min: Optional[int] = Field(alias="yMin", default=None)
    "The minimum y coordinate of the view"
    y_max: Optional[int] = Field(alias="yMax", default=None)
    "The maximum y coordinate of the view"
    t_min: Optional[int] = Field(alias="tMin", default=None)
    "The minimum t coordinate of the view"
    t_max: Optional[int] = Field(alias="tMax", default=None)
    "The maximum t coordinate of the view"
    c_min: Optional[int] = Field(alias="cMin", default=None)
    "The minimum c (channel) coordinate of the view"
    c_max: Optional[int] = Field(alias="cMax", default=None)
    "The maximum c (channel) coordinate of the view"
    context: ID
    gamma: Optional[float] = None
    contrast_limit_min: Optional[float] = Field(alias="contrastLimitMin", default=None)
    contrast_limit_max: Optional[float] = Field(alias="contrastLimitMax", default=None)
    rescale: Optional[bool] = None
    scale: Optional[float] = None
    active: Optional[bool] = None
    color_map: Optional[ColorMap] = Field(alias="colorMap", default=None)
    base_color: Optional[Tuple[float, ...]] = Field(alias="baseColor", default=None)
    image: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class InstrumentInput(BaseModel):
    serial_number: str = Field(alias="serialNumber")
    manufacturer: Optional[str] = None
    name: Optional[str] = None
    model: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ObjectiveInput(BaseModel):
    serial_number: str = Field(alias="serialNumber")
    name: Optional[str] = None
    na: Optional[float] = None
    magnification: Optional[float] = None
    immersion: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CameraInput(BaseModel):
    serial_number: str = Field(alias="serialNumber")
    name: Optional[str] = None
    model: Optional[str] = None
    bit_depth: Optional[int] = Field(alias="bitDepth", default=None)
    sensor_size_x: Optional[int] = Field(alias="sensorSizeX", default=None)
    sensor_size_y: Optional[int] = Field(alias="sensorSizeY", default=None)
    pixel_size_x: Optional[Micrometers] = Field(alias="pixelSizeX", default=None)
    pixel_size_y: Optional[Micrometers] = Field(alias="pixelSizeY", default=None)
    manufacturer: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class SnapshotInput(BaseModel):
    file: Upload
    image: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RoiInput(BaseModel):
    image: ID
    "The image this ROI belongs to"
    vectors: Tuple[FiveDVector, ...]
    "The vector coordinates defining the ROI"
    kind: RoiKind
    "The type/kind of ROI"
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateRoiInput(BaseModel):
    roi: ID
    vectors: Optional[Tuple[FiveDVector, ...]] = None
    kind: Optional[RoiKind] = None
    entity: Optional[ID] = None
    entity_kind: Optional[ID] = Field(alias="entityKind", default=None)
    entity_group: Optional[ID] = Field(alias="entityGroup", default=None)
    entity_parent: Optional[ID] = Field(alias="entityParent", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DeleteRoiInput(BaseModel):
    id: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ViewBase(BaseModel):
    x_min: Optional[int] = Field(default=None, alias="xMin")
    x_max: Optional[int] = Field(default=None, alias="xMax")
    y_min: Optional[int] = Field(default=None, alias="yMin")
    y_max: Optional[int] = Field(default=None, alias="yMax")
    t_min: Optional[int] = Field(default=None, alias="tMin")
    t_max: Optional[int] = Field(default=None, alias="tMax")
    c_min: Optional[int] = Field(default=None, alias="cMin")
    c_max: Optional[int] = Field(default=None, alias="cMax")
    z_min: Optional[int] = Field(default=None, alias="zMin")
    z_max: Optional[int] = Field(default=None, alias="zMax")


class ViewCatch(ViewBase):
    typename: str = Field(alias="__typename", exclude=True)
    x_min: Optional[int] = Field(default=None, alias="xMin")
    x_max: Optional[int] = Field(default=None, alias="xMax")
    y_min: Optional[int] = Field(default=None, alias="yMin")
    y_max: Optional[int] = Field(default=None, alias="yMax")
    t_min: Optional[int] = Field(default=None, alias="tMin")
    t_max: Optional[int] = Field(default=None, alias="tMax")
    c_min: Optional[int] = Field(default=None, alias="cMin")
    c_max: Optional[int] = Field(default=None, alias="cMax")
    z_min: Optional[int] = Field(default=None, alias="zMin")
    z_max: Optional[int] = Field(default=None, alias="zMax")


class ViewFileView(ViewBase, BaseModel):
    typename: Literal["FileView"] = Field(
        alias="__typename", default="FileView", exclude=True
    )


class ViewAffineTransformationView(ViewBase, BaseModel):
    typename: Literal["AffineTransformationView"] = Field(
        alias="__typename", default="AffineTransformationView", exclude=True
    )


class ViewLabelView(ViewBase, BaseModel):
    typename: Literal["LabelView"] = Field(
        alias="__typename", default="LabelView", exclude=True
    )


class ViewChannelView(ViewBase, BaseModel):
    typename: Literal["ChannelView"] = Field(
        alias="__typename", default="ChannelView", exclude=True
    )


class ViewTimepointView(ViewBase, BaseModel):
    typename: Literal["TimepointView"] = Field(
        alias="__typename", default="TimepointView", exclude=True
    )


class ViewOpticsView(ViewBase, BaseModel):
    typename: Literal["OpticsView"] = Field(
        alias="__typename", default="OpticsView", exclude=True
    )


class ViewStructureView(ViewBase, BaseModel):
    typename: Literal["StructureView"] = Field(
        alias="__typename", default="StructureView", exclude=True
    )


class ViewScaleView(ViewBase, BaseModel):
    typename: Literal["ScaleView"] = Field(
        alias="__typename", default="ScaleView", exclude=True
    )


class ViewDerivedView(ViewBase, BaseModel):
    typename: Literal["DerivedView"] = Field(
        alias="__typename", default="DerivedView", exclude=True
    )


class ViewROIView(ViewBase, BaseModel):
    typename: Literal["ROIView"] = Field(
        alias="__typename", default="ROIView", exclude=True
    )


class ViewPixelView(ViewBase, BaseModel):
    typename: Literal["PixelView"] = Field(
        alias="__typename", default="PixelView", exclude=True
    )


class ViewRGBView(ViewBase, BaseModel):
    typename: Literal["RGBView"] = Field(
        alias="__typename", default="RGBView", exclude=True
    )


class ViewContinousScanView(ViewBase, BaseModel):
    typename: Literal["ContinousScanView"] = Field(
        alias="__typename", default="ContinousScanView", exclude=True
    )


class ViewWellPositionView(ViewBase, BaseModel):
    typename: Literal["WellPositionView"] = Field(
        alias="__typename", default="WellPositionView", exclude=True
    )


class ViewAcquisitionView(ViewBase, BaseModel):
    typename: Literal["AcquisitionView"] = Field(
        alias="__typename", default="AcquisitionView", exclude=True
    )


class Camera(BaseModel):
    typename: Literal["Camera"] = Field(
        alias="__typename", default="Camera", exclude=True
    )
    sensor_size_x: Optional[int] = Field(default=None, alias="sensorSizeX")
    sensor_size_y: Optional[int] = Field(default=None, alias="sensorSizeY")
    pixel_size_x: Optional[Micrometers] = Field(default=None, alias="pixelSizeX")
    pixel_size_y: Optional[Micrometers] = Field(default=None, alias="pixelSizeY")
    name: str
    serial_number: str = Field(alias="serialNumber")
    model_config = ConfigDict(frozen=True)


class RenderedPlotStore(HasPresignedDownloadAccessor, BaseModel):
    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    id: ID
    key: str
    model_config = ConfigDict(frozen=True)


class RenderedPlot(BaseModel):
    typename: Literal["RenderedPlot"] = Field(
        alias="__typename", default="RenderedPlot", exclude=True
    )
    id: ID
    store: RenderedPlotStore
    model_config = ConfigDict(frozen=True)


class ListRenderedPlotStore(HasPresignedDownloadAccessor, BaseModel):
    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    id: ID
    key: str
    model_config = ConfigDict(frozen=True)


class ListRenderedPlot(BaseModel):
    typename: Literal["RenderedPlot"] = Field(
        alias="__typename", default="RenderedPlot", exclude=True
    )
    id: ID
    store: ListRenderedPlotStore
    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


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
    model_config = ConfigDict(frozen=True)


class PresignedPostCredentials(BaseModel):
    """Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)"""

    typename: Literal["PresignedPostCredentials"] = Field(
        alias="__typename", default="PresignedPostCredentials", exclude=True
    )
    key: str
    x_amz_credential: str = Field(alias="xAmzCredential")
    x_amz_algorithm: str = Field(alias="xAmzAlgorithm")
    x_amz_date: str = Field(alias="xAmzDate")
    x_amz_signature: str = Field(alias="xAmzSignature")
    policy: str
    datalayer: str
    bucket: str
    store: str
    model_config = ConfigDict(frozen=True)


class TableRowTable(HasParquestStoreTrait, BaseModel):
    typename: Literal["Table"] = Field(
        alias="__typename", default="Table", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class TableRowColumns(BaseModel):
    """A column descriptor"""

    typename: Literal["TableColumn"] = Field(
        alias="__typename", default="TableColumn", exclude=True
    )
    name: str
    model_config = ConfigDict(frozen=True)


class TableRow(BaseModel):
    """A cell of a table"""

    typename: Literal["TableRow"] = Field(
        alias="__typename", default="TableRow", exclude=True
    )
    id: ID
    values: Tuple[Any, ...]
    table: TableRowTable
    columns: Tuple[TableRowColumns, ...]
    model_config = ConfigDict(frozen=True)


class Stage(BaseModel):
    typename: Literal["Stage"] = Field(
        alias="__typename", default="Stage", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class ROIImage(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class ROI(IsVectorizableTrait, BaseModel):
    typename: Literal["ROI"] = Field(alias="__typename", default="ROI", exclude=True)
    id: ID
    image: ROIImage
    vectors: Tuple[FiveDVector, ...]
    kind: RoiKind
    model_config = ConfigDict(frozen=True)


class Objective(BaseModel):
    typename: Literal["Objective"] = Field(
        alias="__typename", default="Objective", exclude=True
    )
    id: ID
    na: Optional[float] = Field(default=None)
    name: str
    serial_number: str = Field(alias="serialNumber")
    model_config = ConfigDict(frozen=True)


class HistoryStuffApp(BaseModel):
    """An app."""

    typename: Literal["App"] = Field(alias="__typename", default="App", exclude=True)
    id: ID
    model_config = ConfigDict(frozen=True)


class HistoryStuff(BaseModel):
    typename: Literal["History"] = Field(
        alias="__typename", default="History", exclude=True
    )
    id: ID
    app: Optional[HistoryStuffApp] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class Instrument(BaseModel):
    typename: Literal["Instrument"] = Field(
        alias="__typename", default="Instrument", exclude=True
    )
    id: ID
    model: Optional[str] = Field(default=None)
    name: str
    serial_number: str = Field(alias="serialNumber")
    model_config = ConfigDict(frozen=True)


class TableCellTable(HasParquestStoreTrait, BaseModel):
    typename: Literal["Table"] = Field(
        alias="__typename", default="Table", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class TableCellColumn(BaseModel):
    """A column descriptor"""

    typename: Literal["TableColumn"] = Field(
        alias="__typename", default="TableColumn", exclude=True
    )
    name: str
    model_config = ConfigDict(frozen=True)


class TableCell(BaseModel):
    """A cell of a table"""

    typename: Literal["TableCell"] = Field(
        alias="__typename", default="TableCell", exclude=True
    )
    id: ID
    table: TableCellTable
    value: Any
    column: TableCellColumn
    model_config = ConfigDict(frozen=True)


class Era(BaseModel):
    typename: Literal["Era"] = Field(alias="__typename", default="Era", exclude=True)
    id: ID
    begin: Optional[datetime] = Field(default=None)
    name: str
    model_config = ConfigDict(frozen=True)


class SnapshotStore(HasPresignedDownloadAccessor, BaseModel):
    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    key: str
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class Snapshot(BaseModel):
    typename: Literal["Snapshot"] = Field(
        alias="__typename", default="Snapshot", exclude=True
    )
    id: ID
    store: SnapshotStore
    name: str
    model_config = ConfigDict(frozen=True)


class ZarrStore(HasZarrStoreAccessor, BaseModel):
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
    model_config = ConfigDict(frozen=True)


class ParquetStore(HasParquetStoreAccesor, BaseModel):
    typename: Literal["ParquetStore"] = Field(
        alias="__typename", default="ParquetStore", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str
    model_config = ConfigDict(frozen=True)


class MeshStore(BaseModel):
    typename: Literal["MeshStore"] = Field(
        alias="__typename", default="MeshStore", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str
    model_config = ConfigDict(frozen=True)


class BigFileStore(HasDownloadAccessor, BaseModel):
    typename: Literal["BigFileStore"] = Field(
        alias="__typename", default="BigFileStore", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class Channel(BaseModel):
    typename: Literal["Channel"] = Field(
        alias="__typename", default="Channel", exclude=True
    )
    id: ID
    name: str
    excitation_wavelength: Optional[float] = Field(
        default=None, alias="excitationWavelength"
    )
    model_config = ConfigDict(frozen=True)


class DerivedViewOriginimage(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    name: str
    "The name of the image"
    model_config = ConfigDict(frozen=True)


class DerivedView(ViewDerivedView, BaseModel):
    typename: Literal["DerivedView"] = Field(
        alias="__typename", default="DerivedView", exclude=True
    )
    id: ID
    origin_image: DerivedViewOriginimage = Field(alias="originImage")
    model_config = ConfigDict(frozen=True)


class ROIViewRoi(IsVectorizableTrait, BaseModel):
    typename: Literal["ROI"] = Field(alias="__typename", default="ROI", exclude=True)
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class ROIView(ViewROIView, BaseModel):
    typename: Literal["ROIView"] = Field(
        alias="__typename", default="ROIView", exclude=True
    )
    id: ID
    roi: ROIViewRoi
    model_config = ConfigDict(frozen=True)


class FileViewFile(BaseModel):
    typename: Literal["File"] = Field(alias="__typename", default="File", exclude=True)
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class FileView(ViewFileView, BaseModel):
    typename: Literal["FileView"] = Field(
        alias="__typename", default="FileView", exclude=True
    )
    id: ID
    series_identifier: Optional[str] = Field(default=None, alias="seriesIdentifier")
    file: FileViewFile
    model_config = ConfigDict(frozen=True)


class AffineTransformationViewStage(BaseModel):
    typename: Literal["Stage"] = Field(
        alias="__typename", default="Stage", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class AffineTransformationView(ViewAffineTransformationView, BaseModel):
    typename: Literal["AffineTransformationView"] = Field(
        alias="__typename", default="AffineTransformationView", exclude=True
    )
    id: ID
    affine_matrix: FourByFourMatrix = Field(alias="affineMatrix")
    stage: AffineTransformationViewStage
    model_config = ConfigDict(frozen=True)


class OpticsViewObjective(BaseModel):
    typename: Literal["Objective"] = Field(
        alias="__typename", default="Objective", exclude=True
    )
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")
    model_config = ConfigDict(frozen=True)


class OpticsViewCamera(BaseModel):
    typename: Literal["Camera"] = Field(
        alias="__typename", default="Camera", exclude=True
    )
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")
    model_config = ConfigDict(frozen=True)


class OpticsViewInstrument(BaseModel):
    typename: Literal["Instrument"] = Field(
        alias="__typename", default="Instrument", exclude=True
    )
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")
    model_config = ConfigDict(frozen=True)


class OpticsView(ViewOpticsView, BaseModel):
    typename: Literal["OpticsView"] = Field(
        alias="__typename", default="OpticsView", exclude=True
    )
    id: ID
    objective: Optional[OpticsViewObjective] = Field(default=None)
    camera: Optional[OpticsViewCamera] = Field(default=None)
    instrument: Optional[OpticsViewInstrument] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class LabelView(ViewLabelView, BaseModel):
    typename: Literal["LabelView"] = Field(
        alias="__typename", default="LabelView", exclude=True
    )
    id: ID
    label: str
    model_config = ConfigDict(frozen=True)


class StructureView(ViewStructureView, BaseModel):
    typename: Literal["StructureView"] = Field(
        alias="__typename", default="StructureView", exclude=True
    )
    id: ID
    structure: str
    model_config = ConfigDict(frozen=True)


class AcquisitionViewOperator(BaseModel):
    """A user."""

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    sub: str
    model_config = ConfigDict(frozen=True)


class AcquisitionView(ViewAcquisitionView, BaseModel):
    typename: Literal["AcquisitionView"] = Field(
        alias="__typename", default="AcquisitionView", exclude=True
    )
    id: ID
    description: Optional[str] = Field(default=None)
    acquired_at: Optional[datetime] = Field(default=None, alias="acquiredAt")
    operator: Optional[AcquisitionViewOperator] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class WellPositionViewWell(BaseModel):
    typename: Literal["MultiWellPlate"] = Field(
        alias="__typename", default="MultiWellPlate", exclude=True
    )
    id: ID
    rows: Optional[int] = Field(default=None)
    columns: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class WellPositionView(ViewWellPositionView, BaseModel):
    typename: Literal["WellPositionView"] = Field(
        alias="__typename", default="WellPositionView", exclude=True
    )
    id: ID
    column: Optional[int] = Field(default=None)
    row: Optional[int] = Field(default=None)
    well: Optional[WellPositionViewWell] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class ContinousScanView(ViewContinousScanView, BaseModel):
    typename: Literal["ContinousScanView"] = Field(
        alias="__typename", default="ContinousScanView", exclude=True
    )
    id: ID
    direction: ScanDirection
    model_config = ConfigDict(frozen=True)


class PixelView(ViewPixelView, BaseModel):
    typename: Literal["PixelView"] = Field(
        alias="__typename", default="PixelView", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class Dataset(BaseModel):
    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    name: str
    description: Optional[str] = Field(default=None)
    history: Tuple[HistoryStuff, ...]
    model_config = ConfigDict(frozen=True)


class TimepointView(ViewTimepointView, BaseModel):
    typename: Literal["TimepointView"] = Field(
        alias="__typename", default="TimepointView", exclude=True
    )
    id: ID
    ms_since_start: Optional[Milliseconds] = Field(default=None, alias="msSinceStart")
    index_since_start: Optional[int] = Field(default=None, alias="indexSinceStart")
    era: Era
    model_config = ConfigDict(frozen=True)


class RGBViewContexts(BaseModel):
    typename: Literal["RGBContext"] = Field(
        alias="__typename", default="RGBContext", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class RGBViewImageDerivedscaleviewsImage(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    store: ZarrStore
    "The store where the image data is stored."
    model_config = ConfigDict(frozen=True)


class RGBViewImageDerivedscaleviews(BaseModel):
    typename: Literal["ScaleView"] = Field(
        alias="__typename", default="ScaleView", exclude=True
    )
    id: ID
    image: RGBViewImageDerivedscaleviewsImage
    scale_x: float = Field(alias="scaleX")
    scale_y: float = Field(alias="scaleY")
    scale_z: float = Field(alias="scaleZ")
    scale_t: float = Field(alias="scaleT")
    scale_c: float = Field(alias="scaleC")
    model_config = ConfigDict(frozen=True)


class RGBViewImage(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    store: ZarrStore
    "The store where the image data is stored."
    derived_scale_views: Tuple[RGBViewImageDerivedscaleviews, ...] = Field(
        alias="derivedScaleViews"
    )
    "Scale views derived from this image"
    model_config = ConfigDict(frozen=True)


class RGBView(ViewRGBView, BaseModel):
    typename: Literal["RGBView"] = Field(
        alias="__typename", default="RGBView", exclude=True
    )
    id: ID
    contexts: Tuple[RGBViewContexts, ...]
    name: str
    image: RGBViewImage
    color_map: ColorMap = Field(alias="colorMap")
    contrast_limit_min: Optional[float] = Field(default=None, alias="contrastLimitMin")
    contrast_limit_max: Optional[float] = Field(default=None, alias="contrastLimitMax")
    gamma: Optional[float] = Field(default=None)
    rescale: bool
    active: bool
    full_colour: str = Field(alias="fullColour")
    base_color: Optional[Tuple[int, ...]] = Field(default=None, alias="baseColor")
    model_config = ConfigDict(frozen=True)


class TableOrigins(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class Table(HasParquestStoreTrait, BaseModel):
    typename: Literal["Table"] = Field(
        alias="__typename", default="Table", exclude=True
    )
    origins: Tuple[TableOrigins, ...]
    id: ID
    name: str
    store: ParquetStore
    model_config = ConfigDict(frozen=True)


class Mesh(BaseModel):
    typename: Literal["Mesh"] = Field(alias="__typename", default="Mesh", exclude=True)
    id: ID
    name: str
    store: MeshStore
    model_config = ConfigDict(frozen=True)


class FileOrigins(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class File(BaseModel):
    typename: Literal["File"] = Field(alias="__typename", default="File", exclude=True)
    origins: Tuple[FileOrigins, ...]
    id: ID
    name: str
    store: BigFileStore
    model_config = ConfigDict(frozen=True)


class ChannelView(ViewChannelView, BaseModel):
    typename: Literal["ChannelView"] = Field(
        alias="__typename", default="ChannelView", exclude=True
    )
    id: ID
    channel: Channel
    model_config = ConfigDict(frozen=True)


class RGBContextImage(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    store: ZarrStore
    "The store where the image data is stored."
    model_config = ConfigDict(frozen=True)


class RGBContext(BaseModel):
    typename: Literal["RGBContext"] = Field(
        alias="__typename", default="RGBContext", exclude=True
    )
    id: ID
    views: Tuple[RGBView, ...]
    image: RGBContextImage
    pinned: bool
    name: str
    z: int
    t: int
    c: int
    blending: Blending
    model_config = ConfigDict(frozen=True)


class ImageViewsBase(BaseModel):
    pass
    model_config = ConfigDict(frozen=True)


class ImageViewsBaseFileView(FileView, ImageViewsBase, BaseModel):
    typename: Literal["FileView"] = Field(
        alias="__typename", default="FileView", exclude=True
    )


class ImageViewsBaseAffineTransformationView(
    AffineTransformationView, ImageViewsBase, BaseModel
):
    typename: Literal["AffineTransformationView"] = Field(
        alias="__typename", default="AffineTransformationView", exclude=True
    )


class ImageViewsBaseLabelView(LabelView, ImageViewsBase, BaseModel):
    typename: Literal["LabelView"] = Field(
        alias="__typename", default="LabelView", exclude=True
    )


class ImageViewsBaseChannelView(ChannelView, ImageViewsBase, BaseModel):
    typename: Literal["ChannelView"] = Field(
        alias="__typename", default="ChannelView", exclude=True
    )


class ImageViewsBaseTimepointView(TimepointView, ImageViewsBase, BaseModel):
    typename: Literal["TimepointView"] = Field(
        alias="__typename", default="TimepointView", exclude=True
    )


class ImageViewsBaseOpticsView(OpticsView, ImageViewsBase, BaseModel):
    typename: Literal["OpticsView"] = Field(
        alias="__typename", default="OpticsView", exclude=True
    )


class ImageViewsBaseStructureView(StructureView, ImageViewsBase, BaseModel):
    typename: Literal["StructureView"] = Field(
        alias="__typename", default="StructureView", exclude=True
    )


class ImageViewsBaseScaleView(ImageViewsBase, BaseModel):
    typename: Literal["ScaleView"] = Field(
        alias="__typename", default="ScaleView", exclude=True
    )


class ImageViewsBaseDerivedView(DerivedView, ImageViewsBase, BaseModel):
    typename: Literal["DerivedView"] = Field(
        alias="__typename", default="DerivedView", exclude=True
    )


class ImageViewsBaseROIView(ROIView, ImageViewsBase, BaseModel):
    typename: Literal["ROIView"] = Field(
        alias="__typename", default="ROIView", exclude=True
    )


class ImageViewsBasePixelView(ImageViewsBase, BaseModel):
    typename: Literal["PixelView"] = Field(
        alias="__typename", default="PixelView", exclude=True
    )


class ImageViewsBaseRGBView(RGBView, ImageViewsBase, BaseModel):
    typename: Literal["RGBView"] = Field(
        alias="__typename", default="RGBView", exclude=True
    )


class ImageViewsBaseContinousScanView(ContinousScanView, ImageViewsBase, BaseModel):
    typename: Literal["ContinousScanView"] = Field(
        alias="__typename", default="ContinousScanView", exclude=True
    )


class ImageViewsBaseWellPositionView(WellPositionView, ImageViewsBase, BaseModel):
    typename: Literal["WellPositionView"] = Field(
        alias="__typename", default="WellPositionView", exclude=True
    )


class ImageViewsBaseAcquisitionView(AcquisitionView, ImageViewsBase, BaseModel):
    typename: Literal["AcquisitionView"] = Field(
        alias="__typename", default="AcquisitionView", exclude=True
    )


class ImageRgbcontexts(BaseModel):
    typename: Literal["RGBContext"] = Field(
        alias="__typename", default="RGBContext", exclude=True
    )
    id: ID
    name: str
    views: Tuple[RGBView, ...]
    model_config = ConfigDict(frozen=True)


class Image(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    name: str
    "The name of the image"
    store: ZarrStore
    "The store where the image data is stored."
    views: Tuple[
        Annotated[
            Union[
                ImageViewsBaseFileView,
                ImageViewsBaseAffineTransformationView,
                ImageViewsBaseLabelView,
                ImageViewsBaseChannelView,
                ImageViewsBaseTimepointView,
                ImageViewsBaseOpticsView,
                ImageViewsBaseStructureView,
                ImageViewsBaseScaleView,
                ImageViewsBaseDerivedView,
                ImageViewsBaseROIView,
                ImageViewsBasePixelView,
                ImageViewsBaseRGBView,
                ImageViewsBaseContinousScanView,
                ImageViewsBaseWellPositionView,
                ImageViewsBaseAcquisitionView,
            ],
            Field(discriminator="typename"),
        ],
        ...,
    ]
    "All views of this image"
    pixel_views: Tuple[PixelView, ...] = Field(alias="pixelViews")
    "Pixel views describing pixel value semantics"
    rgb_contexts: Tuple[ImageRgbcontexts, ...] = Field(alias="rgbContexts")
    "RGB rendering contexts"
    model_config = ConfigDict(frozen=True)


class CreateCameraMutationCreatecamera(BaseModel):
    typename: Literal["Camera"] = Field(
        alias="__typename", default="Camera", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class CreateCameraMutation(BaseModel):
    create_camera: CreateCameraMutationCreatecamera = Field(alias="createCamera")
    "Create a new camera configuration"

    class Arguments(BaseModel):
        input: CameraInput

    class Meta:
        document = "mutation CreateCamera($input: CameraInput!) {\n  createCamera(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class EnsureCameraMutationEnsurecamera(BaseModel):
    typename: Literal["Camera"] = Field(
        alias="__typename", default="Camera", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class EnsureCameraMutation(BaseModel):
    ensure_camera: EnsureCameraMutationEnsurecamera = Field(alias="ensureCamera")
    "Ensure a camera exists, creating if needed"

    class Arguments(BaseModel):
        input: CameraInput

    class Meta:
        document = "mutation EnsureCamera($input: CameraInput!) {\n  ensureCamera(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class CreateRenderTreeMutationCreaterendertree(BaseModel):
    typename: Literal["RenderTree"] = Field(
        alias="__typename", default="RenderTree", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class CreateRenderTreeMutation(BaseModel):
    create_render_tree: CreateRenderTreeMutationCreaterendertree = Field(
        alias="createRenderTree"
    )
    "Create a new render tree for image visualization"

    class Arguments(BaseModel):
        input: RenderTreeInput

    class Meta:
        document = "mutation CreateRenderTree($input: RenderTreeInput!) {\n  createRenderTree(input: $input) {\n    id\n    __typename\n  }\n}"


class From_parquet_likeMutation(BaseModel):
    from_parquet_like: Table = Field(alias="fromParquetLike")
    "Create a table from parquet-like data"

    class Arguments(BaseModel):
        input: FromParquetLike

    class Meta:
        document = "fragment ParquetStore on ParquetStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Table on Table {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...ParquetStore\n    __typename\n  }\n  __typename\n}\n\nmutation from_parquet_like($input: FromParquetLike!) {\n  fromParquetLike(input: $input) {\n    ...Table\n    __typename\n  }\n}"


class RequestTableUploadMutation(BaseModel):
    request_table_upload: Credentials = Field(alias="requestTableUpload")
    "Request credentials to upload a new table"

    class Arguments(BaseModel):
        input: RequestTableUploadInput

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n  __typename\n}\n\nmutation RequestTableUpload($input: RequestTableUploadInput!) {\n  requestTableUpload(input: $input) {\n    ...Credentials\n    __typename\n  }\n}"


class RequestTableAccessMutation(BaseModel):
    request_table_access: AccessCredentials = Field(alias="requestTableAccess")
    "Request credentials to access a table"

    class Arguments(BaseModel):
        input: RequestTableAccessInput

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n  __typename\n}\n\nmutation RequestTableAccess($input: RequestTableAccessInput!) {\n  requestTableAccess(input: $input) {\n    ...AccessCredentials\n    __typename\n  }\n}"


class CreateRenderedPlotMutation(BaseModel):
    create_rendered_plot: RenderedPlot = Field(alias="createRenderedPlot")
    "Create a new rendered plot"

    class Arguments(BaseModel):
        input: RenderedPlotInput

    class Meta:
        document = "fragment RenderedPlot on RenderedPlot {\n  id\n  store {\n    id\n    key\n    __typename\n  }\n  __typename\n}\n\nmutation CreateRenderedPlot($input: RenderedPlotInput!) {\n  createRenderedPlot(input: $input) {\n    ...RenderedPlot\n    __typename\n  }\n}"


class From_file_likeMutation(BaseModel):
    from_file_like: File = Field(alias="fromFileLike")
    "Create a file from file-like data"

    class Arguments(BaseModel):
        input: FromFileLike

    class Meta:
        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nmutation from_file_like($input: FromFileLike!) {\n  fromFileLike(input: $input) {\n    ...File\n    __typename\n  }\n}"


class RequestFileUploadMutation(BaseModel):
    request_file_upload: Credentials = Field(alias="requestFileUpload")
    "Request credentials to upload a new file"

    class Arguments(BaseModel):
        input: RequestFileUploadInput

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n  __typename\n}\n\nmutation RequestFileUpload($input: RequestFileUploadInput!) {\n  requestFileUpload(input: $input) {\n    ...Credentials\n    __typename\n  }\n}"


class RequestFileAccessMutation(BaseModel):
    request_file_access: AccessCredentials = Field(alias="requestFileAccess")
    "Request credentials to access a file"

    class Arguments(BaseModel):
        input: RequestFileAccessInput

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n  __typename\n}\n\nmutation RequestFileAccess($input: RequestFileAccessInput!) {\n  requestFileAccess(input: $input) {\n    ...AccessCredentials\n    __typename\n  }\n}"


class CreateStageMutation(BaseModel):
    create_stage: Stage = Field(alias="createStage")
    "Create a new stage for organizing data"

    class Arguments(BaseModel):
        input: StageInput

    class Meta:
        document = "fragment Stage on Stage {\n  id\n  name\n  __typename\n}\n\nmutation CreateStage($input: StageInput!) {\n  createStage(input: $input) {\n    ...Stage\n    __typename\n  }\n}"


class CreateRoiMutation(BaseModel):
    create_roi: ROI = Field(alias="createRoi")
    "Create a new region of interest"

    class Arguments(BaseModel):
        input: RoiInput

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nmutation CreateRoi($input: RoiInput!) {\n  createRoi(input: $input) {\n    ...ROI\n    __typename\n  }\n}"


class DeleteRoiMutation(BaseModel):
    delete_roi: ID = Field(alias="deleteRoi")
    "Delete an existing region of interest"

    class Arguments(BaseModel):
        input: DeleteRoiInput

    class Meta:
        document = "mutation DeleteRoi($input: DeleteRoiInput!) {\n  deleteRoi(input: $input)\n}"


class UpdateRoiMutation(BaseModel):
    update_roi: ROI = Field(alias="updateRoi")
    "Update an existing region of interest"

    class Arguments(BaseModel):
        input: UpdateRoiInput

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nmutation UpdateRoi($input: UpdateRoiInput!) {\n  updateRoi(input: $input) {\n    ...ROI\n    __typename\n  }\n}"


class CreateObjectiveMutationCreateobjective(BaseModel):
    typename: Literal["Objective"] = Field(
        alias="__typename", default="Objective", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class CreateObjectiveMutation(BaseModel):
    create_objective: CreateObjectiveMutationCreateobjective = Field(
        alias="createObjective"
    )
    "Create a new microscope objective configuration"

    class Arguments(BaseModel):
        input: ObjectiveInput

    class Meta:
        document = "mutation CreateObjective($input: ObjectiveInput!) {\n  createObjective(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class EnsureObjectiveMutationEnsureobjective(BaseModel):
    typename: Literal["Objective"] = Field(
        alias="__typename", default="Objective", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class EnsureObjectiveMutation(BaseModel):
    ensure_objective: EnsureObjectiveMutationEnsureobjective = Field(
        alias="ensureObjective"
    )
    "Ensure an objective exists, creating if needed"

    class Arguments(BaseModel):
        input: ObjectiveInput

    class Meta:
        document = "mutation EnsureObjective($input: ObjectiveInput!) {\n  ensureObjective(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class CreateDatasetMutationCreatedataset(BaseModel):
    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class CreateDatasetMutation(BaseModel):
    create_dataset: CreateDatasetMutationCreatedataset = Field(alias="createDataset")
    "Create a new dataset to organize data"

    class Arguments(BaseModel):
        input: CreateDatasetInput

    class Meta:
        document = "mutation CreateDataset($input: CreateDatasetInput!) {\n  createDataset(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class UpdateDatasetMutationUpdatedataset(BaseModel):
    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class UpdateDatasetMutation(BaseModel):
    update_dataset: UpdateDatasetMutationUpdatedataset = Field(alias="updateDataset")
    "Update dataset metadata"

    class Arguments(BaseModel):
        input: ChangeDatasetInput

    class Meta:
        document = "mutation UpdateDataset($input: ChangeDatasetInput!) {\n  updateDataset(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class RevertDatasetMutationRevertdataset(BaseModel):
    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    id: ID
    name: str
    description: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class RevertDatasetMutation(BaseModel):
    revert_dataset: RevertDatasetMutationRevertdataset = Field(alias="revertDataset")
    "Revert dataset to a previous version"

    class Arguments(BaseModel):
        input: RevertInput

    class Meta:
        document = "mutation RevertDataset($input: RevertInput!) {\n  revertDataset(input: $input) {\n    id\n    name\n    description\n    __typename\n  }\n}"


class CreateInstrumentMutationCreateinstrument(BaseModel):
    typename: Literal["Instrument"] = Field(
        alias="__typename", default="Instrument", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class CreateInstrumentMutation(BaseModel):
    create_instrument: CreateInstrumentMutationCreateinstrument = Field(
        alias="createInstrument"
    )
    "Create a new instrument configuration"

    class Arguments(BaseModel):
        input: InstrumentInput

    class Meta:
        document = "mutation CreateInstrument($input: InstrumentInput!) {\n  createInstrument(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class EnsureInstrumentMutationEnsureinstrument(BaseModel):
    typename: Literal["Instrument"] = Field(
        alias="__typename", default="Instrument", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class EnsureInstrumentMutation(BaseModel):
    ensure_instrument: EnsureInstrumentMutationEnsureinstrument = Field(
        alias="ensureInstrument"
    )
    "Ensure an instrument exists, creating if needed"

    class Arguments(BaseModel):
        input: InstrumentInput

    class Meta:
        document = "mutation EnsureInstrument($input: InstrumentInput!) {\n  ensureInstrument(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class From_array_likeMutation(BaseModel):
    from_array_like: Image = Field(alias="fromArrayLike")
    "Create an image from array-like data"

    class Arguments(BaseModel):
        input: FromArrayLikeInput

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n  __typename\n}\n\nfragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n  __typename\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n    __typename\n  }\n  __typename\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n    __typename\n  }\n  __typename\n}\n\nfragment DerivedView on DerivedView {\n  ...View\n  id\n  originImage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  id\n  objective {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  camera {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  instrument {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  __typename\n}\n\nfragment PixelView on PixelView {\n  ...View\n  id\n  __typename\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  contexts {\n    id\n    name\n    __typename\n  }\n  name\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    derivedScaleViews {\n      id\n      image {\n        id\n        store {\n          ...ZarrStore\n          __typename\n        }\n        __typename\n      }\n      scaleX\n      scaleY\n      scaleZ\n      scaleT\n      scaleC\n      __typename\n    }\n    __typename\n  }\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  fullColour\n  baseColor\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment WellPositionView on WellPositionView {\n  ...View\n  id\n  column\n  row\n  well {\n    id\n    rows\n    columns\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  label\n  __typename\n}\n\nfragment ContinousScanView on ContinousScanView {\n  ...View\n  id\n  direction\n  __typename\n}\n\nfragment AcquisitionView on AcquisitionView {\n  ...View\n  id\n  description\n  acquiredAt\n  operator {\n    sub\n    __typename\n  }\n  __typename\n}\n\nfragment FileView on FileView {\n  ...View\n  id\n  seriesIdentifier\n  file {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureView on StructureView {\n  ...View\n  id\n  structure\n  __typename\n}\n\nfragment ROIView on ROIView {\n  ...View\n  id\n  roi {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment Image on Image {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...AcquisitionView\n    ...RGBView\n    ...WellPositionView\n    ...StructureView\n    ...DerivedView\n    ...ROIView\n    ...FileView\n    ...ContinousScanView\n    __typename\n  }\n  pixelViews {\n    ...PixelView\n    __typename\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nmutation from_array_like($input: FromArrayLikeInput!) {\n  fromArrayLike(input: $input) {\n    ...Image\n    __typename\n  }\n}"


class RequestUploadMutation(BaseModel):
    request_upload: Credentials = Field(alias="requestUpload")
    "Request credentials to upload a new image"

    class Arguments(BaseModel):
        input: RequestUploadInput

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n  __typename\n}\n\nmutation RequestUpload($input: RequestUploadInput!) {\n  requestUpload(input: $input) {\n    ...Credentials\n    __typename\n  }\n}"


class RequestAccessMutation(BaseModel):
    request_access: AccessCredentials = Field(alias="requestAccess")
    "Request credentials to access an image"

    class Arguments(BaseModel):
        input: RequestAccessInput

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n  __typename\n}\n\nmutation RequestAccess($input: RequestAccessInput!) {\n  requestAccess(input: $input) {\n    ...AccessCredentials\n    __typename\n  }\n}"


class CreateEraMutationCreateera(BaseModel):
    typename: Literal["Era"] = Field(alias="__typename", default="Era", exclude=True)
    id: ID
    begin: Optional[datetime] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class CreateEraMutation(BaseModel):
    create_era: CreateEraMutationCreateera = Field(alias="createEra")
    "Create a new era for temporal organization"

    class Arguments(BaseModel):
        input: EraInput

    class Meta:
        document = "mutation CreateEra($input: EraInput!) {\n  createEra(input: $input) {\n    id\n    begin\n    __typename\n  }\n}"


class CreateSnapshotMutation(BaseModel):
    create_snapshot: Snapshot = Field(alias="createSnapshot")
    "Create a new state snapshot"

    class Arguments(BaseModel):
        input: SnapshotInput

    class Meta:
        document = "fragment Snapshot on Snapshot {\n  id\n  store {\n    key\n    presignedUrl\n    __typename\n  }\n  name\n  __typename\n}\n\nmutation CreateSnapshot($input: SnapshotInput!) {\n  createSnapshot(input: $input) {\n    ...Snapshot\n    __typename\n  }\n}"


class CreateRgbViewMutationCreatergbview(BaseModel):
    typename: Literal["RGBView"] = Field(
        alias="__typename", default="RGBView", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class CreateRgbViewMutation(BaseModel):
    create_rgb_view: CreateRgbViewMutationCreatergbview = Field(alias="createRgbView")
    "Create a new view for RGB image data"

    class Arguments(BaseModel):
        input: RGBViewInput

    class Meta:
        document = "mutation CreateRgbView($input: RGBViewInput!) {\n  createRgbView(input: $input) {\n    id\n    __typename\n  }\n}"


class CreateLabelViewMutation(BaseModel):
    create_label_view: LabelView = Field(alias="createLabelView")
    "Create a new view for label data"

    class Arguments(BaseModel):
        input: LabelViewInput

    class Meta:
        document = "fragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  label\n  __typename\n}\n\nmutation CreateLabelView($input: LabelViewInput!) {\n  createLabelView(input: $input) {\n    ...LabelView\n    __typename\n  }\n}"


class CreateRGBContextMutation(BaseModel):
    create_rgb_context: RGBContext = Field(alias="createRgbContext")
    "Create a new RGB context for image visualization"

    class Arguments(BaseModel):
        input: CreateRGBContextInput

    class Meta:
        document = "fragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  contexts {\n    id\n    name\n    __typename\n  }\n  name\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    derivedScaleViews {\n      id\n      image {\n        id\n        store {\n          ...ZarrStore\n          __typename\n        }\n        __typename\n      }\n      scaleX\n      scaleY\n      scaleZ\n      scaleT\n      scaleC\n      __typename\n    }\n    __typename\n  }\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  fullColour\n  baseColor\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n    __typename\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n  __typename\n}\n\nmutation CreateRGBContext($input: CreateRGBContextInput!) {\n  createRgbContext(input: $input) {\n    ...RGBContext\n    __typename\n  }\n}"


class UpdateRGBContextMutation(BaseModel):
    update_rgb_context: RGBContext = Field(alias="updateRgbContext")
    "Update settings of an existing RGB context"

    class Arguments(BaseModel):
        input: UpdateRGBContextInput

    class Meta:
        document = "fragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  contexts {\n    id\n    name\n    __typename\n  }\n  name\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    derivedScaleViews {\n      id\n      image {\n        id\n        store {\n          ...ZarrStore\n          __typename\n        }\n        __typename\n      }\n      scaleX\n      scaleY\n      scaleZ\n      scaleT\n      scaleC\n      __typename\n    }\n    __typename\n  }\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  fullColour\n  baseColor\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n    __typename\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n  __typename\n}\n\nmutation UpdateRGBContext($input: UpdateRGBContextInput!) {\n  updateRgbContext(input: $input) {\n    ...RGBContext\n    __typename\n  }\n}"


class CreateViewCollectionMutationCreateviewcollection(BaseModel):
    typename: Literal["ViewCollection"] = Field(
        alias="__typename", default="ViewCollection", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class CreateViewCollectionMutation(BaseModel):
    create_view_collection: CreateViewCollectionMutationCreateviewcollection = Field(
        alias="createViewCollection"
    )
    "Create a new collection of views to organize related views"

    class Arguments(BaseModel):
        input: ViewCollectionInput

    class Meta:
        document = "mutation CreateViewCollection($input: ViewCollectionInput!) {\n  createViewCollection(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class CreateChannelMutationCreatechannel(BaseModel):
    typename: Literal["Channel"] = Field(
        alias="__typename", default="Channel", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class CreateChannelMutation(BaseModel):
    create_channel: CreateChannelMutationCreatechannel = Field(alias="createChannel")
    "Create a new channel"

    class Arguments(BaseModel):
        input: ChannelInput

    class Meta:
        document = "mutation CreateChannel($input: ChannelInput!) {\n  createChannel(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class EnsureChannelMutationEnsurechannel(BaseModel):
    typename: Literal["Channel"] = Field(
        alias="__typename", default="Channel", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class EnsureChannelMutation(BaseModel):
    ensure_channel: EnsureChannelMutationEnsurechannel = Field(alias="ensureChannel")
    "Ensure a channel exists, creating if needed"

    class Arguments(BaseModel):
        input: ChannelInput

    class Meta:
        document = "mutation EnsureChannel($input: ChannelInput!) {\n  ensureChannel(input: $input) {\n    id\n    name\n    __typename\n  }\n}"


class CreateMeshMutation(BaseModel):
    create_mesh: Mesh = Field(alias="createMesh")
    "Create a new mesh"

    class Arguments(BaseModel):
        input: MeshInput

    class Meta:
        document = "fragment MeshStore on MeshStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Mesh on Mesh {\n  id\n  name\n  store {\n    ...MeshStore\n    __typename\n  }\n  __typename\n}\n\nmutation CreateMesh($input: MeshInput!) {\n  createMesh(input: $input) {\n    ...Mesh\n    __typename\n  }\n}"


class RequestMeshUploadMutation(BaseModel):
    request_mesh_upload: PresignedPostCredentials = Field(alias="requestMeshUpload")
    "Request presigned credentials for mesh upload"

    class Arguments(BaseModel):
        input: RequestMeshUploadInput

    class Meta:
        document = "fragment PresignedPostCredentials on PresignedPostCredentials {\n  key\n  xAmzCredential\n  xAmzAlgorithm\n  xAmzDate\n  xAmzSignature\n  policy\n  datalayer\n  bucket\n  store\n  __typename\n}\n\nmutation RequestMeshUpload($input: RequestMeshUploadInput!) {\n  requestMeshUpload(input: $input) {\n    ...PresignedPostCredentials\n    __typename\n  }\n}"


class GetCameraQuery(BaseModel):
    camera: Camera

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Camera on Camera {\n  sensorSizeX\n  sensorSizeY\n  pixelSizeX\n  pixelSizeY\n  name\n  serialNumber\n  __typename\n}\n\nquery GetCamera($id: ID!) {\n  camera(id: $id) {\n    ...Camera\n    __typename\n  }\n}"


class GetTableQuery(BaseModel):
    table: Table

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ParquetStore on ParquetStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Table on Table {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...ParquetStore\n    __typename\n  }\n  __typename\n}\n\nquery GetTable($id: ID!) {\n  table(id: $id) {\n    ...Table\n    __typename\n  }\n}"


class SearchTablesQueryOptions(HasParquestStoreTrait, BaseModel):
    typename: Literal["Table"] = Field(
        alias="__typename", default="Table", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchTablesQuery(BaseModel):
    options: Tuple[SearchTablesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchTables($search: String, $values: [ID!]) {\n  options: tables(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetRenderedPlotQuery(BaseModel):
    rendered_plot: RenderedPlot = Field(alias="renderedPlot")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment RenderedPlot on RenderedPlot {\n  id\n  store {\n    id\n    key\n    __typename\n  }\n  __typename\n}\n\nquery GetRenderedPlot($id: ID!) {\n  renderedPlot(id: $id) {\n    ...RenderedPlot\n    __typename\n  }\n}"


class ListRenderedPlotsQuery(BaseModel):
    rendered_plots: Tuple[ListRenderedPlot, ...] = Field(alias="renderedPlots")

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListRenderedPlot on RenderedPlot {\n  id\n  store {\n    id\n    key\n    __typename\n  }\n  __typename\n}\n\nquery ListRenderedPlots {\n  renderedPlots {\n    ...ListRenderedPlot\n    __typename\n  }\n}"


class SearchRenderedPlotsQueryOptions(BaseModel):
    typename: Literal["RenderedPlot"] = Field(
        alias="__typename", default="RenderedPlot", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchRenderedPlotsQuery(BaseModel):
    options: Tuple[SearchRenderedPlotsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchRenderedPlots($search: String, $values: [ID!]) {\n  options: renderedPlots(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetFileQuery(BaseModel):
    file: File

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nquery GetFile($id: ID!) {\n  file(id: $id) {\n    ...File\n    __typename\n  }\n}"


class SearchFilesQueryOptions(BaseModel):
    typename: Literal["File"] = Field(alias="__typename", default="File", exclude=True)
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchFilesQuery(BaseModel):
    options: Tuple[SearchFilesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "query SearchFiles($search: String, $values: [ID!], $pagination: OffsetPaginationInput) {\n  options: files(\n    filters: {search: $search, ids: $values}\n    pagination: $pagination\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetTableRowQuery(BaseModel):
    table_row: TableRow = Field(alias="tableRow")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment TableRow on TableRow {\n  id\n  values\n  table {\n    id\n    __typename\n  }\n  columns {\n    name\n    __typename\n  }\n  __typename\n}\n\nquery GetTableRow($id: ID!) {\n  tableRow(id: $id) {\n    ...TableRow\n    __typename\n  }\n}"


class SearchTableRowsQueryOptions(BaseModel):
    """A cell of a table"""

    typename: Literal["TableRow"] = Field(
        alias="__typename", default="TableRow", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchTableRowsQuery(BaseModel):
    options: Tuple[SearchTableRowsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchTableRows($search: String, $values: [ID!]) {\n  options: tableRows(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetStageQuery(BaseModel):
    stage: Stage

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Stage on Stage {\n  id\n  name\n  __typename\n}\n\nquery GetStage($id: ID!) {\n  stage(id: $id) {\n    ...Stage\n    __typename\n  }\n}"


class SearchStagesQueryOptions(BaseModel):
    typename: Literal["Stage"] = Field(
        alias="__typename", default="Stage", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchStagesQuery(BaseModel):
    options: Tuple[SearchStagesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "query SearchStages($search: String, $values: [ID!], $pagination: OffsetPaginationInput) {\n  options: stages(\n    filters: {search: $search, ids: $values}\n    pagination: $pagination\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetRoisQuery(BaseModel):
    rois: Tuple[ROI, ...]

    class Arguments(BaseModel):
        image: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nquery GetRois($image: ID!) {\n  rois(filters: {image: $image}) {\n    ...ROI\n    __typename\n  }\n}"


class GetRoiQuery(BaseModel):
    roi: ROI

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nquery GetRoi($id: ID!) {\n  roi(id: $id) {\n    ...ROI\n    __typename\n  }\n}"


class SearchRoisQueryOptions(IsVectorizableTrait, BaseModel):
    typename: Literal["ROI"] = Field(alias="__typename", default="ROI", exclude=True)
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchRoisQuery(BaseModel):
    options: Tuple[SearchRoisQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchRois($search: String, $values: [ID!]) {\n  options: rois(filters: {search: $search, ids: $values}, pagination: {limit: 10}) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetObjectiveQuery(BaseModel):
    objective: Objective

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Objective on Objective {\n  id\n  na\n  name\n  serialNumber\n  __typename\n}\n\nquery GetObjective($id: ID!) {\n  objective(id: $id) {\n    ...Objective\n    __typename\n  }\n}"


class GetDatasetQuery(BaseModel):
    dataset: Dataset

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment HistoryStuff on History {\n  id\n  app {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment Dataset on Dataset {\n  name\n  description\n  history {\n    ...HistoryStuff\n    __typename\n  }\n  __typename\n}\n\nquery GetDataset($id: ID!) {\n  dataset(id: $id) {\n    ...Dataset\n    __typename\n  }\n}"


class GetInstrumentQuery(BaseModel):
    instrument: Instrument

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Instrument on Instrument {\n  id\n  model\n  name\n  serialNumber\n  __typename\n}\n\nquery GetInstrument($id: ID!) {\n  instrument(id: $id) {\n    ...Instrument\n    __typename\n  }\n}"


class GetTableCellQuery(BaseModel):
    table_cell: TableCell = Field(alias="tableCell")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment TableCell on TableCell {\n  id\n  table {\n    id\n    __typename\n  }\n  value\n  column {\n    name\n    __typename\n  }\n  __typename\n}\n\nquery GetTableCell($id: ID!) {\n  tableCell(id: $id) {\n    ...TableCell\n    __typename\n  }\n}"


class SearchTableCellsQueryOptions(BaseModel):
    """A cell of a table"""

    typename: Literal["TableCell"] = Field(
        alias="__typename", default="TableCell", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchTableCellsQuery(BaseModel):
    options: Tuple[SearchTableCellsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchTableCells($search: String, $values: [ID!]) {\n  options: tableCells(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetImageQuery(BaseModel):
    image: Image
    "Returns a single image by ID"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n  __typename\n}\n\nfragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n  __typename\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n    __typename\n  }\n  __typename\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n    __typename\n  }\n  __typename\n}\n\nfragment DerivedView on DerivedView {\n  ...View\n  id\n  originImage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  id\n  objective {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  camera {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  instrument {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  __typename\n}\n\nfragment PixelView on PixelView {\n  ...View\n  id\n  __typename\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  contexts {\n    id\n    name\n    __typename\n  }\n  name\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    derivedScaleViews {\n      id\n      image {\n        id\n        store {\n          ...ZarrStore\n          __typename\n        }\n        __typename\n      }\n      scaleX\n      scaleY\n      scaleZ\n      scaleT\n      scaleC\n      __typename\n    }\n    __typename\n  }\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  fullColour\n  baseColor\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment WellPositionView on WellPositionView {\n  ...View\n  id\n  column\n  row\n  well {\n    id\n    rows\n    columns\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  label\n  __typename\n}\n\nfragment ContinousScanView on ContinousScanView {\n  ...View\n  id\n  direction\n  __typename\n}\n\nfragment AcquisitionView on AcquisitionView {\n  ...View\n  id\n  description\n  acquiredAt\n  operator {\n    sub\n    __typename\n  }\n  __typename\n}\n\nfragment FileView on FileView {\n  ...View\n  id\n  seriesIdentifier\n  file {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureView on StructureView {\n  ...View\n  id\n  structure\n  __typename\n}\n\nfragment ROIView on ROIView {\n  ...View\n  id\n  roi {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment Image on Image {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...AcquisitionView\n    ...RGBView\n    ...WellPositionView\n    ...StructureView\n    ...DerivedView\n    ...ROIView\n    ...FileView\n    ...ContinousScanView\n    __typename\n  }\n  pixelViews {\n    ...PixelView\n    __typename\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetImage($id: ID!) {\n  image(id: $id) {\n    ...Image\n    __typename\n  }\n}"


class GetRandomImageQuery(BaseModel):
    random_image: Image = Field(alias="randomImage")

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n  __typename\n}\n\nfragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n  __typename\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n    __typename\n  }\n  __typename\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n    __typename\n  }\n  __typename\n}\n\nfragment DerivedView on DerivedView {\n  ...View\n  id\n  originImage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  id\n  objective {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  camera {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  instrument {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  __typename\n}\n\nfragment PixelView on PixelView {\n  ...View\n  id\n  __typename\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  contexts {\n    id\n    name\n    __typename\n  }\n  name\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    derivedScaleViews {\n      id\n      image {\n        id\n        store {\n          ...ZarrStore\n          __typename\n        }\n        __typename\n      }\n      scaleX\n      scaleY\n      scaleZ\n      scaleT\n      scaleC\n      __typename\n    }\n    __typename\n  }\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  fullColour\n  baseColor\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment WellPositionView on WellPositionView {\n  ...View\n  id\n  column\n  row\n  well {\n    id\n    rows\n    columns\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  label\n  __typename\n}\n\nfragment ContinousScanView on ContinousScanView {\n  ...View\n  id\n  direction\n  __typename\n}\n\nfragment AcquisitionView on AcquisitionView {\n  ...View\n  id\n  description\n  acquiredAt\n  operator {\n    sub\n    __typename\n  }\n  __typename\n}\n\nfragment FileView on FileView {\n  ...View\n  id\n  seriesIdentifier\n  file {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureView on StructureView {\n  ...View\n  id\n  structure\n  __typename\n}\n\nfragment ROIView on ROIView {\n  ...View\n  id\n  roi {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment Image on Image {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...AcquisitionView\n    ...RGBView\n    ...WellPositionView\n    ...StructureView\n    ...DerivedView\n    ...ROIView\n    ...FileView\n    ...ContinousScanView\n    __typename\n  }\n  pixelViews {\n    ...PixelView\n    __typename\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery GetRandomImage {\n  randomImage {\n    ...Image\n    __typename\n  }\n}"


class SearchImagesQueryOptions(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    value: ID
    label: str
    "The name of the image"
    model_config = ConfigDict(frozen=True)


class SearchImagesQuery(BaseModel):
    options: Tuple[SearchImagesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchImages($search: String, $values: [ID!]) {\n  options: images(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ImagesQuery(BaseModel):
    images: Tuple[Image, ...]

    class Arguments(BaseModel):
        filter: Optional[ImageFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n  __typename\n}\n\nfragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n  __typename\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n    __typename\n  }\n  __typename\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n    __typename\n  }\n  __typename\n}\n\nfragment DerivedView on DerivedView {\n  ...View\n  id\n  originImage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  id\n  objective {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  camera {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  instrument {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  __typename\n}\n\nfragment PixelView on PixelView {\n  ...View\n  id\n  __typename\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  contexts {\n    id\n    name\n    __typename\n  }\n  name\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    derivedScaleViews {\n      id\n      image {\n        id\n        store {\n          ...ZarrStore\n          __typename\n        }\n        __typename\n      }\n      scaleX\n      scaleY\n      scaleZ\n      scaleT\n      scaleC\n      __typename\n    }\n    __typename\n  }\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  fullColour\n  baseColor\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment WellPositionView on WellPositionView {\n  ...View\n  id\n  column\n  row\n  well {\n    id\n    rows\n    columns\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  label\n  __typename\n}\n\nfragment ContinousScanView on ContinousScanView {\n  ...View\n  id\n  direction\n  __typename\n}\n\nfragment AcquisitionView on AcquisitionView {\n  ...View\n  id\n  description\n  acquiredAt\n  operator {\n    sub\n    __typename\n  }\n  __typename\n}\n\nfragment FileView on FileView {\n  ...View\n  id\n  seriesIdentifier\n  file {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureView on StructureView {\n  ...View\n  id\n  structure\n  __typename\n}\n\nfragment ROIView on ROIView {\n  ...View\n  id\n  roi {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment Image on Image {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...AcquisitionView\n    ...RGBView\n    ...WellPositionView\n    ...StructureView\n    ...DerivedView\n    ...ROIView\n    ...FileView\n    ...ContinousScanView\n    __typename\n  }\n  pixelViews {\n    ...PixelView\n    __typename\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery Images($filter: ImageFilter, $pagination: OffsetPaginationInput) {\n  images(filters: $filter, pagination: $pagination) {\n    ...Image\n    __typename\n  }\n}"


class ViewImageQueryImageStore(HasZarrStoreAccessor, BaseModel):
    typename: Literal["ZarrStore"] = Field(
        alias="__typename", default="ZarrStore", exclude=True
    )
    id: ID
    key: str
    "The key where the data is stored."
    bucket: str
    "The bucket where the data is stored."
    model_config = ConfigDict(frozen=True)


class ViewImageQueryImageViewsBase(BaseModel):
    pass
    model_config = ConfigDict(frozen=True)


class ViewImageQueryImageViewsBaseFileView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["FileView"] = Field(
        alias="__typename", default="FileView", exclude=True
    )


class ViewImageQueryImageViewsBaseAffineTransformationView(
    ViewImageQueryImageViewsBase, BaseModel
):
    typename: Literal["AffineTransformationView"] = Field(
        alias="__typename", default="AffineTransformationView", exclude=True
    )


class ViewImageQueryImageViewsBaseLabelView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["LabelView"] = Field(
        alias="__typename", default="LabelView", exclude=True
    )


class ViewImageQueryImageViewsBaseChannelView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["ChannelView"] = Field(
        alias="__typename", default="ChannelView", exclude=True
    )


class ViewImageQueryImageViewsBaseTimepointView(
    ViewImageQueryImageViewsBase, BaseModel
):
    typename: Literal["TimepointView"] = Field(
        alias="__typename", default="TimepointView", exclude=True
    )


class ViewImageQueryImageViewsBaseOpticsView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["OpticsView"] = Field(
        alias="__typename", default="OpticsView", exclude=True
    )


class ViewImageQueryImageViewsBaseStructureView(
    ViewImageQueryImageViewsBase, BaseModel
):
    typename: Literal["StructureView"] = Field(
        alias="__typename", default="StructureView", exclude=True
    )


class ViewImageQueryImageViewsBaseScaleView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["ScaleView"] = Field(
        alias="__typename", default="ScaleView", exclude=True
    )


class ViewImageQueryImageViewsBaseDerivedView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["DerivedView"] = Field(
        alias="__typename", default="DerivedView", exclude=True
    )


class ViewImageQueryImageViewsBaseROIView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["ROIView"] = Field(
        alias="__typename", default="ROIView", exclude=True
    )


class ViewImageQueryImageViewsBasePixelView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["PixelView"] = Field(
        alias="__typename", default="PixelView", exclude=True
    )


class ViewImageQueryImageViewsBaseRGBView(ViewImageQueryImageViewsBase, BaseModel):
    typename: Literal["RGBView"] = Field(
        alias="__typename", default="RGBView", exclude=True
    )


class ViewImageQueryImageViewsBaseContinousScanView(
    ViewImageQueryImageViewsBase, BaseModel
):
    typename: Literal["ContinousScanView"] = Field(
        alias="__typename", default="ContinousScanView", exclude=True
    )


class ViewImageQueryImageViewsBaseWellPositionView(
    ViewImageQueryImageViewsBase, BaseModel
):
    typename: Literal["WellPositionView"] = Field(
        alias="__typename", default="WellPositionView", exclude=True
    )


class ViewImageQueryImageViewsBaseAcquisitionView(
    ViewImageQueryImageViewsBase, BaseModel
):
    typename: Literal["AcquisitionView"] = Field(
        alias="__typename", default="AcquisitionView", exclude=True
    )


class ViewImageQueryImage(HasZarrStoreTrait, BaseModel):
    typename: Literal["Image"] = Field(
        alias="__typename", default="Image", exclude=True
    )
    id: ID
    store: ViewImageQueryImageStore
    "The store where the image data is stored."
    views: Tuple[
        Annotated[
            Union[
                ViewImageQueryImageViewsBaseFileView,
                ViewImageQueryImageViewsBaseAffineTransformationView,
                ViewImageQueryImageViewsBaseLabelView,
                ViewImageQueryImageViewsBaseChannelView,
                ViewImageQueryImageViewsBaseTimepointView,
                ViewImageQueryImageViewsBaseOpticsView,
                ViewImageQueryImageViewsBaseStructureView,
                ViewImageQueryImageViewsBaseScaleView,
                ViewImageQueryImageViewsBaseDerivedView,
                ViewImageQueryImageViewsBaseROIView,
                ViewImageQueryImageViewsBasePixelView,
                ViewImageQueryImageViewsBaseRGBView,
                ViewImageQueryImageViewsBaseContinousScanView,
                ViewImageQueryImageViewsBaseWellPositionView,
                ViewImageQueryImageViewsBaseAcquisitionView,
            ],
            Field(discriminator="typename"),
        ],
        ...,
    ]
    "All views of this image"
    model_config = ConfigDict(frozen=True)


class ViewImageQuery(BaseModel):
    image: ViewImageQueryImage
    "Returns a single image by ID"

    class Arguments(BaseModel):
        id: ID
        filtersggg: Optional[ViewFilter] = Field(default=None)

    class Meta:
        document = "query ViewImage($id: ID!, $filtersggg: ViewFilter) {\n  image(id: $id) {\n    id\n    store {\n      id\n      key\n      bucket\n      __typename\n    }\n    views(filters: $filtersggg) {\n      ... on RGBView {\n        id\n      }\n      __typename\n    }\n    __typename\n  }\n}"


class GetSnapshotQuery(BaseModel):
    snapshot: Snapshot

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Snapshot on Snapshot {\n  id\n  store {\n    key\n    presignedUrl\n    __typename\n  }\n  name\n  __typename\n}\n\nquery GetSnapshot($id: ID!) {\n  snapshot(id: $id) {\n    ...Snapshot\n    __typename\n  }\n}"


class SearchSnapshotsQueryOptions(BaseModel):
    typename: Literal["Snapshot"] = Field(
        alias="__typename", default="Snapshot", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchSnapshotsQuery(BaseModel):
    options: Tuple[SearchSnapshotsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchSnapshots($search: String, $values: [ID!]) {\n  options: snapshots(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class GetRGBContextQuery(BaseModel):
    rgbcontext: RGBContext

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  contexts {\n    id\n    name\n    __typename\n  }\n  name\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    derivedScaleViews {\n      id\n      image {\n        id\n        store {\n          ...ZarrStore\n          __typename\n        }\n        __typename\n      }\n      scaleX\n      scaleY\n      scaleZ\n      scaleT\n      scaleC\n      __typename\n    }\n    __typename\n  }\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  fullColour\n  baseColor\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n    __typename\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    __typename\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n  __typename\n}\n\nquery GetRGBContext($id: ID!) {\n  rgbcontext(id: $id) {\n    ...RGBContext\n    __typename\n  }\n}"


class GetMeshQuery(BaseModel):
    mesh: Mesh

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment MeshStore on MeshStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Mesh on Mesh {\n  id\n  name\n  store {\n    ...MeshStore\n    __typename\n  }\n  __typename\n}\n\nquery GetMesh($id: ID!) {\n  mesh(id: $id) {\n    ...Mesh\n    __typename\n  }\n}"


class SearchMeshesQueryOptions(BaseModel):
    typename: Literal["Mesh"] = Field(alias="__typename", default="Mesh", exclude=True)
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class SearchMeshesQuery(BaseModel):
    options: Tuple[SearchMeshesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "query SearchMeshes($search: String, $values: [ID!], $pagination: OffsetPaginationInput) {\n  options: meshes(\n    filters: {search: $search, ids: $values}\n    pagination: $pagination\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class WatchFilesSubscriptionFiles(BaseModel):
    typename: Literal["FileEvent"] = Field(
        alias="__typename", default="FileEvent", exclude=True
    )
    create: Optional[File] = Field(default=None)
    delete: Optional[ID] = Field(default=None)
    update: Optional[File] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class WatchFilesSubscription(BaseModel):
    files: WatchFilesSubscriptionFiles
    "Subscribe to real-time file updates"

    class Arguments(BaseModel):
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n  __typename\n}\n\nfragment File on File {\n  origins {\n    id\n    __typename\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n    __typename\n  }\n  __typename\n}\n\nsubscription WatchFiles($dataset: ID) {\n  files(dataset: $dataset) {\n    create {\n      ...File\n      __typename\n    }\n    delete\n    update {\n      ...File\n      __typename\n    }\n    __typename\n  }\n}"


class WatchImagesSubscriptionImages(BaseModel):
    typename: Literal["ImageEvent"] = Field(
        alias="__typename", default="ImageEvent", exclude=True
    )
    create: Optional[Image] = Field(default=None)
    delete: Optional[ID] = Field(default=None)
    update: Optional[Image] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class WatchImagesSubscription(BaseModel):
    images: WatchImagesSubscriptionImages
    "Subscribe to real-time image updates"

    class Arguments(BaseModel):
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n  __typename\n}\n\nfragment View on View {\n  xMin\n  xMax\n  yMin\n  yMax\n  tMin\n  tMax\n  cMin\n  cMax\n  zMin\n  zMax\n  __typename\n}\n\nfragment Era on Era {\n  id\n  begin\n  name\n  __typename\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n    __typename\n  }\n  __typename\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n    __typename\n  }\n  __typename\n}\n\nfragment DerivedView on DerivedView {\n  ...View\n  id\n  originImage {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  id\n  objective {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  camera {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  instrument {\n    id\n    name\n    serialNumber\n    __typename\n  }\n  __typename\n}\n\nfragment PixelView on PixelView {\n  ...View\n  id\n  __typename\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  contexts {\n    id\n    name\n    __typename\n  }\n  name\n  image {\n    id\n    store {\n      ...ZarrStore\n      __typename\n    }\n    derivedScaleViews {\n      id\n      image {\n        id\n        store {\n          ...ZarrStore\n          __typename\n        }\n        __typename\n      }\n      scaleX\n      scaleY\n      scaleZ\n      scaleT\n      scaleC\n      __typename\n    }\n    __typename\n  }\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  fullColour\n  baseColor\n  __typename\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment WellPositionView on WellPositionView {\n  ...View\n  id\n  column\n  row\n  well {\n    id\n    rows\n    columns\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  label\n  __typename\n}\n\nfragment ContinousScanView on ContinousScanView {\n  ...View\n  id\n  direction\n  __typename\n}\n\nfragment AcquisitionView on AcquisitionView {\n  ...View\n  id\n  description\n  acquiredAt\n  operator {\n    sub\n    __typename\n  }\n  __typename\n}\n\nfragment FileView on FileView {\n  ...View\n  id\n  seriesIdentifier\n  file {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment StructureView on StructureView {\n  ...View\n  id\n  structure\n  __typename\n}\n\nfragment ROIView on ROIView {\n  ...View\n  id\n  roi {\n    id\n    name\n    __typename\n  }\n  __typename\n}\n\nfragment Image on Image {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...AcquisitionView\n    ...RGBView\n    ...WellPositionView\n    ...StructureView\n    ...DerivedView\n    ...ROIView\n    ...FileView\n    ...ContinousScanView\n    __typename\n  }\n  pixelViews {\n    ...PixelView\n    __typename\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nsubscription WatchImages($dataset: ID) {\n  images(dataset: $dataset) {\n    create {\n      ...Image\n      __typename\n    }\n    delete\n    update {\n      ...Image\n      __typename\n    }\n    __typename\n  }\n}"


class WatchRoisSubscriptionRois(BaseModel):
    typename: Literal["RoiEvent"] = Field(
        alias="__typename", default="RoiEvent", exclude=True
    )
    create: Optional[ROI] = Field(default=None)
    delete: Optional[ID] = Field(default=None)
    update: Optional[ROI] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class WatchRoisSubscription(BaseModel):
    rois: WatchRoisSubscriptionRois
    "Subscribe to real-time ROI updates"

    class Arguments(BaseModel):
        image: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nsubscription WatchRois($image: ID!) {\n  rois(image: $image) {\n    create {\n      ...ROI\n      __typename\n    }\n    delete\n    update {\n      ...ROI\n      __typename\n    }\n    __typename\n  }\n}"


async def acreate_camera(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    bit_depth: Optional[int] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    manufacturer: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateCameraMutationCreatecamera:
    """CreateCamera

    Create a new camera configuration

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        model: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        bit_depth: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        sensor_size_x: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        sensor_size_y: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        pixel_size_x: The `Micrometers` scalar type represents a matrix valuesas specified by
        pixel_size_y: The `Micrometers` scalar type represents a matrix valuesas specified by
        manufacturer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateCameraMutationCreatecamera
    """
    return (
        await aexecute(
            CreateCameraMutation,
            {
                "input": {
                    "serialNumber": serial_number,
                    "name": name,
                    "model": model,
                    "bitDepth": bit_depth,
                    "sensorSizeX": sensor_size_x,
                    "sensorSizeY": sensor_size_y,
                    "pixelSizeX": pixel_size_x,
                    "pixelSizeY": pixel_size_y,
                    "manufacturer": manufacturer,
                }
            },
            rath=rath,
        )
    ).create_camera


def create_camera(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    bit_depth: Optional[int] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    manufacturer: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateCameraMutationCreatecamera:
    """CreateCamera

    Create a new camera configuration

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        model: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        bit_depth: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        sensor_size_x: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        sensor_size_y: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        pixel_size_x: The `Micrometers` scalar type represents a matrix valuesas specified by
        pixel_size_y: The `Micrometers` scalar type represents a matrix valuesas specified by
        manufacturer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateCameraMutationCreatecamera
    """
    return execute(
        CreateCameraMutation,
        {
            "input": {
                "serialNumber": serial_number,
                "name": name,
                "model": model,
                "bitDepth": bit_depth,
                "sensorSizeX": sensor_size_x,
                "sensorSizeY": sensor_size_y,
                "pixelSizeX": pixel_size_x,
                "pixelSizeY": pixel_size_y,
                "manufacturer": manufacturer,
            }
        },
        rath=rath,
    ).create_camera


async def aensure_camera(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    bit_depth: Optional[int] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    manufacturer: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureCameraMutationEnsurecamera:
    """EnsureCamera

    Ensure a camera exists, creating if needed

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        model: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        bit_depth: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        sensor_size_x: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        sensor_size_y: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        pixel_size_x: The `Micrometers` scalar type represents a matrix valuesas specified by
        pixel_size_y: The `Micrometers` scalar type represents a matrix valuesas specified by
        manufacturer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureCameraMutationEnsurecamera
    """
    return (
        await aexecute(
            EnsureCameraMutation,
            {
                "input": {
                    "serialNumber": serial_number,
                    "name": name,
                    "model": model,
                    "bitDepth": bit_depth,
                    "sensorSizeX": sensor_size_x,
                    "sensorSizeY": sensor_size_y,
                    "pixelSizeX": pixel_size_x,
                    "pixelSizeY": pixel_size_y,
                    "manufacturer": manufacturer,
                }
            },
            rath=rath,
        )
    ).ensure_camera


def ensure_camera(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    bit_depth: Optional[int] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    manufacturer: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureCameraMutationEnsurecamera:
    """EnsureCamera

    Ensure a camera exists, creating if needed

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        model: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        bit_depth: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        sensor_size_x: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        sensor_size_y: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        pixel_size_x: The `Micrometers` scalar type represents a matrix valuesas specified by
        pixel_size_y: The `Micrometers` scalar type represents a matrix valuesas specified by
        manufacturer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureCameraMutationEnsurecamera
    """
    return execute(
        EnsureCameraMutation,
        {
            "input": {
                "serialNumber": serial_number,
                "name": name,
                "model": model,
                "bitDepth": bit_depth,
                "sensorSizeX": sensor_size_x,
                "sensorSizeY": sensor_size_y,
                "pixelSizeX": pixel_size_x,
                "pixelSizeY": pixel_size_y,
                "manufacturer": manufacturer,
            }
        },
        rath=rath,
    ).ensure_camera


async def acreate_render_tree(
    tree: TreeInput, name: str, rath: Optional[MikroNextRath] = None
) -> CreateRenderTreeMutationCreaterendertree:
    """CreateRenderTree

    Create a new render tree for image visualization

    Arguments:
        tree:  (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRenderTreeMutationCreaterendertree
    """
    return (
        await aexecute(
            CreateRenderTreeMutation, {"input": {"tree": tree, "name": name}}, rath=rath
        )
    ).create_render_tree


def create_render_tree(
    tree: TreeInput, name: str, rath: Optional[MikroNextRath] = None
) -> CreateRenderTreeMutationCreaterendertree:
    """CreateRenderTree

    Create a new render tree for image visualization

    Arguments:
        tree:  (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRenderTreeMutationCreaterendertree
    """
    return execute(
        CreateRenderTreeMutation, {"input": {"tree": tree, "name": name}}, rath=rath
    ).create_render_tree


async def afrom_parquet_like(
    dataframe: ParquetLike,
    name: str,
    origins: Optional[Iterable[ID]] = None,
    dataset: Optional[ID] = None,
    label_accessors: Optional[Iterable[PartialLabelAccessorInput]] = None,
    image_accessors: Optional[Iterable[PartialImageAccessorInput]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Table:
    """from_parquet_like

    Create a table from parquet-like data

    Arguments:
        dataframe: The parquet dataframe to create the table from
        name: The name of the table
        origins: The IDs of tables this table was derived from
        dataset: The dataset ID this table belongs to
        label_accessors: Label accessors to create for this table
        image_accessors: Image accessors to create for this table
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table
    """
    return (
        await aexecute(
            From_parquet_likeMutation,
            {
                "input": {
                    "dataframe": dataframe,
                    "name": name,
                    "origins": origins,
                    "dataset": dataset,
                    "labelAccessors": label_accessors,
                    "imageAccessors": image_accessors,
                }
            },
            rath=rath,
        )
    ).from_parquet_like


def from_parquet_like(
    dataframe: ParquetLike,
    name: str,
    origins: Optional[Iterable[ID]] = None,
    dataset: Optional[ID] = None,
    label_accessors: Optional[Iterable[PartialLabelAccessorInput]] = None,
    image_accessors: Optional[Iterable[PartialImageAccessorInput]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Table:
    """from_parquet_like

    Create a table from parquet-like data

    Arguments:
        dataframe: The parquet dataframe to create the table from
        name: The name of the table
        origins: The IDs of tables this table was derived from
        dataset: The dataset ID this table belongs to
        label_accessors: Label accessors to create for this table
        image_accessors: Image accessors to create for this table
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table
    """
    return execute(
        From_parquet_likeMutation,
        {
            "input": {
                "dataframe": dataframe,
                "name": name,
                "origins": origins,
                "dataset": dataset,
                "labelAccessors": label_accessors,
                "imageAccessors": image_accessors,
            }
        },
        rath=rath,
    ).from_parquet_like


async def arequest_table_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestTableUpload

    Request credentials to upload a new table

    Arguments:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials
    """
    return (
        await aexecute(
            RequestTableUploadMutation,
            {"input": {"key": key, "datalayer": datalayer}},
            rath=rath,
        )
    ).request_table_upload


def request_table_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestTableUpload

    Request credentials to upload a new table

    Arguments:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials
    """
    return execute(
        RequestTableUploadMutation,
        {"input": {"key": key, "datalayer": datalayer}},
        rath=rath,
    ).request_table_upload


async def arequest_table_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestTableAccess

    Request credentials to access a table

    Arguments:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials
    """
    return (
        await aexecute(
            RequestTableAccessMutation,
            {"input": {"store": store, "duration": duration}},
            rath=rath,
        )
    ).request_table_access


def request_table_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestTableAccess

    Request credentials to access a table

    Arguments:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials
    """
    return execute(
        RequestTableAccessMutation,
        {"input": {"store": store, "duration": duration}},
        rath=rath,
    ).request_table_access


async def acreate_rendered_plot(
    name: str,
    plot: Upload,
    overlays: Optional[Iterable[OverlayInput]] = None,
    rath: Optional[MikroNextRath] = None,
) -> RenderedPlot:
    """CreateRenderedPlot

    Create a new rendered plot

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        plot:  (required)
        overlays:  (required) (list)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RenderedPlot
    """
    return (
        await aexecute(
            CreateRenderedPlotMutation,
            {"input": {"name": name, "plot": plot, "overlays": overlays}},
            rath=rath,
        )
    ).create_rendered_plot


def create_rendered_plot(
    name: str,
    plot: Upload,
    overlays: Optional[Iterable[OverlayInput]] = None,
    rath: Optional[MikroNextRath] = None,
) -> RenderedPlot:
    """CreateRenderedPlot

    Create a new rendered plot

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        plot:  (required)
        overlays:  (required) (list)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RenderedPlot
    """
    return execute(
        CreateRenderedPlotMutation,
        {"input": {"name": name, "plot": plot, "overlays": overlays}},
        rath=rath,
    ).create_rendered_plot


async def afrom_file_like(
    name: str,
    file: FileLike,
    origins: Optional[Iterable[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> File:
    """from_file_like

    Create a file from file-like data

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        file: The `FileLike` scalar type represents a reference to a big file storage previously created by the user n a datalayer (required)
        origins: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        dataset: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

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
    origins: Optional[Iterable[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> File:
    """from_file_like

    Create a file from file-like data

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        file: The `FileLike` scalar type represents a reference to a big file storage previously created by the user n a datalayer (required)
        origins: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        dataset: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File
    """
    return execute(
        From_file_likeMutation,
        {"input": {"name": name, "file": file, "origins": origins, "dataset": dataset}},
        rath=rath,
    ).from_file_like


async def arequest_file_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestFileUpload

    Request credentials to upload a new file

    Arguments:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

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
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestFileUpload

    Request credentials to upload a new file

    Arguments:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials
    """
    return execute(
        RequestFileUploadMutation,
        {"input": {"key": key, "datalayer": datalayer}},
        rath=rath,
    ).request_file_upload


async def arequest_file_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestFileAccess

    Request credentials to access a file

    Arguments:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

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
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestFileAccess

    Request credentials to access a file

    Arguments:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials
    """
    return execute(
        RequestFileAccessMutation,
        {"input": {"store": store, "duration": duration}},
        rath=rath,
    ).request_file_access


async def acreate_stage(
    name: str, instrument: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> Stage:
    """CreateStage

    Create a new stage for organizing data

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        instrument: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage
    """
    return (
        await aexecute(
            CreateStageMutation,
            {"input": {"name": name, "instrument": instrument}},
            rath=rath,
        )
    ).create_stage


def create_stage(
    name: str, instrument: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> Stage:
    """CreateStage

    Create a new stage for organizing data

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        instrument: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage
    """
    return execute(
        CreateStageMutation,
        {"input": {"name": name, "instrument": instrument}},
        rath=rath,
    ).create_stage


async def acreate_roi(
    image: ID,
    vectors: Iterable[FiveDVector],
    kind: RoiKind,
    rath: Optional[MikroNextRath] = None,
) -> ROI:
    """CreateRoi

    Create a new region of interest

    Arguments:
        image: The image this ROI belongs to
        vectors: The vector coordinates defining the ROI
        kind: The type/kind of ROI
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI
    """
    return (
        await aexecute(
            CreateRoiMutation,
            {"input": {"image": image, "vectors": vectors, "kind": kind}},
            rath=rath,
        )
    ).create_roi


def create_roi(
    image: ID,
    vectors: Iterable[FiveDVector],
    kind: RoiKind,
    rath: Optional[MikroNextRath] = None,
) -> ROI:
    """CreateRoi

    Create a new region of interest

    Arguments:
        image: The image this ROI belongs to
        vectors: The vector coordinates defining the ROI
        kind: The type/kind of ROI
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI
    """
    return execute(
        CreateRoiMutation,
        {"input": {"image": image, "vectors": vectors, "kind": kind}},
        rath=rath,
    ).create_roi


async def adelete_roi(id: ID, rath: Optional[MikroNextRath] = None) -> ID:
    """DeleteRoi

    Delete an existing region of interest

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ID
    """
    return (
        await aexecute(DeleteRoiMutation, {"input": {"id": id}}, rath=rath)
    ).delete_roi


def delete_roi(id: ID, rath: Optional[MikroNextRath] = None) -> ID:
    """DeleteRoi

    Delete an existing region of interest

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ID
    """
    return execute(DeleteRoiMutation, {"input": {"id": id}}, rath=rath).delete_roi


async def aupdate_roi(
    roi: ID,
    vectors: Optional[Iterable[FiveDVector]] = None,
    kind: Optional[RoiKind] = None,
    entity: Optional[ID] = None,
    entity_kind: Optional[ID] = None,
    entity_group: Optional[ID] = None,
    entity_parent: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> ROI:
    """UpdateRoi

    Update an existing region of interest

    Arguments:
        roi: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        vectors: The `Vector` scalar type represents a matrix values as specified by (required) (list)
        kind: RoiKind
        entity: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        entity_kind: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        entity_group: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        entity_parent: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI
    """
    return (
        await aexecute(
            UpdateRoiMutation,
            {
                "input": {
                    "roi": roi,
                    "vectors": vectors,
                    "kind": kind,
                    "entity": entity,
                    "entityKind": entity_kind,
                    "entityGroup": entity_group,
                    "entityParent": entity_parent,
                }
            },
            rath=rath,
        )
    ).update_roi


def update_roi(
    roi: ID,
    vectors: Optional[Iterable[FiveDVector]] = None,
    kind: Optional[RoiKind] = None,
    entity: Optional[ID] = None,
    entity_kind: Optional[ID] = None,
    entity_group: Optional[ID] = None,
    entity_parent: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> ROI:
    """UpdateRoi

    Update an existing region of interest

    Arguments:
        roi: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        vectors: The `Vector` scalar type represents a matrix values as specified by (required) (list)
        kind: RoiKind
        entity: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        entity_kind: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        entity_group: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        entity_parent: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI
    """
    return execute(
        UpdateRoiMutation,
        {
            "input": {
                "roi": roi,
                "vectors": vectors,
                "kind": kind,
                "entity": entity,
                "entityKind": entity_kind,
                "entityGroup": entity_group,
                "entityParent": entity_parent,
            }
        },
        rath=rath,
    ).update_roi


async def acreate_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    immersion: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateObjectiveMutationCreateobjective:
    """CreateObjective

    Create a new microscope objective configuration

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        na: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        magnification: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        immersion: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateObjectiveMutationCreateobjective
    """
    return (
        await aexecute(
            CreateObjectiveMutation,
            {
                "input": {
                    "serialNumber": serial_number,
                    "name": name,
                    "na": na,
                    "magnification": magnification,
                    "immersion": immersion,
                }
            },
            rath=rath,
        )
    ).create_objective


def create_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    immersion: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateObjectiveMutationCreateobjective:
    """CreateObjective

    Create a new microscope objective configuration

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        na: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        magnification: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        immersion: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateObjectiveMutationCreateobjective
    """
    return execute(
        CreateObjectiveMutation,
        {
            "input": {
                "serialNumber": serial_number,
                "name": name,
                "na": na,
                "magnification": magnification,
                "immersion": immersion,
            }
        },
        rath=rath,
    ).create_objective


async def aensure_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    immersion: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureObjectiveMutationEnsureobjective:
    """EnsureObjective

    Ensure an objective exists, creating if needed

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        na: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        magnification: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        immersion: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureObjectiveMutationEnsureobjective
    """
    return (
        await aexecute(
            EnsureObjectiveMutation,
            {
                "input": {
                    "serialNumber": serial_number,
                    "name": name,
                    "na": na,
                    "magnification": magnification,
                    "immersion": immersion,
                }
            },
            rath=rath,
        )
    ).ensure_objective


def ensure_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    immersion: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureObjectiveMutationEnsureobjective:
    """EnsureObjective

    Ensure an objective exists, creating if needed

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        na: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        magnification: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        immersion: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureObjectiveMutationEnsureobjective
    """
    return execute(
        EnsureObjectiveMutation,
        {
            "input": {
                "serialNumber": serial_number,
                "name": name,
                "na": na,
                "magnification": magnification,
                "immersion": immersion,
            }
        },
        rath=rath,
    ).ensure_objective


async def acreate_dataset(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset

    Create a new dataset to organize data

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateDatasetMutationCreatedataset
    """
    return (
        await aexecute(CreateDatasetMutation, {"input": {"name": name}}, rath=rath)
    ).create_dataset


def create_dataset(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset

    Create a new dataset to organize data

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateDatasetMutationCreatedataset
    """
    return execute(
        CreateDatasetMutation, {"input": {"name": name}}, rath=rath
    ).create_dataset


async def aupdate_dataset(
    name: str, id: ID, rath: Optional[MikroNextRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset

    Update dataset metadata

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        UpdateDatasetMutationUpdatedataset
    """
    return (
        await aexecute(
            UpdateDatasetMutation, {"input": {"name": name, "id": id}}, rath=rath
        )
    ).update_dataset


def update_dataset(
    name: str, id: ID, rath: Optional[MikroNextRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset

    Update dataset metadata

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        UpdateDatasetMutationUpdatedataset
    """
    return execute(
        UpdateDatasetMutation, {"input": {"name": name, "id": id}}, rath=rath
    ).update_dataset


async def arevert_dataset(
    id: ID, history_id: ID, rath: Optional[MikroNextRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset

    Revert dataset to a previous version

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        history_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

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
    id: ID, history_id: ID, rath: Optional[MikroNextRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset

    Revert dataset to a previous version

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        history_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RevertDatasetMutationRevertdataset
    """
    return execute(
        RevertDatasetMutation, {"input": {"id": id, "historyId": history_id}}, rath=rath
    ).revert_dataset


async def acreate_instrument(
    serial_number: str,
    manufacturer: Optional[str] = None,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateInstrumentMutationCreateinstrument:
    """CreateInstrument

    Create a new instrument configuration

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        manufacturer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        model: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateInstrumentMutationCreateinstrument
    """
    return (
        await aexecute(
            CreateInstrumentMutation,
            {
                "input": {
                    "serialNumber": serial_number,
                    "manufacturer": manufacturer,
                    "name": name,
                    "model": model,
                }
            },
            rath=rath,
        )
    ).create_instrument


def create_instrument(
    serial_number: str,
    manufacturer: Optional[str] = None,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateInstrumentMutationCreateinstrument:
    """CreateInstrument

    Create a new instrument configuration

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        manufacturer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        model: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateInstrumentMutationCreateinstrument
    """
    return execute(
        CreateInstrumentMutation,
        {
            "input": {
                "serialNumber": serial_number,
                "manufacturer": manufacturer,
                "name": name,
                "model": model,
            }
        },
        rath=rath,
    ).create_instrument


async def aensure_instrument(
    serial_number: str,
    manufacturer: Optional[str] = None,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureInstrumentMutationEnsureinstrument:
    """EnsureInstrument

    Ensure an instrument exists, creating if needed

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        manufacturer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        model: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureInstrumentMutationEnsureinstrument
    """
    return (
        await aexecute(
            EnsureInstrumentMutation,
            {
                "input": {
                    "serialNumber": serial_number,
                    "manufacturer": manufacturer,
                    "name": name,
                    "model": model,
                }
            },
            rath=rath,
        )
    ).ensure_instrument


def ensure_instrument(
    serial_number: str,
    manufacturer: Optional[str] = None,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureInstrumentMutationEnsureinstrument:
    """EnsureInstrument

    Ensure an instrument exists, creating if needed

    Arguments:
        serial_number: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        manufacturer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        model: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureInstrumentMutationEnsureinstrument
    """
    return execute(
        EnsureInstrumentMutation,
        {
            "input": {
                "serialNumber": serial_number,
                "manufacturer": manufacturer,
                "name": name,
                "model": model,
            }
        },
        rath=rath,
    ).ensure_instrument


async def afrom_array_like(
    array: ArrayLike,
    name: str,
    dataset: Optional[ID] = None,
    channel_views: Optional[Iterable[PartialChannelViewInput]] = None,
    transformation_views: Optional[
        Iterable[PartialAffineTransformationViewInput]
    ] = None,
    acquisition_views: Optional[Iterable[PartialAcquisitionViewInput]] = None,
    pixel_views: Optional[Iterable[PartialPixelViewInput]] = None,
    structure_views: Optional[Iterable[PartialStructureViewInput]] = None,
    rgb_views: Optional[Iterable[PartialRGBViewInput]] = None,
    timepoint_views: Optional[Iterable[PartialTimepointViewInput]] = None,
    optics_views: Optional[Iterable[PartialOpticsViewInput]] = None,
    scale_views: Optional[Iterable[PartialScaleViewInput]] = None,
    tags: Optional[Iterable[str]] = None,
    roi_views: Optional[Iterable[PartialROIViewInput]] = None,
    file_views: Optional[Iterable[PartialFileViewInput]] = None,
    derived_views: Optional[Iterable[PartialDerivedViewInput]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Image:
    """from_array_like

    Create an image from array-like data

    Arguments:
        array: The array-like object to create the image from
        name: The name of the image
        dataset: Optional dataset ID to associate the image with
        channel_views: Optional list of channel views
        transformation_views: Optional list of affine transformation views
        acquisition_views: Optional list of acquisition views
        pixel_views: Optional list of pixel views
        structure_views: Optional list of structure views
        rgb_views: Optional list of RGB views
        timepoint_views: Optional list of timepoint views
        optics_views: Optional list of optics views
        scale_views: Optional list of scale views
        tags: Optional list of tags to associate with the image
        roi_views: Optional list of ROI views
        file_views: Optional list of file views
        derived_views: Optional list of derived views
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image
    """
    return (
        await aexecute(
            From_array_likeMutation,
            {
                "input": {
                    "array": array,
                    "name": name,
                    "dataset": dataset,
                    "channelViews": channel_views,
                    "transformationViews": transformation_views,
                    "acquisitionViews": acquisition_views,
                    "pixelViews": pixel_views,
                    "structureViews": structure_views,
                    "rgbViews": rgb_views,
                    "timepointViews": timepoint_views,
                    "opticsViews": optics_views,
                    "scaleViews": scale_views,
                    "tags": tags,
                    "roiViews": roi_views,
                    "fileViews": file_views,
                    "derivedViews": derived_views,
                }
            },
            rath=rath,
        )
    ).from_array_like


def from_array_like(
    array: ArrayLike,
    name: str,
    dataset: Optional[ID] = None,
    channel_views: Optional[Iterable[PartialChannelViewInput]] = None,
    transformation_views: Optional[
        Iterable[PartialAffineTransformationViewInput]
    ] = None,
    acquisition_views: Optional[Iterable[PartialAcquisitionViewInput]] = None,
    pixel_views: Optional[Iterable[PartialPixelViewInput]] = None,
    structure_views: Optional[Iterable[PartialStructureViewInput]] = None,
    rgb_views: Optional[Iterable[PartialRGBViewInput]] = None,
    timepoint_views: Optional[Iterable[PartialTimepointViewInput]] = None,
    optics_views: Optional[Iterable[PartialOpticsViewInput]] = None,
    scale_views: Optional[Iterable[PartialScaleViewInput]] = None,
    tags: Optional[Iterable[str]] = None,
    roi_views: Optional[Iterable[PartialROIViewInput]] = None,
    file_views: Optional[Iterable[PartialFileViewInput]] = None,
    derived_views: Optional[Iterable[PartialDerivedViewInput]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Image:
    """from_array_like

    Create an image from array-like data

    Arguments:
        array: The array-like object to create the image from
        name: The name of the image
        dataset: Optional dataset ID to associate the image with
        channel_views: Optional list of channel views
        transformation_views: Optional list of affine transformation views
        acquisition_views: Optional list of acquisition views
        pixel_views: Optional list of pixel views
        structure_views: Optional list of structure views
        rgb_views: Optional list of RGB views
        timepoint_views: Optional list of timepoint views
        optics_views: Optional list of optics views
        scale_views: Optional list of scale views
        tags: Optional list of tags to associate with the image
        roi_views: Optional list of ROI views
        file_views: Optional list of file views
        derived_views: Optional list of derived views
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image
    """
    return execute(
        From_array_likeMutation,
        {
            "input": {
                "array": array,
                "name": name,
                "dataset": dataset,
                "channelViews": channel_views,
                "transformationViews": transformation_views,
                "acquisitionViews": acquisition_views,
                "pixelViews": pixel_views,
                "structureViews": structure_views,
                "rgbViews": rgb_views,
                "timepointViews": timepoint_views,
                "opticsViews": optics_views,
                "scaleViews": scale_views,
                "tags": tags,
                "roiViews": roi_views,
                "fileViews": file_views,
                "derivedViews": derived_views,
            }
        },
        rath=rath,
    ).from_array_like


async def arequest_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestUpload

    Request credentials to upload a new image

    Arguments:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

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
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestUpload

    Request credentials to upload a new image

    Arguments:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials
    """
    return execute(
        RequestUploadMutation,
        {"input": {"key": key, "datalayer": datalayer}},
        rath=rath,
    ).request_upload


async def arequest_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestAccess

    Request credentials to access an image

    Arguments:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

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
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestAccess

    Request credentials to access an image

    Arguments:
        store: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        duration: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials
    """
    return execute(
        RequestAccessMutation,
        {"input": {"store": store, "duration": duration}},
        rath=rath,
    ).request_access


async def acreate_era(
    name: str, begin: Optional[datetime] = None, rath: Optional[MikroNextRath] = None
) -> CreateEraMutationCreateera:
    """CreateEra

    Create a new era for temporal organization

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        begin: Date with time (isoformat)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEraMutationCreateera
    """
    return (
        await aexecute(
            CreateEraMutation, {"input": {"name": name, "begin": begin}}, rath=rath
        )
    ).create_era


def create_era(
    name: str, begin: Optional[datetime] = None, rath: Optional[MikroNextRath] = None
) -> CreateEraMutationCreateera:
    """CreateEra

    Create a new era for temporal organization

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        begin: Date with time (isoformat)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEraMutationCreateera
    """
    return execute(
        CreateEraMutation, {"input": {"name": name, "begin": begin}}, rath=rath
    ).create_era


async def acreate_snapshot(
    file: Upload, image: ID, rath: Optional[MikroNextRath] = None
) -> Snapshot:
    """CreateSnapshot

    Create a new state snapshot

    Arguments:
        file:  (required)
        image: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot
    """
    return (
        await aexecute(
            CreateSnapshotMutation, {"input": {"file": file, "image": image}}, rath=rath
        )
    ).create_snapshot


def create_snapshot(
    file: Upload, image: ID, rath: Optional[MikroNextRath] = None
) -> Snapshot:
    """CreateSnapshot

    Create a new state snapshot

    Arguments:
        file:  (required)
        image: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot
    """
    return execute(
        CreateSnapshotMutation, {"input": {"file": file, "image": image}}, rath=rath
    ).create_snapshot


async def acreate_rgb_view(
    context: ID,
    image: ID,
    collection: Optional[ID] = None,
    z_min: Optional[int] = None,
    z_max: Optional[int] = None,
    x_min: Optional[int] = None,
    x_max: Optional[int] = None,
    y_min: Optional[int] = None,
    y_max: Optional[int] = None,
    t_min: Optional[int] = None,
    t_max: Optional[int] = None,
    c_min: Optional[int] = None,
    c_max: Optional[int] = None,
    gamma: Optional[float] = None,
    contrast_limit_min: Optional[float] = None,
    contrast_limit_max: Optional[float] = None,
    rescale: Optional[bool] = None,
    scale: Optional[float] = None,
    active: Optional[bool] = None,
    color_map: Optional[ColorMap] = None,
    base_color: Optional[Iterable[float]] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateRgbViewMutationCreatergbview:
    """CreateRgbView

    Create a new view for RGB image data

    Arguments:
        collection: The collection this view belongs to
        z_min: The minimum z coordinate of the view
        z_max: The maximum z coordinate of the view
        x_min: The minimum x coordinate of the view
        x_max: The maximum x coordinate of the view
        y_min: The minimum y coordinate of the view
        y_max: The maximum y coordinate of the view
        t_min: The minimum t coordinate of the view
        t_max: The maximum t coordinate of the view
        c_min: The minimum c (channel) coordinate of the view
        c_max: The maximum c (channel) coordinate of the view
        context: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        gamma: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        contrast_limit_min: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        contrast_limit_max: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        rescale: The `Boolean` scalar type represents `true` or `false`.
        scale: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        active: The `Boolean` scalar type represents `true` or `false`.
        color_map: ColorMap
        base_color: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point). (required) (list)
        image: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRgbViewMutationCreatergbview
    """
    return (
        await aexecute(
            CreateRgbViewMutation,
            {
                "input": {
                    "collection": collection,
                    "zMin": z_min,
                    "zMax": z_max,
                    "xMin": x_min,
                    "xMax": x_max,
                    "yMin": y_min,
                    "yMax": y_max,
                    "tMin": t_min,
                    "tMax": t_max,
                    "cMin": c_min,
                    "cMax": c_max,
                    "context": context,
                    "gamma": gamma,
                    "contrastLimitMin": contrast_limit_min,
                    "contrastLimitMax": contrast_limit_max,
                    "rescale": rescale,
                    "scale": scale,
                    "active": active,
                    "colorMap": color_map,
                    "baseColor": base_color,
                    "image": image,
                }
            },
            rath=rath,
        )
    ).create_rgb_view


def create_rgb_view(
    context: ID,
    image: ID,
    collection: Optional[ID] = None,
    z_min: Optional[int] = None,
    z_max: Optional[int] = None,
    x_min: Optional[int] = None,
    x_max: Optional[int] = None,
    y_min: Optional[int] = None,
    y_max: Optional[int] = None,
    t_min: Optional[int] = None,
    t_max: Optional[int] = None,
    c_min: Optional[int] = None,
    c_max: Optional[int] = None,
    gamma: Optional[float] = None,
    contrast_limit_min: Optional[float] = None,
    contrast_limit_max: Optional[float] = None,
    rescale: Optional[bool] = None,
    scale: Optional[float] = None,
    active: Optional[bool] = None,
    color_map: Optional[ColorMap] = None,
    base_color: Optional[Iterable[float]] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateRgbViewMutationCreatergbview:
    """CreateRgbView

    Create a new view for RGB image data

    Arguments:
        collection: The collection this view belongs to
        z_min: The minimum z coordinate of the view
        z_max: The maximum z coordinate of the view
        x_min: The minimum x coordinate of the view
        x_max: The maximum x coordinate of the view
        y_min: The minimum y coordinate of the view
        y_max: The maximum y coordinate of the view
        t_min: The minimum t coordinate of the view
        t_max: The maximum t coordinate of the view
        c_min: The minimum c (channel) coordinate of the view
        c_max: The maximum c (channel) coordinate of the view
        context: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        gamma: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        contrast_limit_min: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        contrast_limit_max: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        rescale: The `Boolean` scalar type represents `true` or `false`.
        scale: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).
        active: The `Boolean` scalar type represents `true` or `false`.
        color_map: ColorMap
        base_color: The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point). (required) (list)
        image: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRgbViewMutationCreatergbview
    """
    return execute(
        CreateRgbViewMutation,
        {
            "input": {
                "collection": collection,
                "zMin": z_min,
                "zMax": z_max,
                "xMin": x_min,
                "xMax": x_max,
                "yMin": y_min,
                "yMax": y_max,
                "tMin": t_min,
                "tMax": t_max,
                "cMin": c_min,
                "cMax": c_max,
                "context": context,
                "gamma": gamma,
                "contrastLimitMin": contrast_limit_min,
                "contrastLimitMax": contrast_limit_max,
                "rescale": rescale,
                "scale": scale,
                "active": active,
                "colorMap": color_map,
                "baseColor": base_color,
                "image": image,
            }
        },
        rath=rath,
    ).create_rgb_view


async def acreate_label_view(
    label: str,
    image: ID,
    collection: Optional[ID] = None,
    z_min: Optional[int] = None,
    z_max: Optional[int] = None,
    x_min: Optional[int] = None,
    x_max: Optional[int] = None,
    y_min: Optional[int] = None,
    y_max: Optional[int] = None,
    t_min: Optional[int] = None,
    t_max: Optional[int] = None,
    c_min: Optional[int] = None,
    c_max: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> LabelView:
    """CreateLabelView

    Create a new view for label data

    Arguments:
        collection: The collection this view belongs to
        z_min: The minimum z coordinate of the view
        z_max: The maximum z coordinate of the view
        x_min: The minimum x coordinate of the view
        x_max: The maximum x coordinate of the view
        y_min: The minimum y coordinate of the view
        y_max: The maximum y coordinate of the view
        t_min: The minimum t coordinate of the view
        t_max: The maximum t coordinate of the view
        c_min: The minimum c (channel) coordinate of the view
        c_max: The maximum c (channel) coordinate of the view
        label: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        image: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        LabelView
    """
    return (
        await aexecute(
            CreateLabelViewMutation,
            {
                "input": {
                    "collection": collection,
                    "zMin": z_min,
                    "zMax": z_max,
                    "xMin": x_min,
                    "xMax": x_max,
                    "yMin": y_min,
                    "yMax": y_max,
                    "tMin": t_min,
                    "tMax": t_max,
                    "cMin": c_min,
                    "cMax": c_max,
                    "label": label,
                    "image": image,
                }
            },
            rath=rath,
        )
    ).create_label_view


def create_label_view(
    label: str,
    image: ID,
    collection: Optional[ID] = None,
    z_min: Optional[int] = None,
    z_max: Optional[int] = None,
    x_min: Optional[int] = None,
    x_max: Optional[int] = None,
    y_min: Optional[int] = None,
    y_max: Optional[int] = None,
    t_min: Optional[int] = None,
    t_max: Optional[int] = None,
    c_min: Optional[int] = None,
    c_max: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> LabelView:
    """CreateLabelView

    Create a new view for label data

    Arguments:
        collection: The collection this view belongs to
        z_min: The minimum z coordinate of the view
        z_max: The maximum z coordinate of the view
        x_min: The minimum x coordinate of the view
        x_max: The maximum x coordinate of the view
        y_min: The minimum y coordinate of the view
        y_max: The maximum y coordinate of the view
        t_min: The minimum t coordinate of the view
        t_max: The maximum t coordinate of the view
        c_min: The minimum c (channel) coordinate of the view
        c_max: The maximum c (channel) coordinate of the view
        label: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        image: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        LabelView
    """
    return execute(
        CreateLabelViewMutation,
        {
            "input": {
                "collection": collection,
                "zMin": z_min,
                "zMax": z_max,
                "xMin": x_min,
                "xMax": x_max,
                "yMin": y_min,
                "yMax": y_max,
                "tMin": t_min,
                "tMax": t_max,
                "cMin": c_min,
                "cMax": c_max,
                "label": label,
                "image": image,
            }
        },
        rath=rath,
    ).create_label_view


async def acreate_rgb_context(
    image: ID,
    name: Optional[str] = None,
    thumbnail: Optional[ID] = None,
    views: Optional[Iterable[PartialRGBViewInput]] = None,
    z: Optional[int] = None,
    t: Optional[int] = None,
    c: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> RGBContext:
    """CreateRGBContext

    Create a new RGB context for image visualization

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        thumbnail: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        image: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        views:  (required) (list)
        z: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        c: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext
    """
    return (
        await aexecute(
            CreateRGBContextMutation,
            {
                "input": {
                    "name": name,
                    "thumbnail": thumbnail,
                    "image": image,
                    "views": views,
                    "z": z,
                    "t": t,
                    "c": c,
                }
            },
            rath=rath,
        )
    ).create_rgb_context


def create_rgb_context(
    image: ID,
    name: Optional[str] = None,
    thumbnail: Optional[ID] = None,
    views: Optional[Iterable[PartialRGBViewInput]] = None,
    z: Optional[int] = None,
    t: Optional[int] = None,
    c: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> RGBContext:
    """CreateRGBContext

    Create a new RGB context for image visualization

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        thumbnail: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        image: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        views:  (required) (list)
        z: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        c: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext
    """
    return execute(
        CreateRGBContextMutation,
        {
            "input": {
                "name": name,
                "thumbnail": thumbnail,
                "image": image,
                "views": views,
                "z": z,
                "t": t,
                "c": c,
            }
        },
        rath=rath,
    ).create_rgb_context


async def aupdate_rgb_context(
    id: ID,
    name: Optional[str] = None,
    thumbnail: Optional[ID] = None,
    views: Optional[Iterable[PartialRGBViewInput]] = None,
    z: Optional[int] = None,
    t: Optional[int] = None,
    c: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> RGBContext:
    """UpdateRGBContext

    Update settings of an existing RGB context

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        thumbnail: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        views:  (required) (list)
        z: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        c: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext
    """
    return (
        await aexecute(
            UpdateRGBContextMutation,
            {
                "input": {
                    "id": id,
                    "name": name,
                    "thumbnail": thumbnail,
                    "views": views,
                    "z": z,
                    "t": t,
                    "c": c,
                }
            },
            rath=rath,
        )
    ).update_rgb_context


def update_rgb_context(
    id: ID,
    name: Optional[str] = None,
    thumbnail: Optional[ID] = None,
    views: Optional[Iterable[PartialRGBViewInput]] = None,
    z: Optional[int] = None,
    t: Optional[int] = None,
    c: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> RGBContext:
    """UpdateRGBContext

    Update settings of an existing RGB context

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.
        thumbnail: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.
        views:  (required) (list)
        z: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        t: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        c: The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext
    """
    return execute(
        UpdateRGBContextMutation,
        {
            "input": {
                "id": id,
                "name": name,
                "thumbnail": thumbnail,
                "views": views,
                "z": z,
                "t": t,
                "c": c,
            }
        },
        rath=rath,
    ).update_rgb_context


async def acreate_view_collection(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateViewCollectionMutationCreateviewcollection:
    """CreateViewCollection

    Create a new collection of views to organize related views

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateViewCollectionMutationCreateviewcollection
    """
    return (
        await aexecute(
            CreateViewCollectionMutation, {"input": {"name": name}}, rath=rath
        )
    ).create_view_collection


def create_view_collection(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateViewCollectionMutationCreateviewcollection:
    """CreateViewCollection

    Create a new collection of views to organize related views

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateViewCollectionMutationCreateviewcollection
    """
    return execute(
        CreateViewCollectionMutation, {"input": {"name": name}}, rath=rath
    ).create_view_collection


async def acreate_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateChannelMutationCreatechannel:
    """CreateChannel

    Create a new channel

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateChannelMutationCreatechannel
    """
    return (
        await aexecute(CreateChannelMutation, {"input": {"name": name}}, rath=rath)
    ).create_channel


def create_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateChannelMutationCreatechannel:
    """CreateChannel

    Create a new channel

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateChannelMutationCreatechannel
    """
    return execute(
        CreateChannelMutation, {"input": {"name": name}}, rath=rath
    ).create_channel


async def aensure_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> EnsureChannelMutationEnsurechannel:
    """EnsureChannel

    Ensure a channel exists, creating if needed

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureChannelMutationEnsurechannel
    """
    return (
        await aexecute(EnsureChannelMutation, {"input": {"name": name}}, rath=rath)
    ).ensure_channel


def ensure_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> EnsureChannelMutationEnsurechannel:
    """EnsureChannel

    Ensure a channel exists, creating if needed

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureChannelMutationEnsurechannel
    """
    return execute(
        EnsureChannelMutation, {"input": {"name": name}}, rath=rath
    ).ensure_channel


async def acreate_mesh(
    mesh: MeshLike, name: str, rath: Optional[MikroNextRath] = None
) -> Mesh:
    """CreateMesh

    Create a new mesh

    Arguments:
        mesh: The `MeshLike` scalar type represents a reference to a mesh previously created by the user n a datalayer (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Mesh
    """
    return (
        await aexecute(
            CreateMeshMutation, {"input": {"mesh": mesh, "name": name}}, rath=rath
        )
    ).create_mesh


def create_mesh(
    mesh: MeshLike, name: str, rath: Optional[MikroNextRath] = None
) -> Mesh:
    """CreateMesh

    Create a new mesh

    Arguments:
        mesh: The `MeshLike` scalar type represents a reference to a mesh previously created by the user n a datalayer (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Mesh
    """
    return execute(
        CreateMeshMutation, {"input": {"mesh": mesh, "name": name}}, rath=rath
    ).create_mesh


async def arequest_mesh_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> PresignedPostCredentials:
    """RequestMeshUpload

    Request presigned credentials for mesh upload

    Arguments:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        PresignedPostCredentials
    """
    return (
        await aexecute(
            RequestMeshUploadMutation,
            {"input": {"key": key, "datalayer": datalayer}},
            rath=rath,
        )
    ).request_mesh_upload


def request_mesh_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> PresignedPostCredentials:
    """RequestMeshUpload

    Request presigned credentials for mesh upload

    Arguments:
        key: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        datalayer: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        PresignedPostCredentials
    """
    return execute(
        RequestMeshUploadMutation,
        {"input": {"key": key, "datalayer": datalayer}},
        rath=rath,
    ).request_mesh_upload


async def aget_camera(id: ID, rath: Optional[MikroNextRath] = None) -> Camera:
    """GetCamera


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Camera
    """
    return (await aexecute(GetCameraQuery, {"id": id}, rath=rath)).camera


def get_camera(id: ID, rath: Optional[MikroNextRath] = None) -> Camera:
    """GetCamera


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Camera
    """
    return execute(GetCameraQuery, {"id": id}, rath=rath).camera


async def aget_table(id: ID, rath: Optional[MikroNextRath] = None) -> Table:
    """GetTable


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table
    """
    return (await aexecute(GetTableQuery, {"id": id}, rath=rath)).table


def get_table(id: ID, rath: Optional[MikroNextRath] = None) -> Table:
    """GetTable


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table
    """
    return execute(GetTableQuery, {"id": id}, rath=rath).table


async def asearch_tables(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchTablesQueryOptions, ...]:
    """SearchTables


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchTablesQueryTables]
    """
    return (
        await aexecute(
            SearchTablesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_tables(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchTablesQueryOptions, ...]:
    """SearchTables


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchTablesQueryTables]
    """
    return execute(
        SearchTablesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_rendered_plot(
    id: ID, rath: Optional[MikroNextRath] = None
) -> RenderedPlot:
    """GetRenderedPlot


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RenderedPlot
    """
    return (await aexecute(GetRenderedPlotQuery, {"id": id}, rath=rath)).rendered_plot


def get_rendered_plot(id: ID, rath: Optional[MikroNextRath] = None) -> RenderedPlot:
    """GetRenderedPlot


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RenderedPlot
    """
    return execute(GetRenderedPlotQuery, {"id": id}, rath=rath).rendered_plot


async def alist_rendered_plots(
    rath: Optional[MikroNextRath] = None,
) -> Tuple[ListRenderedPlot, ...]:
    """ListRenderedPlots


    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ListRenderedPlot]
    """
    return (await aexecute(ListRenderedPlotsQuery, {}, rath=rath)).rendered_plots


def list_rendered_plots(
    rath: Optional[MikroNextRath] = None,
) -> Tuple[ListRenderedPlot, ...]:
    """ListRenderedPlots


    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ListRenderedPlot]
    """
    return execute(ListRenderedPlotsQuery, {}, rath=rath).rendered_plots


async def asearch_rendered_plots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchRenderedPlotsQueryOptions, ...]:
    """SearchRenderedPlots


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchRenderedPlotsQueryRenderedplots]
    """
    return (
        await aexecute(
            SearchRenderedPlotsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_rendered_plots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchRenderedPlotsQueryOptions, ...]:
    """SearchRenderedPlots


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchRenderedPlotsQueryRenderedplots]
    """
    return execute(
        SearchRenderedPlotsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_file(id: ID, rath: Optional[MikroNextRath] = None) -> File:
    """GetFile


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File
    """
    return (await aexecute(GetFileQuery, {"id": id}, rath=rath)).file


def get_file(id: ID, rath: Optional[MikroNextRath] = None) -> File:
    """GetFile


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File
    """
    return execute(GetFileQuery, {"id": id}, rath=rath).file


async def asearch_files(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchFilesQueryOptions, ...]:
    """SearchFiles


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

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
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchFilesQueryOptions, ...]:
    """SearchFiles


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchFilesQueryFiles]
    """
    return execute(
        SearchFilesQuery,
        {"search": search, "values": values, "pagination": pagination},
        rath=rath,
    ).options


async def aget_table_row(id: ID, rath: Optional[MikroNextRath] = None) -> TableRow:
    """GetTableRow


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        TableRow
    """
    return (await aexecute(GetTableRowQuery, {"id": id}, rath=rath)).table_row


def get_table_row(id: ID, rath: Optional[MikroNextRath] = None) -> TableRow:
    """GetTableRow


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        TableRow
    """
    return execute(GetTableRowQuery, {"id": id}, rath=rath).table_row


async def asearch_table_rows(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchTableRowsQueryOptions, ...]:
    """SearchTableRows


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchTableRowsQueryTablerows]
    """
    return (
        await aexecute(
            SearchTableRowsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_table_rows(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchTableRowsQueryOptions, ...]:
    """SearchTableRows


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchTableRowsQueryTablerows]
    """
    return execute(
        SearchTableRowsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_stage(id: ID, rath: Optional[MikroNextRath] = None) -> Stage:
    """GetStage


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage
    """
    return (await aexecute(GetStageQuery, {"id": id}, rath=rath)).stage


def get_stage(id: ID, rath: Optional[MikroNextRath] = None) -> Stage:
    """GetStage


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage
    """
    return execute(GetStageQuery, {"id": id}, rath=rath).stage


async def asearch_stages(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchStagesQueryOptions, ...]:
    """SearchStages


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchStagesQueryStages]
    """
    return (
        await aexecute(
            SearchStagesQuery,
            {"search": search, "values": values, "pagination": pagination},
            rath=rath,
        )
    ).options


def search_stages(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchStagesQueryOptions, ...]:
    """SearchStages


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchStagesQueryStages]
    """
    return execute(
        SearchStagesQuery,
        {"search": search, "values": values, "pagination": pagination},
        rath=rath,
    ).options


async def aget_rois(image: ID, rath: Optional[MikroNextRath] = None) -> Tuple[ROI, ...]:
    """GetRois


    Arguments:
        image (ID): No description
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ROI]
    """
    return (await aexecute(GetRoisQuery, {"image": image}, rath=rath)).rois


def get_rois(image: ID, rath: Optional[MikroNextRath] = None) -> Tuple[ROI, ...]:
    """GetRois


    Arguments:
        image (ID): No description
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ROI]
    """
    return execute(GetRoisQuery, {"image": image}, rath=rath).rois


async def aget_roi(id: ID, rath: Optional[MikroNextRath] = None) -> ROI:
    """GetRoi


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI
    """
    return (await aexecute(GetRoiQuery, {"id": id}, rath=rath)).roi


def get_roi(id: ID, rath: Optional[MikroNextRath] = None) -> ROI:
    """GetRoi


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI
    """
    return execute(GetRoiQuery, {"id": id}, rath=rath).roi


async def asearch_rois(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchRoisQueryOptions, ...]:
    """SearchRois


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchRoisQueryRois]
    """
    return (
        await aexecute(SearchRoisQuery, {"search": search, "values": values}, rath=rath)
    ).options


def search_rois(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchRoisQueryOptions, ...]:
    """SearchRois


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchRoisQueryRois]
    """
    return execute(
        SearchRoisQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_objective(id: ID, rath: Optional[MikroNextRath] = None) -> Objective:
    """GetObjective


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Objective
    """
    return (await aexecute(GetObjectiveQuery, {"id": id}, rath=rath)).objective


def get_objective(id: ID, rath: Optional[MikroNextRath] = None) -> Objective:
    """GetObjective


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Objective
    """
    return execute(GetObjectiveQuery, {"id": id}, rath=rath).objective


async def aget_dataset(id: ID, rath: Optional[MikroNextRath] = None) -> Dataset:
    """GetDataset


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Dataset
    """
    return (await aexecute(GetDatasetQuery, {"id": id}, rath=rath)).dataset


def get_dataset(id: ID, rath: Optional[MikroNextRath] = None) -> Dataset:
    """GetDataset


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Dataset
    """
    return execute(GetDatasetQuery, {"id": id}, rath=rath).dataset


async def aget_instrument(id: ID, rath: Optional[MikroNextRath] = None) -> Instrument:
    """GetInstrument


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Instrument
    """
    return (await aexecute(GetInstrumentQuery, {"id": id}, rath=rath)).instrument


def get_instrument(id: ID, rath: Optional[MikroNextRath] = None) -> Instrument:
    """GetInstrument


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Instrument
    """
    return execute(GetInstrumentQuery, {"id": id}, rath=rath).instrument


async def aget_table_cell(id: ID, rath: Optional[MikroNextRath] = None) -> TableCell:
    """GetTableCell


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        TableCell
    """
    return (await aexecute(GetTableCellQuery, {"id": id}, rath=rath)).table_cell


def get_table_cell(id: ID, rath: Optional[MikroNextRath] = None) -> TableCell:
    """GetTableCell


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        TableCell
    """
    return execute(GetTableCellQuery, {"id": id}, rath=rath).table_cell


async def asearch_table_cells(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchTableCellsQueryOptions, ...]:
    """SearchTableCells


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchTableCellsQueryTablecells]
    """
    return (
        await aexecute(
            SearchTableCellsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_table_cells(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchTableCellsQueryOptions, ...]:
    """SearchTableCells


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchTableCellsQueryTablecells]
    """
    return execute(
        SearchTableCellsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_image(id: ID, rath: Optional[MikroNextRath] = None) -> Image:
    """GetImage

    Returns a single image by ID

    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image
    """
    return (await aexecute(GetImageQuery, {"id": id}, rath=rath)).image


def get_image(id: ID, rath: Optional[MikroNextRath] = None) -> Image:
    """GetImage

    Returns a single image by ID

    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image
    """
    return execute(GetImageQuery, {"id": id}, rath=rath).image


async def aget_random_image(rath: Optional[MikroNextRath] = None) -> Image:
    """GetRandomImage


    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image
    """
    return (await aexecute(GetRandomImageQuery, {}, rath=rath)).random_image


def get_random_image(rath: Optional[MikroNextRath] = None) -> Image:
    """GetRandomImage


    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image
    """
    return execute(GetRandomImageQuery, {}, rath=rath).random_image


async def asearch_images(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchImagesQueryOptions, ...]:
    """SearchImages


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchImagesQueryImages]
    """
    return (
        await aexecute(
            SearchImagesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_images(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchImagesQueryOptions, ...]:
    """SearchImages


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchImagesQueryImages]
    """
    return execute(
        SearchImagesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aimages(
    filter: Optional[ImageFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[Image, ...]:
    """Images


    Arguments:
        filter (Optional[ImageFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[Image]
    """
    return (
        await aexecute(
            ImagesQuery, {"filter": filter, "pagination": pagination}, rath=rath
        )
    ).images


def images(
    filter: Optional[ImageFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[Image, ...]:
    """Images


    Arguments:
        filter (Optional[ImageFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[Image]
    """
    return execute(
        ImagesQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).images


async def aview_image(
    id: ID,
    filtersggg: Optional[ViewFilter] = None,
    rath: Optional[MikroNextRath] = None,
) -> ViewImageQueryImage:
    """ViewImage

    Returns a single image by ID

    Arguments:
        id (ID): The unique identifier of an object
        filtersggg (Optional[ViewFilter], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ViewImageQueryImage
    """
    return (
        await aexecute(ViewImageQuery, {"id": id, "filtersggg": filtersggg}, rath=rath)
    ).image


def view_image(
    id: ID,
    filtersggg: Optional[ViewFilter] = None,
    rath: Optional[MikroNextRath] = None,
) -> ViewImageQueryImage:
    """ViewImage

    Returns a single image by ID

    Arguments:
        id (ID): The unique identifier of an object
        filtersggg (Optional[ViewFilter], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ViewImageQueryImage
    """
    return execute(
        ViewImageQuery, {"id": id, "filtersggg": filtersggg}, rath=rath
    ).image


async def aget_snapshot(id: ID, rath: Optional[MikroNextRath] = None) -> Snapshot:
    """GetSnapshot


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot
    """
    return (await aexecute(GetSnapshotQuery, {"id": id}, rath=rath)).snapshot


def get_snapshot(id: ID, rath: Optional[MikroNextRath] = None) -> Snapshot:
    """GetSnapshot


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot
    """
    return execute(GetSnapshotQuery, {"id": id}, rath=rath).snapshot


async def asearch_snapshots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchSnapshotsQueryOptions, ...]:
    """SearchSnapshots


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchSnapshotsQuerySnapshots]
    """
    return (
        await aexecute(
            SearchSnapshotsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_snapshots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchSnapshotsQueryOptions, ...]:
    """SearchSnapshots


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchSnapshotsQuerySnapshots]
    """
    return execute(
        SearchSnapshotsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_rgb_context(id: ID, rath: Optional[MikroNextRath] = None) -> RGBContext:
    """GetRGBContext


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext
    """
    return (await aexecute(GetRGBContextQuery, {"id": id}, rath=rath)).rgbcontext


def get_rgb_context(id: ID, rath: Optional[MikroNextRath] = None) -> RGBContext:
    """GetRGBContext


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext
    """
    return execute(GetRGBContextQuery, {"id": id}, rath=rath).rgbcontext


async def aget_mesh(id: ID, rath: Optional[MikroNextRath] = None) -> Mesh:
    """GetMesh


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Mesh
    """
    return (await aexecute(GetMeshQuery, {"id": id}, rath=rath)).mesh


def get_mesh(id: ID, rath: Optional[MikroNextRath] = None) -> Mesh:
    """GetMesh


    Arguments:
        id (ID): The unique identifier of an object
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Mesh
    """
    return execute(GetMeshQuery, {"id": id}, rath=rath).mesh


async def asearch_meshes(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchMeshesQueryOptions, ...]:
    """SearchMeshes


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchMeshesQueryMeshes]
    """
    return (
        await aexecute(
            SearchMeshesQuery,
            {"search": search, "values": values, "pagination": pagination},
            rath=rath,
        )
    ).options


def search_meshes(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> Tuple[SearchMeshesQueryOptions, ...]:
    """SearchMeshes


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchMeshesQueryMeshes]
    """
    return execute(
        SearchMeshesQuery,
        {"search": search, "values": values, "pagination": pagination},
        rath=rath,
    ).options


async def awatch_files(
    dataset: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> AsyncIterator[WatchFilesSubscriptionFiles]:
    """WatchFiles

    Subscribe to real-time file updates

    Arguments:
        dataset (Optional[ID], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchFilesSubscriptionFiles
    """
    async for event in asubscribe(
        WatchFilesSubscription, {"dataset": dataset}, rath=rath
    ):
        yield event.files


def watch_files(
    dataset: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> Iterator[WatchFilesSubscriptionFiles]:
    """WatchFiles

    Subscribe to real-time file updates

    Arguments:
        dataset (Optional[ID], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchFilesSubscriptionFiles
    """
    for event in subscribe(WatchFilesSubscription, {"dataset": dataset}, rath=rath):
        yield event.files


async def awatch_images(
    dataset: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> AsyncIterator[WatchImagesSubscriptionImages]:
    """WatchImages

    Subscribe to real-time image updates

    Arguments:
        dataset (Optional[ID], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchImagesSubscriptionImages
    """
    async for event in asubscribe(
        WatchImagesSubscription, {"dataset": dataset}, rath=rath
    ):
        yield event.images


def watch_images(
    dataset: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> Iterator[WatchImagesSubscriptionImages]:
    """WatchImages

    Subscribe to real-time image updates

    Arguments:
        dataset (Optional[ID], optional): No description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchImagesSubscriptionImages
    """
    for event in subscribe(WatchImagesSubscription, {"dataset": dataset}, rath=rath):
        yield event.images


async def awatch_rois(
    image: ID, rath: Optional[MikroNextRath] = None
) -> AsyncIterator[WatchRoisSubscriptionRois]:
    """WatchRois

    Subscribe to real-time ROI updates

    Arguments:
        image (ID): No description
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchRoisSubscriptionRois
    """
    async for event in asubscribe(WatchRoisSubscription, {"image": image}, rath=rath):
        yield event.rois


def watch_rois(
    image: ID, rath: Optional[MikroNextRath] = None
) -> Iterator[WatchRoisSubscriptionRois]:
    """WatchRois

    Subscribe to real-time ROI updates

    Arguments:
        image (ID): No description
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchRoisSubscriptionRois
    """
    for event in subscribe(WatchRoisSubscription, {"image": image}, rath=rath):
        yield event.rois


AffineTransformationViewFilter.model_rebuild()
DatasetFilter.model_rebuild()
EraFilter.model_rebuild()
FromArrayLikeInput.model_rebuild()
FromParquetLike.model_rebuild()
ImageFilter.model_rebuild()
PartialPixelViewInput.model_rebuild()
ProvenanceFilter.model_rebuild()
RenderTreeInput.model_rebuild()
RenderedPlotInput.model_rebuild()
StageFilter.model_rebuild()
TimepointViewFilter.model_rebuild()
TreeInput.model_rebuild()
TreeNodeInput.model_rebuild()
ViewFilter.model_rebuild()
ZarrStoreFilter.model_rebuild()

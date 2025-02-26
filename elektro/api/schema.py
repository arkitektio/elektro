from pydantic import Field, BaseModel, ConfigDict
from typing import Literal, Iterable, Optional, Tuple, Iterator, List, AsyncIterator
from elektro.scalars import FileLike, TraceLike, FiveDVector
from elektro.traits import (
    HasZarrStoreAccessor,
    IsVectorizableTrait,
    HasDownloadAccessor,
    HasZarrStoreTrait,
)
from enum import Enum
from elektro.rath import ElektroRath
from elektro.funcs import asubscribe, aexecute, execute, subscribe
from rath.scalars import ID


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


class TraceFilter(BaseModel):
    name: Optional["StrFilterLookup"] = None
    ids: Optional[Tuple[ID, ...]] = None
    dataset: Optional["DatasetFilter"] = None
    not_derived: Optional[bool] = Field(alias="notDerived", default=None)
    provenance: Optional["ProvenanceFilter"] = None
    and_: Optional["TraceFilter"] = Field(alias="AND", default=None)
    or_: Optional["TraceFilter"] = Field(alias="OR", default=None)
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


class DatasetFilter(BaseModel):
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    provenance: Optional["ProvenanceFilter"] = None
    and_: Optional["DatasetFilter"] = Field(alias="AND", default=None)
    or_: Optional["DatasetFilter"] = Field(alias="OR", default=None)
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


class OffsetPaginationInput(BaseModel):
    offset: int
    limit: int
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


class FromTraceLikeInput(BaseModel):
    """Input type for creating an image from an array-like object"""

    array: TraceLike
    "The array-like object to create the image from"
    name: str
    "The name of the image"
    dataset: Optional[ID] = None
    "Optional dataset ID to associate the image with"
    tags: Optional[Tuple[str, ...]] = None
    "Optional list of tags to associate with the image"
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


class ROITrace(HasZarrStoreTrait, BaseModel):
    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class ROI(IsVectorizableTrait, BaseModel):
    typename: Literal["ROI"] = Field(alias="__typename", default="ROI", exclude=True)
    id: ID
    trace: ROITrace
    vectors: Tuple[FiveDVector, ...]
    kind: RoiKind
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


class Dataset(BaseModel):
    typename: Literal["Dataset"] = Field(
        alias="__typename", default="Dataset", exclude=True
    )
    name: str
    description: Optional[str] = Field(default=None)
    history: Tuple[HistoryStuff, ...]
    model_config = ConfigDict(frozen=True)


class Trace(HasZarrStoreTrait, BaseModel):
    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    id: ID
    name: str
    "The name of the image"
    store: ZarrStore
    "The store where the image data is stored."
    model_config = ConfigDict(frozen=True)


class FileOrigins(HasZarrStoreTrait, BaseModel):
    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
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


class CreateRoiMutation(BaseModel):
    create_roi: ROI = Field(alias="createRoi")
    "Create a new region of interest"

    class Arguments(BaseModel):
        input: RoiInput

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nmutation CreateRoi($input: RoiInput!) {\n  createRoi(input: $input) {\n    ...ROI\n    __typename\n  }\n}"


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
        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nmutation UpdateRoi($input: UpdateRoiInput!) {\n  updateRoi(input: $input) {\n    ...ROI\n    __typename\n  }\n}"


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


class FromTraceLikeMutation(BaseModel):
    from_trace_like: Trace = Field(alias="fromTraceLike")
    "Create an image from array-like data"

    class Arguments(BaseModel):
        input: FromTraceLikeInput

    class Meta:
        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nmutation FromTraceLike($input: FromTraceLikeInput!) {\n  fromTraceLike(input: $input) {\n    ...Trace\n    __typename\n  }\n}"


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


class GetRoisQuery(BaseModel):
    rois: Tuple[ROI, ...]

    class Arguments(BaseModel):
        image: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nquery GetRois($image: ID!) {\n  rois(filters: {image: $image}) {\n    ...ROI\n    __typename\n  }\n}"


class GetRoiQuery(BaseModel):
    roi: ROI

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nquery GetRoi($id: ID!) {\n  roi(id: $id) {\n    ...ROI\n    __typename\n  }\n}"


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


class GetDatasetQuery(BaseModel):
    dataset: Dataset

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment HistoryStuff on History {\n  id\n  app {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment Dataset on Dataset {\n  name\n  description\n  history {\n    ...HistoryStuff\n    __typename\n  }\n  __typename\n}\n\nquery GetDataset($id: ID!) {\n  dataset(id: $id) {\n    ...Dataset\n    __typename\n  }\n}"


class GetTraceQuery(BaseModel):
    trace: Trace
    "Returns a single image by ID"

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nquery GetTrace($id: ID!) {\n  trace(id: $id) {\n    ...Trace\n    __typename\n  }\n}"


class GetRandomTraceQuery(BaseModel):
    random_trace: Trace = Field(alias="randomTrace")

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nquery GetRandomTrace {\n  randomTrace {\n    ...Trace\n    __typename\n  }\n}"


class SearchTracesQueryOptions(HasZarrStoreTrait, BaseModel):
    typename: Literal["Trace"] = Field(
        alias="__typename", default="Trace", exclude=True
    )
    value: ID
    label: str
    "The name of the image"
    model_config = ConfigDict(frozen=True)


class SearchTracesQuery(BaseModel):
    options: Tuple[SearchTracesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchTraces($search: String, $values: [ID!]) {\n  options: traces(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class ListTracesQuery(BaseModel):
    traces: Tuple[Trace, ...]

    class Arguments(BaseModel):
        filter: Optional[TraceFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nquery ListTraces($filter: TraceFilter, $pagination: OffsetPaginationInput) {\n  traces(filters: $filter, pagination: $pagination) {\n    ...Trace\n    __typename\n  }\n}"


class WatchTracesSubscriptionTraces(BaseModel):
    typename: Literal["TraceEvent"] = Field(
        alias="__typename", default="TraceEvent", exclude=True
    )
    create: Optional[Trace] = Field(default=None)
    delete: Optional[ID] = Field(default=None)
    update: Optional[Trace] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class WatchTracesSubscription(BaseModel):
    traces: WatchTracesSubscriptionTraces
    "Subscribe to real-time image updates"

    class Arguments(BaseModel):
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n  __typename\n}\n\nfragment Trace on Trace {\n  id\n  name\n  store {\n    ...ZarrStore\n    __typename\n  }\n  __typename\n}\n\nsubscription WatchTraces($dataset: ID) {\n  traces(dataset: $dataset) {\n    create {\n      ...Trace\n      __typename\n    }\n    delete\n    update {\n      ...Trace\n      __typename\n    }\n    __typename\n  }\n}"


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
        document = "fragment ROI on ROI {\n  id\n  trace {\n    id\n    __typename\n  }\n  vectors\n  kind\n  __typename\n}\n\nsubscription WatchRois($image: ID!) {\n  rois(image: $image) {\n    create {\n      ...ROI\n      __typename\n    }\n    delete\n    update {\n      ...ROI\n      __typename\n    }\n    __typename\n  }\n}"


async def afrom_file_like(
    name: str,
    file: FileLike,
    origins: Optional[Iterable[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[ElektroRath] = None,
) -> File:
    """from_file_like

    Create a file from file-like data

    Arguments:
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
    origins: Optional[Iterable[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[ElektroRath] = None,
) -> File:
    """from_file_like

    Create a file from file-like data

    Arguments:
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

    Arguments:
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

    Arguments:
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
    store: ID, duration: Optional[int] = None, rath: Optional[ElektroRath] = None
) -> AccessCredentials:
    """RequestFileAccess

    Request credentials to access a file

    Arguments:
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
    store: ID, duration: Optional[int] = None, rath: Optional[ElektroRath] = None
) -> AccessCredentials:
    """RequestFileAccess

    Request credentials to access a file

    Arguments:
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


async def acreate_roi(
    image: ID,
    vectors: Iterable[FiveDVector],
    kind: RoiKind,
    rath: Optional[ElektroRath] = None,
) -> ROI:
    """CreateRoi

    Create a new region of interest

    Arguments:
        image: The image this ROI belongs to
        vectors: The vector coordinates defining the ROI
        kind: The type/kind of ROI
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

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
    rath: Optional[ElektroRath] = None,
) -> ROI:
    """CreateRoi

    Create a new region of interest

    Arguments:
        image: The image this ROI belongs to
        vectors: The vector coordinates defining the ROI
        kind: The type/kind of ROI
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ROI
    """
    return execute(
        CreateRoiMutation,
        {"input": {"image": image, "vectors": vectors, "kind": kind}},
        rath=rath,
    ).create_roi


async def adelete_roi(id: ID, rath: Optional[ElektroRath] = None) -> ID:
    """DeleteRoi

    Delete an existing region of interest

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ID
    """
    return (
        await aexecute(DeleteRoiMutation, {"input": {"id": id}}, rath=rath)
    ).delete_roi


def delete_roi(id: ID, rath: Optional[ElektroRath] = None) -> ID:
    """DeleteRoi

    Delete an existing region of interest

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

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
    rath: Optional[ElektroRath] = None,
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
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

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
    rath: Optional[ElektroRath] = None,
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
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

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


async def acreate_dataset(
    name: str, rath: Optional[ElektroRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset

    Create a new dataset to organize data

    Arguments:
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

    Arguments:
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        CreateDatasetMutationCreatedataset
    """
    return execute(
        CreateDatasetMutation, {"input": {"name": name}}, rath=rath
    ).create_dataset


async def aupdate_dataset(
    name: str, id: ID, rath: Optional[ElektroRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset

    Update dataset metadata

    Arguments:
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
    name: str, id: ID, rath: Optional[ElektroRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset

    Update dataset metadata

    Arguments:
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
    id: ID, history_id: ID, rath: Optional[ElektroRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset

    Revert dataset to a previous version

    Arguments:
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
    id: ID, history_id: ID, rath: Optional[ElektroRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset

    Revert dataset to a previous version

    Arguments:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        history_id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        RevertDatasetMutationRevertdataset
    """
    return execute(
        RevertDatasetMutation, {"input": {"id": id, "historyId": history_id}}, rath=rath
    ).revert_dataset


async def afrom_trace_like(
    array: TraceLike,
    name: str,
    dataset: Optional[ID] = None,
    tags: Optional[Iterable[str]] = None,
    rath: Optional[ElektroRath] = None,
) -> Trace:
    """FromTraceLike

    Create an image from array-like data

    Arguments:
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
    array: TraceLike,
    name: str,
    dataset: Optional[ID] = None,
    tags: Optional[Iterable[str]] = None,
    rath: Optional[ElektroRath] = None,
) -> Trace:
    """FromTraceLike

    Create an image from array-like data

    Arguments:
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

    Arguments:
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

    Arguments:
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
    store: ID, duration: Optional[int] = None, rath: Optional[ElektroRath] = None
) -> AccessCredentials:
    """RequestAccess

    Request credentials to access an image

    Arguments:
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
    store: ID, duration: Optional[int] = None, rath: Optional[ElektroRath] = None
) -> AccessCredentials:
    """RequestAccess

    Request credentials to access an image

    Arguments:
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


async def aget_file(id: ID, rath: Optional[ElektroRath] = None) -> File:
    """GetFile


    Arguments:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        File
    """
    return (await aexecute(GetFileQuery, {"id": id}, rath=rath)).file


def get_file(id: ID, rath: Optional[ElektroRath] = None) -> File:
    """GetFile


    Arguments:
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
) -> Tuple[SearchFilesQueryOptions, ...]:
    """SearchFiles


    Arguments:
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
) -> Tuple[SearchFilesQueryOptions, ...]:
    """SearchFiles


    Arguments:
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


async def aget_rois(image: ID, rath: Optional[ElektroRath] = None) -> Tuple[ROI, ...]:
    """GetRois


    Arguments:
        image (ID): No description
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[ROI]
    """
    return (await aexecute(GetRoisQuery, {"image": image}, rath=rath)).rois


def get_rois(image: ID, rath: Optional[ElektroRath] = None) -> Tuple[ROI, ...]:
    """GetRois


    Arguments:
        image (ID): No description
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[ROI]
    """
    return execute(GetRoisQuery, {"image": image}, rath=rath).rois


async def aget_roi(id: ID, rath: Optional[ElektroRath] = None) -> ROI:
    """GetRoi


    Arguments:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        ROI
    """
    return (await aexecute(GetRoiQuery, {"id": id}, rath=rath)).roi


def get_roi(id: ID, rath: Optional[ElektroRath] = None) -> ROI:
    """GetRoi


    Arguments:
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
) -> Tuple[SearchRoisQueryOptions, ...]:
    """SearchRois


    Arguments:
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
) -> Tuple[SearchRoisQueryOptions, ...]:
    """SearchRois


    Arguments:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[SearchRoisQueryRois]
    """
    return execute(
        SearchRoisQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_dataset(id: ID, rath: Optional[ElektroRath] = None) -> Dataset:
    """GetDataset


    Arguments:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Dataset
    """
    return (await aexecute(GetDatasetQuery, {"id": id}, rath=rath)).dataset


def get_dataset(id: ID, rath: Optional[ElektroRath] = None) -> Dataset:
    """GetDataset


    Arguments:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Dataset
    """
    return execute(GetDatasetQuery, {"id": id}, rath=rath).dataset


async def aget_trace(id: ID, rath: Optional[ElektroRath] = None) -> Trace:
    """GetTrace

    Returns a single image by ID

    Arguments:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return (await aexecute(GetTraceQuery, {"id": id}, rath=rath)).trace


def get_trace(id: ID, rath: Optional[ElektroRath] = None) -> Trace:
    """GetTrace

    Returns a single image by ID

    Arguments:
        id (ID): The unique identifier of an object
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return execute(GetTraceQuery, {"id": id}, rath=rath).trace


async def aget_random_trace(rath: Optional[ElektroRath] = None) -> Trace:
    """GetRandomTrace


    Arguments:
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return (await aexecute(GetRandomTraceQuery, {}, rath=rath)).random_trace


def get_random_trace(rath: Optional[ElektroRath] = None) -> Trace:
    """GetRandomTrace


    Arguments:
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        Trace
    """
    return execute(GetRandomTraceQuery, {}, rath=rath).random_trace


async def asearch_traces(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[ElektroRath] = None,
) -> Tuple[SearchTracesQueryOptions, ...]:
    """SearchTraces


    Arguments:
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
) -> Tuple[SearchTracesQueryOptions, ...]:
    """SearchTraces


    Arguments:
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
) -> Tuple[Trace, ...]:
    """ListTraces


    Arguments:
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
) -> Tuple[Trace, ...]:
    """ListTraces


    Arguments:
        filter (Optional[TraceFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        List[Trace]
    """
    return execute(
        ListTracesQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).traces


async def awatch_traces(
    dataset: Optional[ID] = None, rath: Optional[ElektroRath] = None
) -> AsyncIterator[WatchTracesSubscriptionTraces]:
    """WatchTraces

    Subscribe to real-time image updates

    Arguments:
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

    Arguments:
        dataset (Optional[ID], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchTracesSubscriptionTraces
    """
    for event in subscribe(WatchTracesSubscription, {"dataset": dataset}, rath=rath):
        yield event.traces


async def awatch_files(
    dataset: Optional[ID] = None, rath: Optional[ElektroRath] = None
) -> AsyncIterator[WatchFilesSubscriptionFiles]:
    """WatchFiles

    Subscribe to real-time file updates

    Arguments:
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

    Arguments:
        dataset (Optional[ID], optional): No description.
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchFilesSubscriptionFiles
    """
    for event in subscribe(WatchFilesSubscription, {"dataset": dataset}, rath=rath):
        yield event.files


async def awatch_rois(
    image: ID, rath: Optional[ElektroRath] = None
) -> AsyncIterator[WatchRoisSubscriptionRois]:
    """WatchRois

    Subscribe to real-time ROI updates

    Arguments:
        image (ID): No description
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchRoisSubscriptionRois
    """
    async for event in asubscribe(WatchRoisSubscription, {"image": image}, rath=rath):
        yield event.rois


def watch_rois(
    image: ID, rath: Optional[ElektroRath] = None
) -> Iterator[WatchRoisSubscriptionRois]:
    """WatchRois

    Subscribe to real-time ROI updates

    Arguments:
        image (ID): No description
        rath (elektro.rath.ElektroRath, optional): The elektro rath client

    Returns:
        WatchRoisSubscriptionRois
    """
    for event in subscribe(WatchRoisSubscription, {"image": image}, rath=rath):
        yield event.rois


DatasetFilter.model_rebuild()
ProvenanceFilter.model_rebuild()
TraceFilter.model_rebuild()

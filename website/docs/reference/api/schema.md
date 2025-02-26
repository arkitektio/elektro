---
sidebar_label: schema
title: api.schema
---

## OmeroFileType Objects

```python
class OmeroFileType(str, Enum)
```

An enumeration.

#### TIFF

Tiff

#### JPEG

Jpeg

#### MSR

MSR File

#### CZI

Zeiss Microscopy File

#### UNKNOWN

Unwknon File Format

## RepresentationVariety Objects

```python
class RepresentationVariety(str, Enum)
```

An enumeration.

#### MASK

Mask (Value represent Labels)

#### VOXEL

Voxel (Value represent Intensity)

#### RGB

RGB (First three channel represent RGB)

#### UNKNOWN

Unknown

## RepresentationVarietyInput Objects

```python
class RepresentationVarietyInput(str, Enum)
```

Variety expresses the Type of Representation we are dealing with

#### MASK

Mask (Value represent Labels)

#### VOXEL

Voxel (Value represent Intensity)

#### RGB

RGB (First three channel represent RGB)

#### UNKNOWN

Unknown

## ROIType Objects

```python
class ROIType(str, Enum)
```

An enumeration.

#### ELLIPSE

Ellipse

#### POLYGON

POLYGON

#### LINE

Line

#### RECTANGLE

Rectangle

#### PATH

Path

#### UNKNOWN

Unknown

## RoiTypeInput Objects

```python
class RoiTypeInput(str, Enum)
```

An enumeration.

#### ELLIPSIS

Ellipse

#### POLYGON

POLYGON

#### LINE

Line

#### RECTANGLE

Rectangle

#### PATH

Path

#### UNKNOWN

Unknown

## InputVector Objects

```python
class InputVector(BaseModel, Vectorizable)
```

#### x

X-coordinate

#### y

Y-coordinate

#### z

Z-coordinate

## RepresentationFragmentSample Objects

```python
class RepresentationFragmentSample(Sample, BaseModel)
```

Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure),
was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of
the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample

## RepresentationFragment Objects

```python
class RepresentationFragment(Representation, BaseModel)
```

#### sample

The Sample this representation belongs to

#### type

The Representation can have varying types, consult your API

#### variety

The Representation can have varying types, consult your API

#### name

Cleartext name

## ROIFragmentVectors Objects

```python
class ROIFragmentVectors(BaseModel)
```

#### x

X-coordinate

#### y

Y-coordinate

#### z

Z-coordinate

## ROIFragmentRepresentation Objects

```python
class ROIFragmentRepresentation(Representation, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants

@elements/rep:latest

## ROIFragmentCreator Objects

```python
class ROIFragmentCreator(BaseModel)
```

A reflection on the real User

#### color

The associated color for this user

## ROIFragment Objects

```python
class ROIFragment(ROI, BaseModel)
```

#### type

The Representation can have varying types, consult your API

## TableFragmentCreator Objects

```python
class TableFragmentCreator(BaseModel)
```

A reflection on the real User

## TableFragmentSample Objects

```python
class TableFragmentSample(Sample, BaseModel)
```

Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure),
was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of
the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample

## TableFragmentRepresentation Objects

```python
class TableFragmentRepresentation(Representation, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants

@elements/rep:latest

## TableFragmentExperiment Objects

```python
class TableFragmentExperiment(Experiment, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants @elements/experiment

## TableFragment Objects

```python
class TableFragment(Table, BaseModel)
```

#### tags

A comma-separated list of tags.

#### store

The location of the Parquet on the Storage System (S3 or Media-URL)

## SampleFragmentRepresentations Objects

```python
class SampleFragmentRepresentations(Representation, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants

@elements/rep:latest

## SampleFragmentExperiments Objects

```python
class SampleFragmentExperiments(Experiment, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants @elements/experiment

## ExperimentFragmentCreator Objects

```python
class ExperimentFragmentCreator(BaseModel)
```

A reflection on the real User

## Get_omero_fileQuery Objects

```python
class Get_omero_fileQuery(BaseModel)
```

#### omerofile

Get a single representation by ID

## Expand_omerofileQuery Objects

```python
class Expand_omerofileQuery(BaseModel)
```

#### omerofile

Get a single representation by ID

## Search_omerofileQuery Objects

```python
class Search_omerofileQuery(BaseModel)
```

#### omerofiles

My samples return all of the users samples attached to the current user

## Expand_representationQuery Objects

```python
class Expand_representationQuery(BaseModel)
```

#### representation

Get a single representation by ID

## Get_representationQuery Objects

```python
class Get_representationQuery(BaseModel)
```

#### representation

Get a single representation by ID

## Search_representationQueryRepresentations Objects

```python
class Search_representationQueryRepresentations(Representation, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants

@elements/rep:latest

#### label

Cleartext name

## Search_representationQuery Objects

```python
class Search_representationQuery(BaseModel)
```

#### representations

All represetations

## Get_random_repQuery Objects

```python
class Get_random_repQuery(BaseModel)
```

#### random_representation

Get a single representation by ID

## ThumbnailQuery Objects

```python
class ThumbnailQuery(BaseModel)
```

#### thumbnail

Get a single representation by ID

## Expand_thumbnailQuery Objects

```python
class Expand_thumbnailQuery(BaseModel)
```

#### thumbnail

Get a single representation by ID

## Get_roisQuery Objects

```python
class Get_roisQuery(BaseModel)
```

#### rois

All represetations

## TableQuery Objects

```python
class TableQuery(BaseModel)
```

#### table

Get a single representation by ID

## Expand_tableQuery Objects

```python
class Expand_tableQuery(BaseModel)
```

#### table

Get a single representation by ID

## Search_tablesQuery Objects

```python
class Search_tablesQuery(BaseModel)
```

#### tables

My samples return all of the users samples attached to the current user

## Get_sampleQuery Objects

```python
class Get_sampleQuery(BaseModel)
```

#### sample

Get a single representation by ID

## Search_sampleQuerySamples Objects

```python
class Search_sampleQuerySamples(Sample, BaseModel)
```

Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure),
was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of
the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample

## Search_sampleQuery Objects

```python
class Search_sampleQuery(BaseModel)
```

#### samples

All Samples

## Expand_sampleQuery Objects

```python
class Expand_sampleQuery(BaseModel)
```

#### sample

Get a single representation by ID

## Get_experimentQuery Objects

```python
class Get_experimentQuery(BaseModel)
```

#### experiment

Get a single representation by ID

## Expand_experimentQuery Objects

```python
class Expand_experimentQuery(BaseModel)
```

#### experiment

Get a single representation by ID

## Search_experimentQueryExperiments Objects

```python
class Search_experimentQueryExperiments(Experiment, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants @elements/experiment

## Search_experimentQuery Objects

```python
class Search_experimentQuery(BaseModel)
```

#### experiments

All Samples

## Watch_samplesSubscriptionMysamplesUpdateExperiments Objects

```python
class Watch_samplesSubscriptionMysamplesUpdateExperiments(Experiment, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants @elements/experiment

## Watch_samplesSubscriptionMysamplesUpdate Objects

```python
class Watch_samplesSubscriptionMysamplesUpdate(Sample, BaseModel)
```

Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure),
was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of
the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample

## Watch_samplesSubscriptionMysamplesCreateExperiments Objects

```python
class Watch_samplesSubscriptionMysamplesCreateExperiments(Experiment, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants @elements/experiment

## Watch_samplesSubscriptionMysamplesCreate Objects

```python
class Watch_samplesSubscriptionMysamplesCreate(Sample, BaseModel)
```

Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure),
was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of
the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample

## Create_size_featureMutationCreatesizefeatureLabelRepresentation Objects

```python
class Create_size_featureMutationCreatesizefeatureLabelRepresentation(Representation, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants

@elements/rep:latest

## Create_size_featureMutation Objects

```python
class Create_size_featureMutation(BaseModel)
```

#### create_size_feature

Creates a Sample

## Create_labelMutation Objects

```python
class Create_labelMutation(BaseModel)
```

#### create_label

Creates a Sample

## From_xarrayMutation Objects

```python
class From_xarrayMutation(BaseModel)
```

#### from_x_array

Creates a Representation

## Double_uploadMutationX Objects

```python
class Double_uploadMutationX(Representation, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants

@elements/rep:latest

## Double_uploadMutationY Objects

```python
class Double_uploadMutationY(Representation, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants

@elements/rep:latest

## Double_uploadMutation Objects

```python
class Double_uploadMutation(BaseModel)
```

#### x

Creates a Representation

#### y

Creates a Representation

## Create_metricMutationCreatemetricRep Objects

```python
class Create_metricMutationCreatemetricRep(Representation, BaseModel)
```

A Representation is a multi-dimensional Array that can do what ever it wants

@elements/rep:latest

## Create_metricMutationCreatemetricCreator Objects

```python
class Create_metricMutationCreatemetricCreator(BaseModel)
```

A reflection on the real User

## Create_metricMutationCreatemetric Objects

```python
class Create_metricMutationCreatemetric(BaseModel)
```

#### rep

The Representatoin this Metric belongs to

#### key

The Key

## Create_metricMutation Objects

```python
class Create_metricMutation(BaseModel)
```

#### create_metric

Creates a Representation

## Create_roiMutation Objects

```python
class Create_roiMutation(BaseModel)
```

#### create_roi

Creates a Sample

## From_dfMutation Objects

```python
class From_dfMutation(BaseModel)
```

#### from_df

Creates a Representation

## Create_sampleMutationCreatesampleCreator Objects

```python
class Create_sampleMutationCreatesampleCreator(BaseModel)
```

A reflection on the real User

## Create_sampleMutationCreatesample Objects

```python
class Create_sampleMutationCreatesample(Sample, BaseModel)
```

Samples are storage containers for representations. A Sample is to be understood analogous to a Biological Sample. It existed in Time (the time of acquisiton and experimental procedure),
was measured in space (x,y,z) and in different modalities (c). Sample therefore provide a datacontainer where each Representation of
the data shares the same dimensions. Every transaction to our image data is still part of the original acuqistion, so also filtered images are refering back to the sample

## Create_sampleMutation Objects

```python
class Create_sampleMutation(BaseModel)
```

#### create_sample

Creates a Sample\n

## Create_experimentMutation Objects

```python
class Create_experimentMutation(BaseModel)
```

#### create_experiment

Create an experiment (only signed in users)

#### aget_omero_file

```python
async def aget_omero_file(id: Optional[ID], rath: MikroRath = None) -> OmeroFileFragment
```

get_omero_file

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

OmeroFileFragment

#### get_omero_file

```python
def get_omero_file(id: Optional[ID], rath: MikroRath = None) -> OmeroFileFragment
```

get_omero_file

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

OmeroFileFragment

#### aexpand_omerofile

```python
async def aexpand_omerofile(id: Optional[ID], rath: MikroRath = None) -> OmeroFileFragment
```

expand_omerofile

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

OmeroFileFragment

#### expand_omerofile

```python
def expand_omerofile(id: Optional[ID], rath: MikroRath = None) -> OmeroFileFragment
```

expand_omerofile

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

OmeroFileFragment

#### asearch_omerofile

```python
async def asearch_omerofile(search: Optional[str], rath: MikroRath = None) -> Optional[List[Optional[Search_omerofileQueryOmerofiles]]]
```

search_omerofile

omerofiles: My samples return all of the users samples attached to the current user

**Arguments**:

- `search` _str_ - search
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_omerofileQuery

#### search_omerofile

```python
def search_omerofile(search: Optional[str], rath: MikroRath = None) -> Optional[List[Optional[Search_omerofileQueryOmerofiles]]]
```

search_omerofile

omerofiles: My samples return all of the users samples attached to the current user

**Arguments**:

- `search` _str_ - search
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_omerofileQuery

#### aexpand_representation

```python
async def aexpand_representation(id: Optional[ID], rath: MikroRath = None) -> RepresentationFragment
```

expand_representation

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

RepresentationFragment

#### expand_representation

```python
def expand_representation(id: Optional[ID], rath: MikroRath = None) -> RepresentationFragment
```

expand_representation

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

RepresentationFragment

#### aget_representation

```python
async def aget_representation(id: Optional[ID], rath: MikroRath = None) -> RepresentationFragment
```

get_representation

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

RepresentationFragment

#### get_representation

```python
def get_representation(id: Optional[ID], rath: MikroRath = None) -> RepresentationFragment
```

get_representation

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

RepresentationFragment

#### asearch_representation

```python
async def asearch_representation(search: Optional[str] = None, rath: MikroRath = None) -> Optional[List[Optional[Search_representationQueryRepresentations]]]
```

search_representation

representations: All represetations

**Arguments**:

- `search` _Optional[str], optional_ - search.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_representationQuery

#### search_representation

```python
def search_representation(search: Optional[str] = None, rath: MikroRath = None) -> Optional[List[Optional[Search_representationQueryRepresentations]]]
```

search_representation

representations: All represetations

**Arguments**:

- `search` _Optional[str], optional_ - search.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_representationQuery

#### aget_random_rep

```python
async def aget_random_rep(rath: MikroRath = None) -> RepresentationFragment
```

get_random_rep

Get a single representation by ID

**Arguments**:

- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

RepresentationFragment

#### get_random_rep

```python
def get_random_rep(rath: MikroRath = None) -> RepresentationFragment
```

get_random_rep

Get a single representation by ID

**Arguments**:

- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

RepresentationFragment

#### athumbnail

```python
async def athumbnail(id: Optional[ID], rath: MikroRath = None) -> ThumbnailFragment
```

Thumbnail

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ThumbnailFragment

#### thumbnail

```python
def thumbnail(id: Optional[ID], rath: MikroRath = None) -> ThumbnailFragment
```

Thumbnail

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ThumbnailFragment

#### aexpand_thumbnail

```python
async def aexpand_thumbnail(id: Optional[ID], rath: MikroRath = None) -> ThumbnailFragment
```

expand_thumbnail

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ThumbnailFragment

#### expand_thumbnail

```python
def expand_thumbnail(id: Optional[ID], rath: MikroRath = None) -> ThumbnailFragment
```

expand_thumbnail

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ThumbnailFragment

#### aget_rois

```python
async def aget_rois(representation: Optional[ID], type: Optional[List[Optional[RoiTypeInput]]] = None, rath: MikroRath = None) -> ROIFragment
```

get_rois

All represetations

**Arguments**:

- `representation` _ID_ - representation
- `type` _Optional[List[Optional[RoiTypeInput]]], optional_ - type.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ROIFragment

#### get_rois

```python
def get_rois(representation: Optional[ID], type: Optional[List[Optional[RoiTypeInput]]] = None, rath: MikroRath = None) -> ROIFragment
```

get_rois

All represetations

**Arguments**:

- `representation` _ID_ - representation
- `type` _Optional[List[Optional[RoiTypeInput]]], optional_ - type.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ROIFragment

#### atable

```python
async def atable(id: Optional[ID], rath: MikroRath = None) -> TableFragment
```

Table

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

TableFragment

#### table

```python
def table(id: Optional[ID], rath: MikroRath = None) -> TableFragment
```

Table

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

TableFragment

#### aexpand_table

```python
async def aexpand_table(id: Optional[ID], rath: MikroRath = None) -> TableFragment
```

expand_table

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

TableFragment

#### expand_table

```python
def expand_table(id: Optional[ID], rath: MikroRath = None) -> TableFragment
```

expand_table

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

TableFragment

#### asearch_tables

```python
async def asearch_tables(rath: MikroRath = None) -> Optional[List[Optional[Search_tablesQueryTables]]]
```

search_tables

tables: My samples return all of the users samples attached to the current user

**Arguments**:

- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_tablesQuery

#### search_tables

```python
def search_tables(rath: MikroRath = None) -> Optional[List[Optional[Search_tablesQueryTables]]]
```

search_tables

tables: My samples return all of the users samples attached to the current user

**Arguments**:

- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_tablesQuery

#### aget_sample

```python
async def aget_sample(id: Optional[ID], rath: MikroRath = None) -> SampleFragment
```

get_sample

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

SampleFragment

#### get_sample

```python
def get_sample(id: Optional[ID], rath: MikroRath = None) -> SampleFragment
```

get_sample

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

SampleFragment

#### asearch_sample

```python
async def asearch_sample(search: Optional[str] = None, rath: MikroRath = None) -> Optional[List[Optional[Search_sampleQuerySamples]]]
```

search_sample

samples: All Samples

**Arguments**:

- `search` _Optional[str], optional_ - search.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_sampleQuery

#### search_sample

```python
def search_sample(search: Optional[str] = None, rath: MikroRath = None) -> Optional[List[Optional[Search_sampleQuerySamples]]]
```

search_sample

samples: All Samples

**Arguments**:

- `search` _Optional[str], optional_ - search.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_sampleQuery

#### aexpand_sample

```python
async def aexpand_sample(id: Optional[ID], rath: MikroRath = None) -> SampleFragment
```

expand_sample

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

SampleFragment

#### expand_sample

```python
def expand_sample(id: Optional[ID], rath: MikroRath = None) -> SampleFragment
```

expand_sample

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

SampleFragment

#### aget_experiment

```python
async def aget_experiment(id: Optional[ID], rath: MikroRath = None) -> ExperimentFragment
```

get_experiment

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ExperimentFragment

#### get_experiment

```python
def get_experiment(id: Optional[ID], rath: MikroRath = None) -> ExperimentFragment
```

get_experiment

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ExperimentFragment

#### aexpand_experiment

```python
async def aexpand_experiment(id: Optional[ID], rath: MikroRath = None) -> ExperimentFragment
```

expand_experiment

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ExperimentFragment

#### expand_experiment

```python
def expand_experiment(id: Optional[ID], rath: MikroRath = None) -> ExperimentFragment
```

expand_experiment

Get a single representation by ID

**Arguments**:

- `id` _ID_ - id
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ExperimentFragment

#### asearch_experiment

```python
async def asearch_experiment(search: Optional[str] = None, rath: MikroRath = None) -> Optional[List[Optional[Search_experimentQueryExperiments]]]
```

search_experiment

experiments: All Samples

**Arguments**:

- `search` _Optional[str], optional_ - search.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_experimentQuery

#### search_experiment

```python
def search_experiment(search: Optional[str] = None, rath: MikroRath = None) -> Optional[List[Optional[Search_experimentQueryExperiments]]]
```

search_experiment

experiments: All Samples

**Arguments**:

- `search` _Optional[str], optional_ - search.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Search_experimentQuery

#### awatch_rois

```python
async def awatch_rois(representation: Optional[ID], rath: MikroRath = None) -> AsyncIterator[Optional[Watch_roisSubscriptionRois]]
```

watch_rois

**Arguments**:

- `representation` _ID_ - representation
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Watch_roisSubscription

#### watch_rois

```python
def watch_rois(representation: Optional[ID], rath: MikroRath = None) -> Iterator[Optional[Watch_roisSubscriptionRois]]
```

watch_rois

**Arguments**:

- `representation` _ID_ - representation
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Watch_roisSubscription

#### awatch_samples

```python
async def awatch_samples(rath: MikroRath = None) -> AsyncIterator[Optional[Watch_samplesSubscriptionMysamples]]
```

watch_samples

**Arguments**:

- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Watch_samplesSubscription

#### watch_samples

```python
def watch_samples(rath: MikroRath = None) -> Iterator[Optional[Watch_samplesSubscriptionMysamples]]
```

watch_samples

**Arguments**:

- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Watch_samplesSubscription

#### anegotiate

```python
async def anegotiate(rath: MikroRath = None) -> Optional[Dict]
```

negotiate

**Arguments**:

- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Optional[Dict]

#### negotiate

```python
def negotiate(rath: MikroRath = None) -> Optional[Dict]
```

negotiate

**Arguments**:

- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Optional[Dict]

#### aupload_bioimage

```python
async def aupload_bioimage(file: Optional[Upload], rath: MikroRath = None) -> Optional[Upload_bioimageMutationUploadomerofile]
```

upload_bioimage

**Arguments**:

- `file` _Upload_ - file
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Upload_bioimageMutation

#### upload_bioimage

```python
def upload_bioimage(file: Optional[Upload], rath: MikroRath = None) -> Optional[Upload_bioimageMutationUploadomerofile]
```

upload_bioimage

**Arguments**:

- `file` _Upload_ - file
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Upload_bioimageMutation

#### acreate_size_feature

```python
async def acreate_size_feature(label: Optional[ID], size: Optional[float], creator: Optional[ID] = None, rath: MikroRath = None) -> Optional[Create_size_featureMutationCreatesizefeature]
```

create_size_feature

createSizeFeature: Creates a Sample

**Arguments**:

- `label` _ID_ - label
- `size` _float_ - size
- `creator` _Optional[ID], optional_ - creator.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Create_size_featureMutation

#### create_size_feature

```python
def create_size_feature(label: Optional[ID], size: Optional[float], creator: Optional[ID] = None, rath: MikroRath = None) -> Optional[Create_size_featureMutationCreatesizefeature]
```

create_size_feature

createSizeFeature: Creates a Sample

**Arguments**:

- `label` _ID_ - label
- `size` _float_ - size
- `creator` _Optional[ID], optional_ - creator.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Create_size_featureMutation

#### acreate_label

```python
async def acreate_label(instance: Optional[int], representation: Optional[ID], creator: Optional[ID], name: Optional[str] = None, rath: MikroRath = None) -> Optional[Create_labelMutationCreatelabel]
```

create_label

createLabel: Creates a Sample

**Arguments**:

- `instance` _int_ - instance
- `representation` _ID_ - representation
- `creator` _ID_ - creator
- `name` _Optional[str], optional_ - name.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Create_labelMutation

#### create_label

```python
def create_label(instance: Optional[int], representation: Optional[ID], creator: Optional[ID], name: Optional[str] = None, rath: MikroRath = None) -> Optional[Create_labelMutationCreatelabel]
```

create_label

createLabel: Creates a Sample

**Arguments**:

- `instance` _int_ - instance
- `representation` _ID_ - representation
- `creator` _ID_ - creator
- `name` _Optional[str], optional_ - name.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Create_labelMutation

#### afrom_xarray

```python
async def afrom_xarray(xarray: Optional[XArray], name: Optional[str] = None, variety: Optional[RepresentationVarietyInput] = None, origins: Optional[List[Optional[ID]]] = None, tags: Optional[List[Optional[str]]] = None, sample: Optional[ID] = None, omero: Optional[OmeroRepresentationInput] = None, rath: MikroRath = None) -> RepresentationFragment
```

from_xarray

Creates a Representation

**Arguments**:

- `xarray` _XArray_ - xarray
- `name` _Optional[str], optional_ - name.
- `variety` _Optional[RepresentationVarietyInput], optional_ - variety.
- `origins` _Optional[List[Optional[ID]]], optional_ - origins.
- `tags` _Optional[List[Optional[str]]], optional_ - tags.
- `sample` _Optional[ID], optional_ - sample.
- `omero` _Optional[OmeroRepresentationInput], optional_ - omero.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

RepresentationFragment

#### from_xarray

```python
def from_xarray(xarray: Optional[XArray], name: Optional[str] = None, variety: Optional[RepresentationVarietyInput] = None, origins: Optional[List[Optional[ID]]] = None, tags: Optional[List[Optional[str]]] = None, sample: Optional[ID] = None, omero: Optional[OmeroRepresentationInput] = None, rath: MikroRath = None) -> RepresentationFragment
```

from_xarray

Creates a Representation

**Arguments**:

- `xarray` _XArray_ - xarray
- `name` _Optional[str], optional_ - name.
- `variety` _Optional[RepresentationVarietyInput], optional_ - variety.
- `origins` _Optional[List[Optional[ID]]], optional_ - origins.
- `tags` _Optional[List[Optional[str]]], optional_ - tags.
- `sample` _Optional[ID], optional_ - sample.
- `omero` _Optional[OmeroRepresentationInput], optional_ - omero.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

RepresentationFragment

#### adouble_upload

```python
async def adouble_upload(xarray: Optional[XArray], name: Optional[str] = None, origins: Optional[List[Optional[ID]]] = None, tags: Optional[List[Optional[str]]] = None, sample: Optional[ID] = None, omero: Optional[OmeroRepresentationInput] = None, rath: MikroRath = None) -> Double_uploadMutation
```

double_upload

x: Creates a Representation
y: Creates a Representation

**Arguments**:

- `xarray` _XArray_ - xarray
- `name` _Optional[str], optional_ - name.
- `origins` _Optional[List[Optional[ID]]], optional_ - origins.
- `tags` _Optional[List[Optional[str]]], optional_ - tags.
- `sample` _Optional[ID], optional_ - sample.
- `omero` _Optional[OmeroRepresentationInput], optional_ - omero.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Double_uploadMutation

#### double_upload

```python
def double_upload(xarray: Optional[XArray], name: Optional[str] = None, origins: Optional[List[Optional[ID]]] = None, tags: Optional[List[Optional[str]]] = None, sample: Optional[ID] = None, omero: Optional[OmeroRepresentationInput] = None, rath: MikroRath = None) -> Double_uploadMutation
```

double_upload

x: Creates a Representation
y: Creates a Representation

**Arguments**:

- `xarray` _XArray_ - xarray
- `name` _Optional[str], optional_ - name.
- `origins` _Optional[List[Optional[ID]]], optional_ - origins.
- `tags` _Optional[List[Optional[str]]], optional_ - tags.
- `sample` _Optional[ID], optional_ - sample.
- `omero` _Optional[OmeroRepresentationInput], optional_ - omero.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Double_uploadMutation

#### acreate_thumbnail

```python
async def acreate_thumbnail(rep: Optional[ID], file: Optional[File], rath: MikroRath = None) -> ThumbnailFragment
```

create_thumbnail

**Arguments**:

- `rep` _ID_ - rep
- `file` _File_ - file
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ThumbnailFragment

#### create_thumbnail

```python
def create_thumbnail(rep: Optional[ID], file: Optional[File], rath: MikroRath = None) -> ThumbnailFragment
```

create_thumbnail

**Arguments**:

- `rep` _ID_ - rep
- `file` _File_ - file
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ThumbnailFragment

#### acreate_metric

```python
async def acreate_metric(key: Optional[str], value: Optional[Dict], rep: Optional[ID] = None, sample: Optional[ID] = None, experiment: Optional[ID] = None, rath: MikroRath = None) -> Optional[Create_metricMutationCreatemetric]
```

create_metric

createMetric: Creates a Representation

**Arguments**:

- `key` _str_ - key
- `value` _Dict_ - value
- `rep` _Optional[ID], optional_ - rep.
- `sample` _Optional[ID], optional_ - sample.
- `experiment` _Optional[ID], optional_ - experiment.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Create_metricMutation

#### create_metric

```python
def create_metric(key: Optional[str], value: Optional[Dict], rep: Optional[ID] = None, sample: Optional[ID] = None, experiment: Optional[ID] = None, rath: MikroRath = None) -> Optional[Create_metricMutationCreatemetric]
```

create_metric

createMetric: Creates a Representation

**Arguments**:

- `key` _str_ - key
- `value` _Dict_ - value
- `rep` _Optional[ID], optional_ - rep.
- `sample` _Optional[ID], optional_ - sample.
- `experiment` _Optional[ID], optional_ - experiment.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Create_metricMutation

#### acreate_roi

```python
async def acreate_roi(representation: Optional[ID], vectors: Optional[List[Optional[InputVector]]], type: Optional[RoiTypeInput], creator: Optional[ID] = None, rath: MikroRath = None) -> ROIFragment
```

create_roi

Creates a Sample

**Arguments**:

- `representation` _ID_ - representation
- `vectors` _List[Optional[InputVector]]_ - vectors
- `type` _RoiTypeInput_ - type
- `creator` _Optional[ID], optional_ - creator.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ROIFragment

#### create_roi

```python
def create_roi(representation: Optional[ID], vectors: Optional[List[Optional[InputVector]]], type: Optional[RoiTypeInput], creator: Optional[ID] = None, rath: MikroRath = None) -> ROIFragment
```

create_roi

Creates a Sample

**Arguments**:

- `representation` _ID_ - representation
- `vectors` _List[Optional[InputVector]]_ - vectors
- `type` _RoiTypeInput_ - type
- `creator` _Optional[ID], optional_ - creator.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ROIFragment

#### afrom_df

```python
async def afrom_df(df: Optional[DataFrame], rath: MikroRath = None) -> TableFragment
```

from_df

Creates a Representation

**Arguments**:

- `df` _DataFrame_ - df
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

TableFragment

#### from_df

```python
def from_df(df: Optional[DataFrame], rath: MikroRath = None) -> TableFragment
```

from_df

Creates a Representation

**Arguments**:

- `df` _DataFrame_ - df
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

TableFragment

#### acreate_sample

```python
async def acreate_sample(name: Optional[str] = None, creator: Optional[str] = None, meta: Optional[Dict] = None, experiments: Optional[List[Optional[ID]]] = None, rath: MikroRath = None) -> Optional[Create_sampleMutationCreatesample]
```

create_sample

createSample: Creates a Sample

**Arguments**:

- `name` _Optional[str], optional_ - name.
- `creator` _Optional[str], optional_ - creator.
- `meta` _Optional[Dict], optional_ - meta.
- `experiments` _Optional[List[Optional[ID]]], optional_ - experiments.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Create_sampleMutation

#### create_sample

```python
def create_sample(name: Optional[str] = None, creator: Optional[str] = None, meta: Optional[Dict] = None, experiments: Optional[List[Optional[ID]]] = None, rath: MikroRath = None) -> Optional[Create_sampleMutationCreatesample]
```

create_sample

createSample: Creates a Sample

**Arguments**:

- `name` _Optional[str], optional_ - name.
- `creator` _Optional[str], optional_ - creator.
- `meta` _Optional[Dict], optional_ - meta.
- `experiments` _Optional[List[Optional[ID]]], optional_ - experiments.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

Create_sampleMutation

#### acreate_experiment

```python
async def acreate_experiment(name: Optional[str], creator: Optional[str] = None, meta: Optional[Dict] = None, description: Optional[str] = None, rath: MikroRath = None) -> ExperimentFragment
```

create_experiment

Create an experiment (only signed in users)

**Arguments**:

- `name` _str_ - name
- `creator` _Optional[str], optional_ - creator.
- `meta` _Optional[Dict], optional_ - meta.
- `description` _Optional[str], optional_ - description.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ExperimentFragment

#### create_experiment

```python
def create_experiment(name: Optional[str], creator: Optional[str] = None, meta: Optional[Dict] = None, description: Optional[str] = None, rath: MikroRath = None) -> ExperimentFragment
```

create_experiment

Create an experiment (only signed in users)

**Arguments**:

- `name` _str_ - name
- `creator` _Optional[str], optional_ - creator.
- `meta` _Optional[Dict], optional_ - meta.
- `description` _Optional[str], optional_ - description.
- `rath` _mikro_nextrath.MikroRath, optional_ - The mikro rath client

**Returns**:

ExperimentFragment

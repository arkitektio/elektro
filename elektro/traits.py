"""
Traits for elektro

Traits are mixins that are added to every graphql type that exists on the mikro schema.
We use them to add functionality to the graphql types that extend from the base type.

Every GraphQL Model on Mikro gets a identifier and shrinking methods to ensure the compatibliity
with arkitekt. This is done by adding the identifier and the shrinking methods to the graphql type.
If you want to add your own traits to the graphql type, you can do so by adding them in the graphql
.config.yaml file.

"""

from typing import Awaitable, List, TypeVar, Protocol, Optional, cast
import pandas as pd
from pydantic import BaseModel
import xarray as xr
from typing import TYPE_CHECKING
from dask.array import from_zarr  # type: ignore
import zarr
from typing import Any
from rath.turms.utils import get_attributes_or_error


if TYPE_CHECKING:
    from elektro.api.schema import (
        Compartment,
        Section,
        SectionParamMap,
        GlobalParamMap,
        SectionInput,
        ModelConfigInput,
        CellInput,
        CompartmentInput,
        SectionParamMapInput,
    )


class ModelConfigTrait(BaseModel):
    def as_input(self) -> "ModelConfigInput":
        """Convert the model to a ModelConfigInput"""
        from elektro.api.schema import ModelConfigInput

        return ModelConfigInput(
            **self.model_dump(exclude={"id", "created_at", "updated_at"}),
        )


class SectionInputTrait(BaseModel):
    pass


class CompartmentInputTrait(BaseModel):
    def get_section_param_for_id(self, id: str) -> "SectionParamMapInput":
        sections = get_attributes_or_error(self, "section_params")
        x = next((section for section in sections if section.param == id), None)
        if x is None:
            raise ValueError(f"SectionParam with id {id} not found available are: {",".join(map(lambda x: x.param, sections))}")
        return x


class BiophysicsInputTrait(BaseModel):
    """Mixin for Biophysics data"""

    def get_compartment_for_id(self, id: str) -> "CompartmentInput":
        sections = get_attributes_or_error(self, "compartments")
        x = next((section for section in sections if section.id == id), None)
        if x is None:
            raise ValueError(f"Compartment with id {id} not found")
        return x


class TopologyInputTrait(BaseModel):
    """Mixin for Topology data"""

    def get_section_for_id(self, id: str) -> "SectionInput":
        sections = get_attributes_or_error(self, "sections")
        x = next((section for section in sections if section.id == id), None)
        if x is None:
            raise ValueError(f"Section with id {id} not found")
        return x

    @property
    def section_ids(self) -> List[str]:
        sections = get_attributes_or_error(self, "sections")
        return [section.id for section in sections]


class ModelConfigInputTrait(BaseModel):
    """Mixin for Topology data"""

    def get_cell_for_id(self, id: str) -> "CellInput":
        sections = get_attributes_or_error(self, "cells")
        x = next((section for section in sections if section.id == id), None)
        if x is None:
            raise ValueError(f"Cell with id {id} not found")
        return x

    @property
    def cell_ids(self) -> List[str]:
        sections = get_attributes_or_error(self, "cells")
        return [section.id for section in sections]


class BiophysicsTrait:
    """Mixin for Biophysics data"""

    def compartment_for_id(self, id: str) -> "Compartment":
        compartments = get_attributes_or_error(self, "compartments")
        x = next(
            (compartment for compartment in compartments if compartment.id == id), None
        )
        if x is None:
            raise ValueError(f"Compartment with id {id} not found")
        return x

    @property
    def compartment_ids(self) -> List[str]:
        compartments = get_attributes_or_error(self, "compartments")
        return [compartment.id for compartment in compartments]
    
    
    
    def as_dataframe(self) -> pd.DataFrame:
        """Convert the biophysics data to a pandas DataFrame"""
        from elektro.api.schema import Compartment
        
        
        compartments: list[Compartment] = get_attributes_or_error(self, "compartments")
        
        records = []
        
        for compartment in compartments:
        
            data = {
                "id": compartment.id,
                "mechanisms": " ".join(([mechanism for mechanism in compartment.mechanisms])),
                **{param.param: param.value for param in compartment.section_params},
                **{param.param: param.value for param in compartment.global_params}
            }
            
            records.append(data)
            
        return pd.DataFrame.from_records(records)
            
      
class TopologyTrait:
    """Mixin for Biophysics data"""

    def section_for_id(self, id: str) -> "Section":
        sections = get_attributes_or_error(self, "sections")
        x = next(
            (sec for sec in sections if sec.id == id), None
        )
        if x is None:
            raise ValueError(f"Compartment with id {id} not found")
        return x

    @property
    def section_ids(self) -> List[str]:
        compartments = get_attributes_or_error(self, "sections")
        return [compartment.id for compartment in compartments]
    
    
    
    def as_dataframe(self) -> pd.DataFrame:
        """Convert the biophysics data to a pandas DataFrame"""
        from elektro.api.schema import Section
        
        
        compartments: list[Section] = get_attributes_or_error(self, "sections")
        
        records = []
        
        for sec in compartments:
        
            data = {
                "id": sec.id,
                "length": sec.length,
                "diameter": sec.diam,
                "category": sec.category,
                "n_segments": sec.nseg,
                "connections": ", ".join([f"{conn.parent}({conn.location})" for conn in sec.connections]),
            }
            
            records.append(data)
            
        return pd.DataFrame.from_records(records)  
        
        


class CompartmentTrait:
    """Mixin for Biophysics data"""

    def section_param_for_id(self, id: str) -> "SectionParamMap":
        compartments = get_attributes_or_error(self, "section_params")
        x = next(
            (compartment for compartment in compartments if compartment.param == id),
            None,
        )
        if x is None:
            raise ValueError(f"SectionParam with id {id} not found")
        return x

    def global_param_for_id(self, id: str) -> "GlobalParamMap":
        compartments = get_attributes_or_error(self, "global_params")
        x = next(
            (compartment for compartment in compartments if compartment.param == id),
            None,
        )
        if x is None:
            raise ValueError(f"GlobalParam with id {id} not found")
        return x


class ExperimentTrait(BaseModel):
    @property
    def data(self) -> xr.Dataset:
        from elektro.api.schema import Experiment

        self = cast(Experiment, self)

        time_trace = self.time_trace.data

        recording_arrays = []
        recording_labels = []

        for i in self.recording_views:
            recording_xarray = i.recording.trace.data
            label = i.label

            label_array = xr.DataArray(
                data=recording_xarray.data,
                dims=["time"],
                coords={"time": time_trace},
            )

            recording_arrays.append(label_array)
            recording_labels.append(label)

        simulation_arrays = []
        simulation_labels = []

        for i in self.stimulus_views:
            stimulus_xarray = i.stimulus.trace.data
            label = i.label

            labeled_array = xr.DataArray(
                data=stimulus_xarray.data,
                dims=["time"],
                coords={"time": time_trace},
            )

            simulation_arrays.append(labeled_array)
            simulation_labels.append(label)

            # Add the recording to the dataset

        recording_arrays = xr.concat(recording_arrays, dim="trace")
        recording_arrays = recording_arrays.assign_coords(trace=recording_labels)

        simulation_arrays = xr.concat(simulation_arrays, dim="trace")
        simulation_arrays = simulation_arrays.assign_coords(trace=simulation_labels)

        # Create the dataset

        return xr.Dataset(
            {
                "recordings": recording_arrays,
                "stimulations": simulation_arrays,
            }
        )


class HasZarrStoreTrait(BaseModel):
    """Representation Trait

    Implements both identifier and shrinking methods.
    Also Implements the data attribute

    Attributes:
        data (xarray.Dataset): The data of the representation.

    """

    @property
    def data(self) -> xr.DataArray:
        store = get_attributes_or_error(self, "store")

        array: zarr.Array = from_zarr(store.zarr_store)
        print(array)

        return xr.DataArray(array, dims=["time"])

    @property
    def multi_scale_data(self) -> List[xr.DataArray]:
        scale_views = get_attributes_or_error(self, "derived_scale_views")

        if len(scale_views) == 0:
            raise ValueError(
                "No ScaleView found in views. Please create a ScaleView first."
            )

        sorted_views = sorted(scale_views, key=lambda image: image.scale_x)
        return [x.image.data for x in sorted_views]

    async def adata(self) -> Awaitable[xr.DataArray]:
        """The Data of the Representation as an xr.DataArray. Accessible from asyncio.

        Returns:
            xr.DataArray: The associated object.

        Raises:
            AssertionError: If the representation has no store attribute quries
        """
        pstore = get_attributes_or_error(self, "store")
        return await pstore.aopen()


V = TypeVar("V")


class HasZarrStoreAccessor(BaseModel):
    _openstore: Any = None

    @property
    def zarr_store(self):
        from elektro.io.download import open_zarr_store

        if self._openstore is None:
            id = get_attributes_or_error(self, "id")
            self._openstore = open_zarr_store(id)
        return self._openstore


class HasDownloadAccessor(BaseModel):
    _dataset: Any = None

    def download(self, file_name: str | None = None) -> "str":
        from elektro.io.download import download_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return download_file(url, file_name=file_name or key)


class HasPresignedDownloadAccessor(BaseModel):
    _dataset: Any = None

    def download(self, file_name: str | None = None) -> str:
        from elektro.io.download import download_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return download_file(url, file_name=file_name or key)


class Vector(Protocol):
    """A Protocol for Vectorizable data

    Attributes:
        x (float): The x value
        y (float): The y value
        z (float): The z value
        t (float): The t value
        c (float): The c value
    """

    x: float
    y: float
    z: float
    t: float
    c: float

    def __call__(
        self: V,
        x: Optional[int] = None,
        y: Optional[int] = None,
        z: Optional[int] = None,
        t: Optional[int] = None,
        c: Optional[int] = None,
    ) -> V: ...


class IsVectorizableTrait:
    pass

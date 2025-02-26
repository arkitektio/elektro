"""
Traits for elektro

Traits are mixins that are added to every graphql type that exists on the mikro schema.
We use them to add functionality to the graphql types that extend from the base type.

Every GraphQL Model on Mikro gets a identifier and shrinking methods to ensure the compatibliity
with arkitekt. This is done by adding the identifier and the shrinking methods to the graphql type.
If you want to add your own traits to the graphql type, you can do so by adding them in the graphql
.config.yaml file.

"""

from typing import Awaitable, List, TypeVar, Tuple, Protocol, Optional
import numpy as np
from pydantic import BaseModel
import xarray as xr
import pandas as pd
from typing import TYPE_CHECKING
from dask.array import from_zarr
import zarr
from .scalars import FiveDVector
from .utils import rechunk
from rath.scalars import ID
from typing import Any
from rath.turms.utils import get_attributes_or_error
import dataclasses

if TYPE_CHECKING:
    from pyarrow.parquet import ParquetDataset
    from elektro.api.schema import Entity



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

        return xr.DataArray(array, dims=["c", "t", "z", "y", "x"])

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

    def get_pixel_size(self, stage: ID = None) -> Tuple[float, float, float]:
        """The pixel size of the representation

        Returns:
            Tuple[float, float, float]: The pixel size
        """
        views = get_attributes_or_error(self, "views")

        for view in views:
            if isinstance(view, PixelTranslatable):
                if stage is None:
                    return view.pixel_size
                else:
                    if get_attributes_or_error(view, "stage.id") == stage:
                        return view.pixel_size

        raise NotImplementedError(
            f"No pixel size found for this representation {self}. Have you attached any views?"
        )


class PhysicalSizeProtocol(Protocol):
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
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        z: Optional[int] = None,
        t: Optional[int] = None,
        c: Optional[int] = None,
    ): ...


class PhysicalSizeTrait:
    """Additional Methods for PhysicalSize"""

    def is_similar(
        self: PhysicalSizeProtocol,
        other: PhysicalSizeProtocol,
        tolerance: Optional[float] = 0.02,
        raise_exception: Optional[bool] = False,
    ) -> bool:
        if hasattr(self, "x") and self.x is not None and other.x is not None:
            if abs(other.x - self.x) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"X values are not similar: {self.x} vs {other.x} is above tolerance {tolerance}"
                    )
                return False
        if hasattr(self, "y") and self.y is not None and other.y is not None:
            if abs(other.y - self.y) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"Y values are not similar: {self.y} vs {other.y} is above tolerance {tolerance}"
                    )
                return False
        if hasattr(self, "z") and self.z is not None and other.z is not None:
            if abs(other.z - self.z) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"Z values are not similar: {self.z} vs {other.z} is above tolerance {tolerance}"
                    )
                return False
        if hasattr(self, "t") and self.t is not None and other.t is not None:
            if abs(other.t - self.t) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"T values are not similar: {self.t} vs {other.t} is above tolerance {tolerance}"
                    )
                return False
        if hasattr(self, "c") and self.c is not None and other.c is not None:
            if abs(other.c - self.c) > tolerance:
                if raise_exception:
                    raise ValueError(
                        f"C values are not similar: {self.c} vs {other.c} is above tolerance {tolerance}"
                    )
                return False

        return True

    def to_scale(self):
        return [
            getattr(self, "t", 1),
            getattr(self, "c", 1),
            getattr(self, "z", 1),
            getattr(self, "y", 1),
            getattr(self, "x", 1),
        ]


class IsVectorizableTrait:
    """Additional Methods for ROI"""

    @property
    def vector_data(self) -> np.ndarray:
        """A numpy array of the vectors of the ROI

        Returns:
            np.ndarray: _description_
        """
        return self.get_vector_data(dims="yx")

    def get_vector_data(self, dims="yx") -> np.ndarray:
        vector_list = getattr(self, "vectors", None)
        assert (
            vector_list
        ), "Please query 'vectors' in your request on 'ROI'. Data is not accessible otherwise"
        vector_list: list

        mapper = {
            "y": 4,
            "x": 3,
            "z": 2,
            "t": 1,
            "c": 0,
        }

        return np.array([[v[mapper[ac]] for ac in dims] for v in vector_list])

    def center(self) -> FiveDVector:
        """The center of the ROI

        Caluclates the geometrical center of the ROI according to its type
        and the vectors of the ROI.

        Returns:
            InputVector: The center of the ROI
        """
        from elektro.api.schema import RoiTypeInput, InputVector

        assert hasattr(
            self, "type"
        ), "Please query 'type' in your request on 'ROI'. Center is not accessible otherwise"
        if self.type == RoiTypeInput.RECTANGLE:
            return InputVector.from_array(
                self.get_vector_data(dims="ctzyx").mean(axis=0)
            )

        raise NotImplementedError(
            f"Center calculation not implemented for this ROI type {self.type}"
        )

    def crop(self, data: xr.DataArray) -> xr.DataArray:
        """Crop the data to the ROI

        Args:
            data (xr.DataArray): The data to crop

        Returns:
            xr.DataArray: The cropped data
        """
        vector_data = self.get_vector_data(dims="ctzyx")
        return data.sel(
            x=slice(vector_data[:, 3].min(), vector_data[:, 3].max()),
            y=slice(vector_data[:, 4].min(), vector_data[:, 4].max()),
            z=slice(vector_data[:, 2].min(), vector_data[:, 2].max()),
            t=slice(vector_data[:, 1].min(), vector_data[:, 1].max()),
            c=slice(vector_data[:, 0].min(), vector_data[:, 0].max()),
        )

    def center_as_array(self) -> np.ndarray:
        """The center of the ROI

        Caluclates the geometrical center of the ROI according to its type
        and the vectors of the ROI.

        Returns:
            InputVector: The center of the ROI
        """
        from elektro.api.schema import RoiTypeInput

        assert hasattr(
            self, "type"
        ), "Please query 'type' in your request on 'ROI'. Center is not accessible otherwise"
        if self.type == RoiTypeInput.RECTANGLE:
            return self.get_vector_data(dims="ctzyx").mean(axis=0)
        if self.type == RoiTypeInput.POINT:
            return self.get_vector_data(dims="ctzyx")[0]

        raise NotImplementedError(
            f"Center calculation not implemented for this ROI type {self.type}"
        )


class HasParquestStoreTrait(BaseModel):
    """Table Trait

    Implements both identifier and shrinking methods.
    Also Implements the data attribute

    Attributes:
        data (pd.DataFrame): The data of the table.

    """

    @property
    def data(self) -> pd.DataFrame:
        """The data of this table as a pandas dataframe

        Returns:
            pd.DataFrame: The Dataframe
        """
        store: "ParquetStore" = get_attributes_or_error(self, "store")
        return store.parquet_dataset.read_pandas().to_pandas()


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


class HasParquetStoreAccesor(BaseModel):
    _dataset: Any = None

    @property
    def parquet_dataset(self) -> "ParquetDataset":
        import pyarrow.parquet as pq
        from elektro.io.download import open_parquet_filesystem

        if self._dataset is None:
            id = get_attributes_or_error(self, "id")
            self._dataset = open_parquet_filesystem(id)
        return self._dataset


class HasDownloadAccessor(BaseModel):
    _dataset: Any = None

    def download(self, file_name: str = None) -> "str":
        from elektro.io.download import download_file

        url, key = get_attributes_or_error(self, "presigned_url", "key")
        return download_file(url, file_name=file_name or key)


class HasPresignedDownloadAccessor(BaseModel):
    _dataset: Any = None

    def download(self, file_name: str = None) -> str:
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


T = TypeVar("T", bound=Vector)


class HasPixelSizeTrait:
    """Mixin for PixelTranslatable data"""

    @property
    def pixel_size(self) -> Tuple[float, float, float]:
        """The pixel size of the representation

        Returns:
            Tuple[float, float, float]: The pixel size
        """
        kind, matrix = get_attributes_or_error(self, "kind", "matrix")

        if kind == "AFFINE":
            return tuple(np.array(matrix).reshape(4, 4).diagonal()[:3])

        raise NotImplementedError(f"Pixel size not implemented for this kind {kind}")

    @property
    def position(self) -> Tuple[float, float, float]:
        """The pixel size of the representation

        Returns:
            Tuple[float, float, float]: The pixel size
        """
        kind, matrix = get_attributes_or_error(self, "kind", "matrix")

        if kind == "AFFINE":
            return tuple(np.array(matrix).reshape(4, 4)[:3, 3])

        raise NotImplementedError(f"Pixel size not implemented for this kind {kind}")


class HasFromNumpyArrayTrait:
    """Mixin for Vectorizable data
    adds functionality to convert a numpy array to a list of vectors
    """

    @classmethod
    def list_from_numpyarray(
        cls: T,
        x: np.ndarray,
        t: Optional[int] = None,
        c: Optional[int] = None,
        z: Optional[int] = None,
    ) -> List[T]:
        """Creates a list of InputVector from a numpya array

        Args:
            vector_list (List[List[float]]): A list of lists of floats

        Returns:
            List[Vectorizable]: A list of InputVector
        """
        assert x.ndim == 2, "Needs to be a List array of vectors"
        if x.shape[1] == 4:
            return [cls(x=i[1], y=i[0], z=i[2], t=i[3], c=c) for i in x.tolist()]
        if x.shape[1] == 3:
            return [cls(x=i[1], y=i[0], z=i[2], t=t, c=c) for i in x.tolist()]
        elif x.shape[1] == 2:
            return [cls(x=i[1], y=i[0], t=t, c=c, z=z) for i in x.tolist()]
        else:
            raise NotImplementedError(
                f"Incompatible shape {x.shape} of {x}. List dimension needs to either be of size 2 or 3"
            )

    @classmethod
    def from_array(
        cls: T,
        x: np.ndarray,
    ) -> T:
        return cls(x=x[4], y=x[3], z=x[2], t=x[1], c=x[0])

import asyncio

from elektro.scalars import TraceLike, FileLike
from rath.links.parsing import ParsingLink
from rath.operation import Operation, opify
from elektro.io.types import Uploader
from typing import Any
from elektro.io.upload import aupload_bigfile, aupload_xarray
from pydantic import Field
from concurrent.futures import ThreadPoolExecutor
import uuid
from functools import partial
from elektro.datalayer import DataLayer


async def apply_recursive(func, obj, typeguard):
    """
    Recursively applies an asynchronous function to elements in a nested structure.

    Args:
        func (callable): The asynchronous function to apply.
        obj (any): The nested structure (dict, list, tuple, etc.) to process.
        typeguard (type): The type of elements to apply the function to.

    Returns:
        any: The nested structure with the function applied to elements of the specified type.
    """
    if isinstance(
        obj, dict
    ):  # If obj is a dictionary, recursively apply to each key-value pair
        return {k: await apply_recursive(func, v, typeguard) for k, v in obj.items()}
    elif isinstance(obj, list):  # If obj is a list, recursively apply to each element
        return await asyncio.gather(
            *[apply_recursive(func, elem, typeguard) for elem in obj]
        )
    elif isinstance(
        obj, tuple
    ):  # If obj is a tuple, recursively apply to each element and convert back to tuple
        return tuple(
            await asyncio.gather(
                *[apply_recursive(func, elem, typeguard) for elem in obj]
            )
        )
    elif isinstance(obj, typeguard):  # If obj matches the typeguard, apply the function
        return await func(obj)
    else:  # If obj is not a dict, list, tuple, or matching the typeguard, return it as is
        return obj


async def afake_upload(xarray: TraceLike, *args, **kwargs) -> str:
    return str(uuid.uuid4())


class UploadLink(ParsingLink):
    """Data Layer Upload Link

    This link is used to upload  supported types to a DataLayer.
    It parses queries, mutatoin and subscription arguments and
    uploads the items to the DataLayer, and substitures the
    DataFrame with the S3 path.

    Args:
        ParsingLink (_type_): _description_


    """
    xarray_uploader: Uploader = aupload_xarray
    bigfile_uploader: Uploader = aupload_bigfile
    datalayer: DataLayer

    executor: ThreadPoolExecutor = Field(
        default_factory=lambda: ThreadPoolExecutor(max_workers=4), exclude=True
    )
    _executor_session: Any = None

    async def __aenter__(self):
        self._executor_session = self.executor.__enter__()

    async def aget_image_credentials(self, key, datalayer) -> Any:
        from elektro.api.schema import RequestUploadMutation, RequestUploadInput

        operation = opify(
            RequestUploadMutation.Meta.document,
            variables={
                "input": RequestUploadInput(key=key, datalayer=datalayer).model_dump()
            },
        )

        async for result in self.next.aexecute(operation):
            return RequestUploadMutation(**result.data).request_upload


    async def aget_bigfile_credentials(self, key, datalayer) -> Any:
        from elektro.api.schema import (
            RequestFileUploadMutation,
            RequestFileUploadInput,
        )

        operation = opify(
            RequestFileUploadMutation.Meta.document,
            variables={
                "input": RequestFileUploadInput(
                    key=key, datalayer=datalayer
                ).model_dump()
            },
        )

        async for result in self.next.aexecute(operation):
            return RequestFileUploadMutation(**result.data).request_file_upload
        

    async def aupload_xarray(self, datalayer: "DataLayer", xarray: TraceLike) -> str:
        assert datalayer is not None, "Datalayer must be set"
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self.aget_image_credentials(xarray.key, endpoint_url)
        return await self.xarray_uploader(
            xarray,
            credentials,
            datalayer,
            self._executor_session,
        )

    async def aupload_bigfile(self, datalayer: "DataLayer", file: FileLike) -> str:
        assert datalayer is not None, "Datalayer must be set"
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self.aget_bigfile_credentials(file.key, endpoint_url)
        return await self.bigfile_uploader(
            file,
            credentials,
            datalayer,
            self._executor_session,
        )
    

    async def aparse(self, operation: Operation) -> Operation:
        """Parse the operation (Async)

        Extracts the DataFrame from the operation and uploads it to the DataLayer.

        Args:
            operation (Operation): The operation to parse

        Returns:
            Operation: _description_
        """

        datalayer = operation.context.kwargs.get("datalayer", self.datalayer)

        operation.variables = await apply_recursive(
            partial(self.aupload_xarray, datalayer),
            operation.variables,
            TraceLike,
        )
        operation.variables = await apply_recursive(
            partial(self.aupload_bigfile, datalayer), operation.variables, FileLike
        )

        return operation

    async def adisconnect(self):
        self.executor.__exit__(None, None, None)

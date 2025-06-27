from typing import TYPE_CHECKING
from elektro.scalars import TraceLike, FileLike
import asyncio
import s3fs
from aiobotocore.session import get_session
import botocore
from concurrent.futures import ThreadPoolExecutor

from .errors import PermissionsError, UploadError
from zarr.storage import FsspecStore
import zarr
import zarr.api.asynchronous as async_api
import aiohttp

if TYPE_CHECKING:
    from elektro.api.schema import Credentials
    from elektro.datalayer import DataLayer


async def astore_xarray_input(
    xarray: TraceLike,
    credentials: "Credentials",
    endpoint_url: "DataLayer",
) -> str:
    """Stores an xarray in the DataLayer"""

    filesystem = s3fs.S3FileSystem(
        secret=credentials.secret_key,
        key=credentials.access_key,
        client_kwargs={
            "endpoint_url": endpoint_url,
            "aws_session_token": credentials.session_token,
        },
        asynchronous=True,
    )

    # random_uuid = uuid.uuid4()
    # s3_path = f"zarr/{random_uuid}.zarr"

    array = xarray.value

    s3_path = f"{credentials.bucket}/{credentials.key}"
    store = FsspecStore(filesystem, read_only=False, path=s3_path)

    try:
        await async_api.save_array(store, array.to_numpy(), zarr_version=3)
        return credentials.store
    except Exception as e:
        raise UploadError(f"Error while uploading to {s3_path}") from e


async def aupload_bigfile(
    file: FileLike,
    credentials: "Credentials",
    datalayer: "DataLayer",
    executor: ThreadPoolExecutor = None,
) -> str:
    """Store a DataFrame in the DataLayer"""
    session = get_session()

    endpoint_url = await datalayer.get_endpoint_url()

    async with session.create_client(
        "s3",
        region_name="us-west-2",
        endpoint_url=endpoint_url,
        aws_secret_access_key=credentials.secret_key,
        aws_access_key_id=credentials.access_key,
        aws_session_token=credentials.session_token,
    ) as client:
        try:
            await client.put_object(
                Bucket=credentials.bucket, Key=credentials.key, Body=file.value
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "InvalidAccessKeyId":
                return PermissionsError(
                    "Access Key is invalid, trying to get new credentials"
                )

            raise e

    return credentials.store


async def aupload_xarray(
    array: TraceLike,
    credentials: "Credentials",
    datalayer: "DataLayer",
    executor: ThreadPoolExecutor,
) -> str:
    """Store a DataFrame in the DataLayer"""
    return await astore_xarray_input(
        array, credentials, await datalayer.get_endpoint_url()
    )

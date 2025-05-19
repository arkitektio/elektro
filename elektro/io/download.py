import zarr.storage
from elektro.api.schema import (
    arequest_access,
    arequest_file_access,
    AccessCredentials,
)
from elektro.datalayer import DataLayer, current_elektro_datalayer
import s3fs  # type: ignore
from koil import unkoil
import zarr
import aiohttp
from typing import Tuple
from rath.scalars import ID


async def aget_zarr_credentials_and_endpoint(
    store: str,
) -> Tuple[AccessCredentials, str]:
    datalayer = current_elektro_datalayer.get()
    if not datalayer:
        raise ValueError("No datalayer found. Please provide a datalayer.")

    credentials = await arequest_access(ID.validate(store))
    endpoint_url = await datalayer.get_endpoint_url()
    return credentials, endpoint_url


async def aget_file_credentials_and_endpoint(
    store: str,
) -> Tuple[AccessCredentials, str]:
    datalayer = current_elektro_datalayer.get()
    if not datalayer:
        raise ValueError("No datalayer found. Please provide a datalayer.")

    credentials = await arequest_file_access(ID.validate(store))
    endpoint_url = await datalayer.get_endpoint_url()
    return credentials, endpoint_url


def open_zarr_store(store_id: str, cache: int = 2**30):
    credentials, endpoint_url = unkoil(aget_zarr_credentials_and_endpoint, store_id)

    _s3fs = s3fs.S3FileSystem(
        secret=credentials.secret_key,
        key=credentials.access_key,
        client_kwargs={
            "endpoint_url": endpoint_url,
            "aws_session_token": credentials.session_token,
        },
        asynchronous=True,
    )
    print(credentials.path)
    return zarr.storage.FsspecStore(
        _s3fs, read_only=False, path=f"{credentials.bucket}/{credentials.key}"
    )


async def aopen_zarr_store(store_id: str, cache: int = 2**30):
    credentials, endpoint_url = await aget_zarr_credentials_and_endpoint(store_id)

    _s3fs = s3fs.S3FileSystem(
        secret=credentials.secret_key,
        key=credentials.access_key,
        client_kwargs={
            "endpoint_url": endpoint_url,
            "aws_session_token": credentials.session_token,
        },
        asynchronous=True,
    )

    return zarr.storage.FsspecStore(
        _s3fs, read_only=False, path=f"{credentials.bucket}/{credentials.key}"
    )


async def adownload_file(
    presigned_url: str,
    file_name: str,
    datalayer: DataLayer | None = None,
):
    datalayer = datalayer or current_elektro_datalayer.get()
    if not datalayer:
        raise ValueError("No datalayer found. Please provide a datalayer.")
    endpoint_url = await datalayer.get_endpoint_url()

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint_url + presigned_url) as response:
            with open(file_name, "wb") as file:
                while True:
                    chunk = await response.content.read(
                        1024
                    )  # read the response by chunks of 1024 bytes
                    if not chunk:
                        break
                    file.write(chunk)

    return file_name


def download_file(
    presigned_url: str, file_name: str, datalayer: DataLayer | None = None
):
    return unkoil(
        adownload_file, presigned_url, file_name=file_name, datalayer=datalayer
    )

"""
This module offers simple file storage utilities suited for typical scenarios in our services.
Its primary function is to facilitate file transfers between services using our temporary cloud storage solution.

NOTE:
    This module is not designed to manage intricate file storage tasks. For more sophisticated capabilities, you must develop custom solutions.
    These may include:

    - Download caching
    - File integrity verification via hashing
    - Custom request headers
    - Concurrent operations
    - Access control lists (ACLs)
    - And other advanced features

NOTE:
    This module is intentionally designed for simplicity and relies solely on the standard library and the `google-cloud-storage` package.
    As the `google-cloud-storage` package does not support asynchronous operations, this module also does not support async functionality.
"""

import shutil
from os.path import basename, join, splitext
from pathlib import Path

from .anyuri import AnyUri, FileUri, GSUri, HttpUri
from .exceptions import DownloadError, FileCopyError, UploadError, UriSchemaError
from .temp import filename
from .utils.gs import (
    download_from_gs_uri,
    download_from_http_url,
    extract_ext_from_uri,
    upload_to_gs_uri,
)


def local(uri: AnyUri | Path | str) -> FileUri:
    """
    Downloads the specified URI to the local temporary file system.

    This function aims to preserve the same file extension as the original URI, while generating a unique filename to avoid any conflicts.

    - If the URI points to a local file, the function duplicates it in the local file system.
    - If the URI is an HTTP URL, the function fetches the file and stores it in the local file system.
    - If the URI is a GS URL, the function employs the Google Cloud Storage SDK to download the file to the local file system, even if the file is not publicly accessible.

    Args:
        uri: The URI of the file to be downloaded.

    Returns:
        The local path where the file has been downloaded. If the file extension cannot be inferred from the URI, the function defaults to using ".unknown" as the file extension.

    Raises:
        UriSchemaError: If the URI scheme is not supported.
        DownloadError: If the URI is an HTTP or GS URL and the download operation fails.
        FileCopyError: If the URI is a local file and the file copy operation fails.

    Note:
        This function generates a unique filename to avoid conflicts. It strives to preserve the same file extension as the original URI, but defaults to ".unknown" if the file extension cannot be inferred.
    """
    any_uri = AnyUri(uri)
    target_file_uri = FileUri(filename(suffix=extract_ext_from_uri(any_uri)))

    if isinstance(any_uri, HttpUri):
        try:
            return download_from_http_url(any_uri, target_file_uri)
        except Exception as e:
            raise DownloadError(f"failed to download {any_uri}") from e

    if isinstance(any_uri, FileUri):
        try:
            return shutil.copy(any_uri.as_source(), target_file_uri.as_source())
        except Exception as e:
            raise FileCopyError(f"failed to copy {any_uri}") from e

    if isinstance(any_uri, GSUri):
        try:
            return download_from_gs_uri(any_uri, target_file_uri)
        except Exception as e:
            raise DownloadError(f"failed to download {any_uri}") from e

    raise NotImplementedError(f"not supported uri {any_uri}")


def remote(
    uri: AnyUri | Path | str,
    location: str = "gs://livingbio-tmp",
) -> GSUri:
    """
    Uploads the URI to our cloud storage at our temporary storage `gs://livingbio-tmp` and returns the file's GSUri. When the upload happens, it always uses a random filename to avoid conflicts.

    - If the URI is a GSUri or HttpUri, the function will first download it to the local file system and then upload it to the cloud storage.
    - If the URI is already a local file, the function will upload it directly to the cloud storage.

    Args:
        uri: The URI to upload.
        location: The cloud storage location to upload the file to. Defaults to `gs://livingbio-tmp`.

    Returns:
        The uploaded file's GSUri. If the file extension cannot be extracted from the URI, the function uses ".unknown" as the file extension.

    Raises:
        UriSchemaError: If the URI scheme is not supported.
        DownloadError: If the URI is an HTTP or GS URL and the download operation fails.
        FileCopyError: If the URI is a local file and the file copy operation fails.
        UploadError: If the upload operation fails.

    NOTE:
        This function always uses a random filename to avoid conflicts. It tries to use the same file extension as the URI, but if the file extension cannot be extracted from the URI, the function uses ".unknown" as the file extension.
    """
    _uri = AnyUri(uri)

    if isinstance(_uri, (GSUri, HttpUri)):
        path = local(_uri)

    elif isinstance(_uri, FileUri):
        path = _uri

    else:
        raise UriSchemaError(f"unsupported uri {_uri}")

    _, ext = splitext(path)

    target_uri = join(location, basename(filename(suffix=ext)))

    try:
        return upload_to_gs_uri(path, GSUri(target_uri))
    except Exception as e:
        raise UploadError(f"failed to upload {uri} to {target_uri}") from e

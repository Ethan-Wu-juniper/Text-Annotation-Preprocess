import re
from os.path import splitext
from urllib.parse import urlparse
from urllib.request import build_opener, install_opener, urlretrieve

from google.cloud import storage  # type: ignore

from ..credential import get_crendential
from ..anyuri import AnyUri, FileUri, GSUri, HttpUri


def is_legal_file_ext(ext: str) -> bool:
    """
    Check if the file extension is legal.

    Args:
        ext: The file extension to check.

    Returns:
        True if the file extension is legal, False otherwise.
    """

    # Regular expression for validating a file extension
    # This pattern checks for a starting dot, followed by 1 to 10 alphanumeric characters
    # You can adjust the [A-Za-z0-9] part to include any additional characters you consider valid
    pattern = r"^\.[A-Za-z0-9]{1,10}$"
    return bool(re.match(pattern, ext))


def extract_ext_from_uri(http_uri: AnyUri) -> str | None:
    """
    Extract the ext from a URI. If the URI has a valid file extension, use it.
    Otherwise, return None

    Args:
        http_uri: The URL to extract the filename from.

    Returns:
        The extract file extension, None if the URL does not have a valid file extension
    """

    # Parse the URL to extract the path
    parsed_url = urlparse(http_uri.as_uri())
    path = parsed_url.path

    # Split the path by '/' to get the last part
    path_parts = path.split("/")
    filename = path_parts[-1]

    # Split the filename by '.' to get the file extension
    name, ext = splitext(filename)
    if is_legal_file_ext(ext):
        return ext

    return None


def download_from_http_url(http_uri: HttpUri, local_filepath: FileUri) -> FileUri:
    """
    Downloads the specified HTTP URL to the local file system.

    Args:
        http_uri: The HTTP URL to download.
        local_filepath: The local file path where the downloaded file will be saved.

    Returns:
        The local path where the file has been downloaded.
    """

    # Create an opener object
    opener = build_opener()
    opener.addheaders = [
        (
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        )
    ]

    # Install the opener globally so it will be used for all urllib.request.urlopen calls
    install_opener(opener)
    path, _ = urlretrieve(http_uri, local_filepath)
    return local_filepath


def download_from_gs_uri(gs_uri: GSUri, local_filepath: FileUri) -> FileUri:
    """
    Downloads the specified Google Cloud Storage (GS) URI to the local file system.

    Args:
        gs_uri: The GS URI to download.
        local_filepath: The local file path where the downloaded file will be saved.

    Returns:
        The local path where the file has been downloaded.
    """
    p = urlparse(gs_uri.as_uri())

    # Set your Google Cloud Storage bucket name
    bucket_name = p.netloc

    # Set the path of the file you want to download in the bucket
    file_path = p.path.lstrip("/")

    # Initialize a client
    client = storage.Client(credentials=get_crendential())

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Get the blob (file) you want to download
    blob = bucket.blob(file_path)

    # Download the file
    blob.download_to_filename(local_filepath)

    return local_filepath


def upload_to_gs_uri(local_file_path: FileUri, gs_uri: GSUri) -> GSUri:
    """
    Uploads a local file to a specified Google Cloud Storage (GS) URI.

    Args:
        local_file_path: The path of the local file to be uploaded.
        gs_uri: The GS URI where the file will be uploaded.

    Returns:
        The GS URI where the file has been uploaded.
    """

    p = urlparse(gs_uri.as_uri())

    # Set your Google Cloud Storage bucket name
    bucket_name = p.netloc

    # Set the destination path within the bucket where you want to upload the file
    destination_blob_name = p.path.lstrip("/")

    # Initialize a client
    client = storage.Client(credentials=get_crendential())

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Create a blob (file) with the specified destination path
    blob = bucket.blob(destination_blob_name)

    # Upload the local file to the specified blob (file)
    blob.upload_from_filename(local_file_path)

    return gs_uri

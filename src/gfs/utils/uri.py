import os
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse, urlunparse


def normalize_url(http_uri: str) -> str:
    """
    Normalizes a HttpUri by resolving '..' and '.' in the path.

    Parameters:
        http_uri: The URL to be normalized.

    Returns:
        The normalized URL.

    """
    parsed_url = urlparse(http_uri)
    resolved_url = urljoin(http_uri, parsed_url.path)

    return urlunparse(parsed_url._replace(path=urlparse(resolved_url).path))


def uri_to_path(file_uri: str) -> str:
    """
    Converts a File URI to a path. It is the inverse of path.as_uri().

    Parameters:
        file_uri: The File URI to be converted.

    Returns:
        The converted path.

    """
    # https://stackoverflow.com/questions/5977576/is-there-a-convenient-way-to-map-a-file-uri-to-os-path
    parsed = urlparse(file_uri)

    if parsed.scheme != "file":
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")

    path_str = unquote(parsed.path)

    # Windows fix for "/C:/..." → "C:/..."
    if (
        os.name == "nt"
        and path_str.startswith("/")
        and len(path_str) > 2
        and path_str[2] == ":"
    ):
        path_str = path_str[1:]

    return os.path.normpath(Path(path_str))

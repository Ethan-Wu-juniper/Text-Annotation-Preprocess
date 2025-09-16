class GFSError(Exception):
    """Base class for all GFS errors."""


class UriSchemaError(GFSError, ValueError):
    """
    Raised when the URI schema is not supported. It is a subclass of both GFSError and ValueError.
    """


class DownloadError(GFSError):
    """
    Raised when the download operation fails.
    """


class FileCopyError(GFSError):
    """
    Raised when the file copy operation fails.
    """


class UploadError(GFSError):
    """
    Raised when the upload operation fails.
    """


__all__ = [
    "GFSError",
    "UriSchemaError",
    "DownloadError",
    "FileCopyError",
    "UploadError",
]

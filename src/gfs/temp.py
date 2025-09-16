"""
This module provides functionality to create temporary files and directories specific to the current thread. These temporary resources are automatically deleted when the context (thread) exits, preventing Out-Of-Memory (OOM) errors due to excessive temporary data.

This feature is particularly beneficial in a web server context, where it's essential to clean up temporary data after each request to maintain optimal performance and resource utilization.
"""

import pathlib
import tempfile
import threading
from contextlib import contextmanager
from typing import Generator, Optional

_thread_locals = threading.local()


@contextmanager
def threading_tempdir() -> Generator[str, None, None]:
    """
    Create a temporary directory for the current thread. The directory will be deleted when the context exits.

    Returns:
        The temporary directory path.

    Examples:
        >>> with threading_tempdir() as temp_dir:
        ...     f = filename() # create a temporary filename (not exists) in the temporary directory
        ...     with open(f, "w") as ofile:
        ...         ofile.write("hello world")
        ...     assert os.path.exists(f)
        ...
        >>> assert not os.path.exists(f) # the file will be deleted with context

    """
    with tempfile.TemporaryDirectory() as tempdir:
        _thread_locals.tempdir = tempdir
        yield tempdir
        _thread_locals.tempdir = None


def get_threading_tempdir() -> Optional[str]:
    """
    Retrieves the path of the temporary directory specific to the current thread, provided that 'threading_tempdir' is enabled.

    Returns:
        The path of the thread-specific temporary directory. If 'threading_tempdir' is not enabled, returns `None`.
    """
    return getattr(_thread_locals, "tempdir", None)


def dirname(suffix: str = None, prefix: str = None) -> pathlib.Path:
    """
    Creates a temporary directory.

    - If 'threading_tempdir' is enabled, the directory is created within the thread's temporary folder and is deleted when the context exits.
    - If 'threading_tempdir' is not enabled, the temporary directory behaves like a regular 'tempfile.TemporaryDirectory'.

    Args:
        suffix: The suffix of the temporary directory.
        prefix: The prefix of the temporary directory.

    Returns:
        The temporary directory path.
    """

    return pathlib.Path(
        tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=get_threading_tempdir())
    )


def filepath(suffix: str = None, prefix: str = None) -> pathlib.Path:
    """
    Creates a temporary filepath without actually creating a file.

    - If 'threading_tempdir' is enabled, the file will be automatically deleted when the context exits.
    - If 'threading_tempdir' is not enabled, the temporary file behaves like a regular 'tempfile.NamedTemporaryFile'.

    Args:
        suffix: The suffix of the temporary file. If suffix is not specified, it will be set to `.unknown`. If suffix does not start with `.`, `.` will be added to the beginning of suffix.
        prefix: The prefix of the temporary file.

    Returns:
        The temporary file path.

    Notes:
        The only difference between `filepath` and `filename` is that `filepath` returns a `pathlib.Path` object while `filename` returns a `str` object.
    """

    if suffix is None:
        suffix = ".unknown"

    if not suffix.startswith("."):
        suffix = "." + suffix

    with tempfile.NamedTemporaryFile(
        prefix=prefix, suffix=suffix, dir=get_threading_tempdir()
    ) as ofile:
        return ofile.name


def filename(suffix: str = None, prefix: str = None) -> str:
    """
    Creates a temporary filepath without actually creating a file.

    - If 'threading_tempdir' is enabled, the file will be automatically deleted when the context exits.
    - If 'threading_tempdir' is not enabled, the temporary file behaves like a regular 'tempfile.NamedTemporaryFile'.

    Args:
        suffix: The suffix of the temporary file. If suffix is not specified, it will be set to `.unknown`. If suffix does not start with `.`, `.` will be added to the beginning of suffix.
        prefix: The prefix of the temporary file.

    Returns:
        The temporary file path.

    Notes:
        The only difference between `filepath` and `filename` is that `filepath` returns a `pathlib.Path` object while `filename` returns a `str` object.
    """
    return str(filepath(suffix=suffix, prefix=prefix))


__all__ = ["dirname", "filepath", "filename", "threading_tempdir"]

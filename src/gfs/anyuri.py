"""
This module defines the AnyUri class and it's subclasses. AnyUri is a polymorphic virtual superclass for different URI. Constructing an
instance will automatically dispatch to `GSUri`, `HttpUri` or `FileUri` based on the input. It also supports both
isinstance and issubclass checks.


The class is decided to reduce repetative code to check the uri type.

```py
# Before
def download(uri: str) -> Any
    if uri.startswith("gs://") or uri.startswith("https://storage.googleapis.com/")
        return download_gs(uri)
    elif uri.startswith("http://") or uri.startswith("https://"):
        return download_http(uri)
    elif uri.startswith("file://") or uri.startswith("/"):
        return download_file(uri)

# After
def download(uri: AnyUri) -> Any
    if isinstance(uri, GSUri):
        return download_gs(uri)
    elif isinstance(uri, HttpUri):
        return download_http(uri)
    elif isinstance(uri, FileUri):
        return download_file(uri)
```

AnyUri provides some basic handly interface to reduce the code complexity. For example, it provides `as_uri` and `as_source`

```py
# Before
def ffprobe(uri: str) -> Any:
    if uri.startswith("gs://") or uri.startswith("https://storage.googleapis.com/")
        # convert uri to https
        ...
    elif uri.startswith("http://") or uri.startswith("https://"):
        ...
    elif uri.startswith("file://") or uri.startswith("/"):
        # convert uri to local path
    do_ffprobe(converted_uri)


# After
def ffprobe(uri: AnyUri) -> Any:
    do_ffprobe(uri.as_source())
```

AnyUri also helps with type checking. It can be used as a type declaration to leverage mypy's type checking.

```py
# Before
def some_func() -> str:
    ...

def some_other_func(uri: str) -> None:
    # need to validate whether it is a http uri or not
    ...

some_other_func(some_func())

# After
def some_func() -> HttpUri:
    ...

def some_other_func(uri: HttpUri) -> None:
    ...

some_other_func(some_func())  # type checking will validate that the uri is a http uri
```

AnyUri also integrates with Pydantic. When used as a type declaration for a Pydantic BaseModel, the Pydantic validation process will appropriately run inputs through this class' constructor and dispatch to specific URI type.

```py
from pydantic import BaseModel
from gfs import AnyUri

class MyModel(BaseModel):
    uri: AnyUri

MyModel(uri="https://example.com/1.jpg")  # will be validated as HttpUri
```

Notes:
    AnyUri support both pydantic 1.0 and 2.0

AnyUri behaves just like a regular string. It can be safely used in any context where a normal string is applicable. This is a main difference from another similar package `cloudpathlib`.

```py
>>> AnyUri("https://example.com/1.jpg") == "https://example.com/1.jpg"
True

>>> ffprobe(AnyUri("gs://bucket/1.jpg"))  # works!
```
"""

from __future__ import annotations

import pathlib
from typing import Any, no_type_check
from urllib.parse import ParseResult, urlparse, urlunparse

from .exceptions import UriSchemaError
from .utils.uri import normalize_url, uri_to_path
from functools import cached_property


class AnyUri(str):
    """
    Polymorphic virtual superclass for different URI. Constructing an instance will automatically dispatch to
    `GSUri`, `HttpUri` or `FileUri` based on the input. It also supports both isinstance and issubclass checks.

    This class also integrates with Pydantic. When used as a type declaration for a Pydantic BaseModel, the Pydantic
    validation process will appropriately run inputs through this class' constructor and dispatch to specific URI type.

    This class is a subclass of str. It can be used as a normal string safely.

    Notes:
        This class is, in fact, an abstract class. It is never instantiated directly but always defers to a subclass. It does not inherit from ABC due to compatibility issues between abstract classes and the str type.

    Examples:
        >>> AnyUri("https://example.com/1.jpg")
        HttpUri("https://example.com/1.jpg")

        >>> AnyUri("gs://bucket/1.jpg")
        GSUri("gs://bucket/1.jpg")

        >>> AnyUri("https://storage.googleapis.com/bucket/1.jpg")
        GSUri("gs://bucket/1.jpg")

        >>> AnyUri("file:///1.jpg")
        FileUri("file://localhost/1.jpg")

        >>> AnyUri("file://localhost/1.jpg")
        FileUri("file://localhost/1.jpg")

        >>> AnyUri("/1.jpg")
        FileUri("file://localhost/1.jpg")

    Notes:
        It will convert all input to str first, so it is safe to pass in `pathlib.Path` or other types.

    Examples:
        >>> AnyUri(pathlib.Path("/1.jpg"))
        FileUri("file://localhost/1.jpg")

    """

    def __new__(cls, value: Any) -> AnyUri:
        return cls.validate(value)

    @cached_property
    def _parsed(self) -> ParseResult:
        return urlparse(self.as_uri())

    @property
    def scheme(self) -> str:
        """
        The scheme of the uri.
        """
        return self._parsed.scheme

    @property
    def netloc(self) -> str:
        """
        The netloc of the uri.
        """
        return self._parsed.netloc

    @property
    def path(self) -> str:
        """
        The path of the uri.
        """
        return self._parsed.path

    @property
    def params(self) -> str:
        """
        The params of the uri.
        """
        return self._parsed.params

    @property
    def query(self) -> str:
        """
        The query of the uri.
        """
        return self._parsed.query

    @property
    def fragment(self) -> str:
        """
        The fragment of the uri.
        """
        return self._parsed.fragment

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.as_uri()}")'

    def as_uri(self) -> str:
        """
        The uri representation of the uri, which is the more standard representation of the uri.

        Returns:
            uri representation of the uri

        Examples:
            >>> AnyUri("gs://bucket/1.jpg").as_uri()
            "gs://bucket/1.jpg"

            >>> AnyUri("https://example.com/1.jpg").as_uri()
            "https://example.com/1.jpg"

            >>> AnyUri("file:///1.jpg").as_uri()
            "file://localhost/1.jpg"
        """
        return self.as_source()

    def as_source(self) -> str:
        """
        The source representation of the URI, which is its most commonly used format, is compatible with the majority of tools. Furthermore, this representation is returned when using AnyUri as a string. This occurs, for example, when applying str(uri) or when the URI is directly utilized.

        Returns:
            source representation of the uri

        Examples:
            >>> AnyUri("gs://bucket/1.jpg").as_source()
            "https://storage.googleapis.com/bucket/1.jpg"

            >>> AnyUri("https://example.com/1.jpg").as_source()
            "https://example.com/1.jpg"

            >>> AnyUri("file:///1.jpg").as_source()
            "/1.jpg"

        Notes:
            The ffmpeg input URL, used as `ffmpeg -i URL`, accepts the source representation of the URI.

        """
        return str(self)

    # NOTE: this is a hack to make pydantic2 work with AnyUri
    @no_type_check
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        from pydantic_core import core_schema

        return core_schema.no_info_after_validator_function(
            cls.validate, core_schema.any_schema()
        )

    # NOTE: this is a hack to make pydantic work with AnyUri
    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> AnyUri:
        """
        Validates the uri and returns the uri.

        Args:
            value: uri to validate

        Returns:
            the uri

        Raises:
            UriSchemaError: if the uri cannot be validated by any of the subclasses
        """

        _sub_class: list[type[AnyUri]] = [GSUri, HttpUri, FileUri]
        v = str(value)
        for _cls in _sub_class:
            try:
                return _cls(v)
            except UriSchemaError:
                continue

        raise UriSchemaError(f"Invalid URI: {value}")


class HttpUri(AnyUri):
    """
    HttpUri is a URI that points to a HTTP resource. It accepts both http and https scheme.

    Examples:
        >>> HttpUri("https://example.com/1.jpg")
        HttpUri("https://example.com/1.jpg")

        >>> HttpUri("http://example.com/1.jpg")
        HttpUri("http://example.com/1.jpg")
    """

    def __new__(cls, value: Any) -> HttpUri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        p: ParseResult = urlparse(v)
        if p.scheme not in {"http", "https"}:
            raise UriSchemaError(f"Invalid scheme: {value}")
        return normalize_url(v)

    @classmethod
    def validate(cls, value: Any) -> HttpUri:
        value = cls._validate(value)
        return cls(value)


class FileUri(AnyUri):
    """
    FileUri is a URI that points to a local file. It accepts both str, pathlib.Path and file:// scheme.

    Examples:
        >>> FileUri("file:///1.jpg")
        FileUri("file://localhost/1.jpg")

        >>> FileUri("file://localhost/1.jpg")
        FileUri("file://localhost/1.jpg")

        >>> FileUri("/1.jpg")
        FileUri("file://localhost/1.jpg")

        >>> FileUri(pathlib.Path("/1.jpg"))
        FileUri("file://localhost/1.jpg")

    NOTE:
        FileUri will ignore the `query`, `fragment`, and `params` part of the uri
    """

    def __new__(cls, value: Any) -> FileUri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)

        if "://" not in v:
            # NOTE: it is a local path
            path = pathlib.Path(v)
            v = path.resolve().as_uri()

        p: ParseResult = urlparse(v)

        if p.scheme not in {"file"}:
            raise UriSchemaError(f"Invalid scheme: {value}")
        if p.netloc not in {"", "localhost"}:
            raise UriSchemaError(f"Invalid netloc: {value}")
        return uri_to_path(v)

    @classmethod
    def validate(cls, value: Any) -> FileUri:
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        return f"file://localhost{self}"


class GSUri(AnyUri):
    """
    GSUri is a URI that points to a Google Cloud Storage resource. It accepts both gs and https scheme.

    Examples:
        >>> GSUri("gs://bucket/1.jpg")
        GSUri("gs://bucket/1.jpg")

        >>> GSUri("https://storage.googleapis.com/bucket/1.jpg")
        GSUri("gs://bucket/1.jpg")

    NOTE:
        GSUri will ignore the `query`, `fragment`, and `params` part of the uri
    """

    def __new__(cls, value: Any) -> GSUri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        p: ParseResult = urlparse(v)
        if p.scheme in {"http", "https"}:
            if p.netloc != "storage.googleapis.com":
                raise UriSchemaError(f"Invalid netloc: {value}")

            return urlunparse(
                (
                    "https",
                    "storage.googleapis.com",
                    p.path,
                    p.params,
                    p.query,
                    p.fragment,
                )
            )
        if p.scheme == "gs":
            return urlunparse(
                (
                    "https",
                    "storage.googleapis.com",
                    f"{p.netloc}{p.path}",
                    p.params,
                    p.query,
                    p.fragment,
                )
            )

        raise UriSchemaError(f"Invalid GSUri: {value}")

    @classmethod
    def validate(cls, value: Any) -> GSUri:
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        return self.replace("https://storage.googleapis.com/", "gs://")


__all__ = ["AnyUri", "HttpUri", "FileUri", "GSUri"]

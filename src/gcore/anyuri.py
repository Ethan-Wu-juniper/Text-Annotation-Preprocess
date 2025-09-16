from __future__ import annotations

import os
import pathlib
from typing import Any, Callable, Generator
from urllib.parse import ParseResult, unquote, urlparse
from urllib.request import url2pathname

from pydantic import parse_obj_as

AnyCallable = Callable[..., Any]
CallableGenerator = Generator[AnyCallable, None, None]


def uri_to_path(uri: str) -> str:
    # https://stackoverflow.com/questions/5977576/is-there-a-convenient-way-to-map-a-file-uri-to-os-path
    parsed = urlparse(uri)
    host = "{0}{0}{mnt}{0}".format(os.path.sep, mnt=parsed.netloc)
    return os.path.normpath(os.path.join(host, url2pathname(unquote(parsed.path))))


class AnyUri(str):
    @classmethod
    def __get_validators__(cls) -> CallableGenerator:
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls._validate

    @classmethod
    def _validate(cls, value: Any) -> AnyUri:
        """Used as a Pydantic validator. See
        https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types"""

        _sub_class: list[type[AnyUri]] = [GSUri, HttpUri, FileUri]
        value = str(value)

        for _cls in _sub_class:
            try:
                # FIXME:
                if _cls == FileUri:
                    if "://" not in value:
                        p = pathlib.Path(value)
                        return parse_obj_as(FileUri, p.resolve().as_uri())

                return parse_obj_as(_cls, value)
            except ValueError:
                continue

        raise ValueError(f"Invalid URI: {value}")

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.as_uri()}")'

    def as_uri(self) -> str:
        return self.as_source()

    def as_source(self) -> str:
        raise NotImplementedError(f"{self.__class__} not implemented as_source")


class HttpUri(AnyUri):
    @classmethod
    def _validate(cls, value: Any) -> HttpUri:
        p = urlparse(value)
        assert p.scheme in {"http", "https"}, f"Invalid scheme: {value}"
        return cls(value)

    def as_source(self) -> str:
        return str(self)


class FileUri(AnyUri):
    @classmethod
    def _validate(cls, value: Any) -> FileUri:
        p = urlparse(value)
        if p.scheme == "file":
            assert p.netloc in {"", "localhost"}, f"Invalid netloc: {value}"
            return cls(uri_to_path(value))

        assert not p.scheme, f"Invalid scheme: {value}"
        return cls(uri_to_path(f"file://localhost{value}"))

    def as_source(self) -> str:
        return str(self)

    def as_uri(self) -> str:
        return f"file://localhost{self}"


class GSUri(AnyUri):
    @classmethod
    def _validate(cls, value: Any) -> GSUri:
        p: ParseResult = urlparse(value)

        if p.scheme in {"http", "https"}:
            if p.netloc == "storage.googleapis.com":
                query = ""
                if p.query:
                    query = f"?{p.query}"
                return cls(
                    "https://storage.googleapis.com/" + p.path.lstrip("/") + query
                )

            raise ValueError(f"Invalid netloc: {value}")

        if p.scheme == "gs":
            return cls(
                f"https://storage.googleapis.com/{p.netloc}/" + p.path.lstrip("/")
            )

        raise ValueError(f"Invalid scheme: {value}")

    def as_source(self) -> str:
        return str(self)

    def as_uri(self) -> str:
        return self.replace("https://storage.googleapis.com/", "gs://")

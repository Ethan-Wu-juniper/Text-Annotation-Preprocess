import re
from distutils import version

import pydantic


class APPConfig(pydantic.BaseSettings):
    application: str = pydantic.Field(env="APP_NAME", default="foo-application")
    version: str = pydantic.Field(env="APP_VERSION", default="0.0.1a0")
    instance: str = pydantic.Field(env="HOSTNAME", default="localhost")

    @pydantic.validator("application")
    def application_validate(cls, v: str) -> str:
        if not re.match(r"^[\w\-]+$", v):
            raise ValueError(f"application format not correct {v}")
        return v

    @pydantic.validator("version")
    def version_validate(cls, v: str) -> str:
        version.StrictVersion(v)
        return v

    @pydantic.validator("instance")
    def instance_validate(cls, v: str) -> str:
        if not re.match(r"^[\w\-\.\:]+$", v):
            raise ValueError(f"instance format not correct {v}")
        return v

    @property
    def is_staging(self) -> bool:
        return "a" in self.version or "b" in self.version


app: APPConfig = APPConfig()

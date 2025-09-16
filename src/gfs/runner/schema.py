"""
It is mainly for backward compatibility with the old genv-fs schema.
"""

from typing import Any

from pydantic import BaseModel


class RunnerResult(BaseModel):
    """
    The result of a command run by the runner.
    It is for backward compatibility with the old schema.
    """

    cmd: list[str]
    """
    The command that was run.
    """
    stdout: str | None = None
    """
    The standard output of the command.
    """
    stderr: str | None = None
    """
    The standard error of the command.
    """

    output: Any = None
    """
    The output of the command.
    """
    exit_code: int = 0
    """
    The exit code of the command.
    """

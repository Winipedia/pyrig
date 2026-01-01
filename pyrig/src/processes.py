"""Operating system utilities.

Subprocess execution with enhanced error logging and command path discovery.
Used throughout pyrig for running external tools (git, uv, pytest, pre-commit).

Utilities:
    - which_with_raise: Find executable paths with optional error raising
    - run_subprocess: Execute commands with detailed error logging

Example:
    >>> from pyrig.src.os.os import run_subprocess, which_with_raise
    >>> which_with_raise("uv")  # '/usr/bin/uv'
    >>> run_subprocess(["uv", "sync"])
"""

import logging
import subprocess  # nosec: B404
from collections.abc import Sequence
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def run_subprocess(  # noqa: PLR0913
    args: Sequence[str],
    *,
    input_: str | bytes | None = None,
    capture_output: bool = True,
    timeout: int | None = None,
    check: bool = True,
    cwd: str | Path | None = None,
    **kwargs: Any,
) -> subprocess.CompletedProcess[Any]:
    """Execute subprocess with enhanced error logging.

    Wrapper around subprocess.run() that logs command, exit code, stdout, and stderr
    on failure before re-raising exception.

    Args:
        args: Command and arguments as sequence (e.g., ["git", "status"]).
        input_: Optional data to send to stdin (string or bytes).
        capture_output: If True (default), captures stdout/stderr.
        timeout: Maximum seconds to wait. None (default) means no timeout.
        check: If True (default), raises CalledProcessError on non-zero exit.
        cwd: Working directory. Defaults to current directory.
        **kwargs: Additional arguments passed to subprocess.run().

    Returns:
        CompletedProcess with args, returncode, stdout, stderr.

    Raises:
        subprocess.CalledProcessError: If process returns non-zero exit and check=True.
        subprocess.TimeoutExpired: If process exceeds timeout.

    Example:
        >>> run_subprocess(["git", "status"])
        >>> run_subprocess(["false"], check=False).returncode  # 1
    """
    if cwd is None:
        cwd = Path.cwd()
    try:
        result = subprocess.run(  # noqa: S603  # nosec: B603
            args,
            check=check,
            input=input_,
            capture_output=capture_output,
            timeout=timeout,
            cwd=cwd,
            **kwargs,
        )
    except subprocess.CalledProcessError as e:
        logger.exception(
            "Command failed: %s (exit code %d)\nstdout: %s\nstderr: %s",
            args,
            e.returncode,
            e.stdout.decode("utf-8"),
            e.stderr.decode("utf-8"),
        )
        raise
    else:
        return result


class Args(tuple[str, ...]):
    """Command-line arguments container with execution capabilities.

    Immutable tuple subclass representing command arguments.
    Return type for all Tool methods.

    Methods:
        __str__: Convert to space-separated string
        run: Execute via subprocess

    Example:
        >>> args = Args(("uv", "sync"))
        >>> print(args)
        uv sync
        >>> args.run()
        CompletedProcess(...)
    """

    __slots__ = ()

    def __str__(self) -> str:
        """Convert to space-separated string.

        Returns:
            Space-separated command string.
        """
        return " ".join(self)

    def run(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        """Execute command via subprocess.

        Args:
            *args: Additional arguments appended to command.
            **kwargs: Keyword arguments passed to run_subprocess
                (check, capture_output, cwd, etc.).

        Returns:
            CompletedProcess from subprocess execution.

        Raises:
            subprocess.CalledProcessError: If check=True and command fails.
        """
        return run_subprocess(self, *args, **kwargs)

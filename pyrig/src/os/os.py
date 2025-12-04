"""Operating system utilities for subprocess execution and command discovery.

This module provides utilities for working with the operating system,
including subprocess execution with enhanced error logging and command
path discovery. These utilities are used throughout pyrig for running
external tools like git, uv, and pre-commit.

Example:
    >>> from pyrig.src.os.os import run_subprocess, which_with_raise
    >>> uv_path = which_with_raise("uv")
    >>> result = run_subprocess(["uv", "sync"])
"""

import logging
import shutil
import subprocess  # nosec: B404
from collections.abc import Sequence
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def which_with_raise(cmd: str, *, raise_error: bool = True) -> str | None:
    """Find the path to an executable command.

    A wrapper around `shutil.which()` that optionally raises an exception
    if the command is not found, rather than silently returning None.

    Args:
        cmd: The command name to find (e.g., "git", "uv", "python").
        raise_error: If True (default), raises FileNotFoundError when the
            command is not found. If False, returns None instead.

    Returns:
        The absolute path to the command executable, or None if not found
        and `raise_error` is False.

    Raises:
        FileNotFoundError: If the command is not found and `raise_error` is True.

    Example:
        >>> which_with_raise("git")
        '/usr/bin/git'
        >>> which_with_raise("nonexistent", raise_error=False)
        None
    """
    path = shutil.which(cmd)
    if path is None:
        msg = f"Command {cmd} not found"
        if raise_error:
            raise FileNotFoundError(msg)
    return path


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
    """Execute a subprocess with enhanced error logging.

    A wrapper around `subprocess.run()` that provides detailed logging when
    a subprocess fails. On failure, logs the command arguments, return code,
    stdout, and stderr before re-raising the exception.

    Args:
        args: The command and arguments to execute (e.g., ["git", "status"]).
        input_: Data to send to the subprocess's stdin.
        capture_output: If True (default), captures stdout and stderr.
        timeout: Maximum seconds to wait for the process to complete.
        check: If True (default), raises CalledProcessError on non-zero exit.
        cwd: Working directory for the subprocess. Defaults to current directory.
        **kwargs: Additional arguments passed to `subprocess.run()`.

    Returns:
        A CompletedProcess instance with return code, stdout, and stderr.

    Raises:
        subprocess.CalledProcessError: If the process returns non-zero exit
            code and `check` is True. The exception is logged with full
            details before being re-raised.
        subprocess.TimeoutExpired: If the process exceeds `timeout`.

    Example:
        >>> result = run_subprocess(["git", "status"])
        >>> print(result.stdout.decode())
        On branch main...
    """
    if cwd is None:
        cwd = Path.cwd()
    try:
        return subprocess.run(  # noqa: S603  # nosec: B603
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
            """
Failed to run subprocess:
    args: %s
    returncode: %s
    stdout: %s
    stderr: %s
""",
            args,
            e.returncode,
            e.stdout.decode("utf-8"),
            e.stderr.decode("utf-8"),
        )
        raise

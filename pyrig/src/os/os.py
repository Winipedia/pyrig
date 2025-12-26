"""Operating system utilities for subprocess execution and command discovery.

This module provides utilities for working with the operating system,
including subprocess execution with enhanced error logging and command path
discovery. These utilities are used throughout pyrig for running external
tools like git, uv, pytest, and pre-commit.

The module provides two main utilities:
    - **which_with_raise**: Find executable paths with optional error raising
    - **run_subprocess**: Execute commands with detailed error logging

The enhanced error logging in `run_subprocess` is particularly valuable for
debugging failed commands, as it logs the full command, exit code, stdout,
and stderr before re-raising the exception.

Example:
    >>> from pyrig.src.os.os import run_subprocess, which_with_raise
    >>> # Find command path
    >>> uv_path = which_with_raise("uv")
    >>> print(uv_path)
    '/usr/bin/uv'
    >>>
    >>> # Run command with automatic error logging
    >>> result = run_subprocess(["uv", "sync"])
    >>> result.returncode
    0
    >>>
    >>> # Run command that might fail
    >>> try:
    ...     run_subprocess(["false"])  # Command that always fails
    ... except subprocess.CalledProcessError as e:
    ...     print(f"Command failed with exit code {e.returncode}")

See Also:
    pyrig.src.management.base.base.Args: Uses run_subprocess for execution
    pyrig.src.management: Tool wrappers that use these utilities
"""

import logging
import shutil
import subprocess  # nosec: B404
from collections.abc import Sequence
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def which_with_raise(cmd: str, *, raise_error: bool = True) -> str | None:
    """Find the path to an executable command with optional error raising.

    A wrapper around `shutil.which()` that optionally raises an exception
    if the command is not found, rather than silently returning None. This
    is useful for validating that required tools are installed before
    attempting to use them.

    The function searches for the command in the system PATH and returns
    the absolute path to the executable if found.

    Args:
        cmd: The command name to find (e.g., "git", "uv", "python", "pytest").
            This should be the bare command name without path or extension.
        raise_error: If True (default), raises FileNotFoundError when the
            command is not found. If False, returns None instead, allowing
            the caller to handle the missing command gracefully.

    Returns:
        The absolute path to the command executable as a string, or None if
        the command is not found and `raise_error` is False.

    Raises:
        FileNotFoundError: If the command is not found in PATH and
            `raise_error` is True. The error message includes the command name.

    Example:
        Basic usage::

            >>> which_with_raise("git")
            '/usr/bin/git'

        Handling missing commands::

            >>> which_with_raise("nonexistent", raise_error=False)
            None

        Validating required tools::

            >>> try:
            ...     uv_path = which_with_raise("uv")
            ... except FileNotFoundError:
            ...     print("Please install uv: pip install uv")

    Note:
        The function uses `shutil.which()` internally, which respects the
        system PATH and platform-specific executable extensions (e.g., .exe
        on Windows).

    See Also:
        run_subprocess: Execute commands found with this function
        shutil.which: Underlying implementation
    """
    path = shutil.which(cmd)
    if path is None:
        logger.debug("Command not found: %s", cmd)
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
    stdout, and stderr before re-raising the exception. This makes debugging
    failed commands much easier.

    The function is used throughout pyrig for running external tools like git,
    uv, pytest, and pre-commit. The enhanced logging is particularly valuable
    in CI environments where you can't interactively debug failures.

    Args:
        args: The command and arguments to execute as a sequence of strings
            (e.g., ["git", "status"], ["uv", "sync"]). The first element is
            the command name, and subsequent elements are arguments.
        input_: Optional data to send to the subprocess's stdin. Can be a
            string or bytes. If provided, it's sent to the process and stdin
            is closed.
        capture_output: If True (default), captures stdout and stderr and
            makes them available in the returned CompletedProcess object.
            If False, output goes to the parent process's stdout/stderr.
        timeout: Maximum seconds to wait for the process to complete. If the
            process doesn't finish within this time, TimeoutExpired is raised.
            None (default) means no timeout.
        check: If True (default), raises CalledProcessError if the process
            returns a non-zero exit code. If False, the function returns
            normally regardless of exit code.
        cwd: Working directory for the subprocess. Can be a string or Path.
            Defaults to the current working directory if not specified.
        **kwargs: Additional keyword arguments passed directly to
            `subprocess.run()`. Common options include env, shell, etc.

    Returns:
        A CompletedProcess instance containing:
            - args: The command that was run
            - returncode: Exit code of the process
            - stdout: Captured stdout (if capture_output=True)
            - stderr: Captured stderr (if capture_output=True)

    Raises:
        subprocess.CalledProcessError: If the process returns a non-zero exit
            code and `check` is True. Before re-raising, the exception is
            logged with full details (command, exit code, stdout, stderr).
        subprocess.TimeoutExpired: If the process exceeds the specified
            `timeout` duration.

    Example:
        Basic command execution::

            >>> result = run_subprocess(["git", "status"])
            >>> print(result.stdout.decode())
            On branch main...

        With input::

            >>> result = run_subprocess(
            ...     ["python", "-c", "import sys; print(sys.stdin.read())"],
            ...     input_="Hello, World!"
            ... )

        Without error checking::

            >>> result = run_subprocess(["false"], check=False)
            >>> result.returncode
            1

        With timeout::

            >>> result = run_subprocess(["sleep", "10"], timeout=5)
            # Raises TimeoutExpired after 5 seconds

    Note:
        - The function always uses the current working directory if `cwd` is
          not specified
        - Error logging includes decoded stdout/stderr, which assumes UTF-8
          encoding
        - The function is marked with security linters (nosec, noqa) because
          subprocess execution is inherently risky, but the usage here is
          controlled

    See Also:
        pyrig.src.management.base.base.Args.run: Uses this for execution
        subprocess.run: Underlying implementation
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

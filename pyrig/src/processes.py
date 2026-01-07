"""Subprocess execution utilities with enhanced error handling.

Core module for running external tools (git, uv, pytest, pre-commit) throughout pyrig.
Provides consistent subprocess execution with automatic error logging and a fluent
command-building interface.

Utilities:
    run_subprocess: Execute commands with detailed error logging on failure.
    Args: Immutable command container returned by all Tool.get_*_args methods.

Example:
    >>> from pyrig.src.processes import run_subprocess, Args
    >>> run_subprocess(["uv", "sync"])
    >>> Args(("git", "status")).run()
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
    shell: bool = False,
    text: bool = True,
    **kwargs: Any,
) -> subprocess.CompletedProcess[Any]:
    """Execute subprocess with enhanced error logging.

    Wrapper around subprocess.run() that logs command, exit code, stdout, and stderr
    when CalledProcessError is raised, before re-raising the exception. Used as the
    underlying execution mechanism for all Tool command wrappers (PackageManager,
    Linter, ContainerEngine, etc.).

    Args:
        args: Command and arguments as sequence (e.g., ["git", "status"]).
        input_: Data to send to stdin (string or bytes). Defaults to None.
        capture_output: If True (default), captures stdout/stderr.
        timeout: Maximum seconds to wait. None (default) means no timeout.
        check: If True (default), raises CalledProcessError on non-zero exit.
        cwd: Working directory. Defaults to current directory.
        shell: Must be False. Raises ValueError if True (shell mode is
            forbidden in pyrig for security reasons).
        text: If True (default), stdout and stderr are decoded as text.
        **kwargs: Additional arguments passed to subprocess.run().

    Returns:
        CompletedProcess with args, returncode, stdout, stderr.

    Raises:
        ValueError: If shell=True is passed.
        subprocess.CalledProcessError: If process returns non-zero exit and check=True.
            Error details are logged before re-raising.
        subprocess.TimeoutExpired: If process exceeds timeout.

    Example:
        >>> run_subprocess(["git", "status"])
        >>> run_subprocess(["false"], check=False).returncode  # 1
    """
    if shell:
        msg = "For security reasons shell mode is forbidden."
        raise ValueError(msg)
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
            shell=False,
            text=text,
            **kwargs,
        )
    except subprocess.CalledProcessError as e:
        logger.exception(
            "Command failed: %s (exit code %d)\nstdout: %s\nstderr: %s",
            args,
            e.returncode,
            e.stdout,
            e.stderr,
        )
        raise
    else:
        return result


class Args(tuple[str, ...]):
    """Immutable command-line arguments container with execution capabilities.

    Tuple subclass representing a complete command ready for execution.
    Returned by all Tool.get_*_args methods (e.g., PackageManager.get_sync_args,
    Linter.get_check_args) to provide a consistent interface for building, inspecting,
    and executing subprocess commands.

    The class enables a fluent API pattern where commands can be built incrementally
    and then either inspected as strings or executed via subprocess.

    Example:
        >>> args = Args(["uv", "sync"])
        >>> print(args)  # uv sync
        >>> args.run()   # Executes the command
        CompletedProcess(args=['uv', 'sync'], returncode=0, ...)
    """

    __slots__ = ()

    def __str__(self) -> str:
        """Convert to space-separated string.

        Returns:
            Space-separated command string.
        """
        return " ".join(self)

    def __repr__(self) -> str:
        """Return space-separated string representation.

        Delegates to __str__ for consistent display in REPL and debugging.

        Returns:
            Space-separated command string (same as __str__).
        """
        return str(self)

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
        return run_subprocess((*self, *args), **kwargs)

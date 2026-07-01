"""Utilities for safe subprocess execution."""

import logging
import subprocess  # nosec: B404
from collections.abc import Sequence
from functools import cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Args(tuple[str, ...]):
    """Immutable sequence of command-line tokens that can execute itself."""

    __slots__ = ()

    def __str__(self) -> str:
        """Return the command as a single space-separated string."""
        return " ".join(self)

    def run(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        """Execute the command with any extra positional arguments appended.

        Args:
            *args: Additional arguments to append to the command before execution.
            **kwargs: Keyword arguments forwarded to the subprocess runner.

        Returns:
            The completed process result.
        """
        return run_subprocess((*self, *args), **kwargs)

    def run_cached(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        """Execute the command, caching the result for identical arguments.

        Args:
            *args: Additional arguments to append to the command before execution.
            **kwargs: Keyword arguments forwarded to the subprocess runner.
                All values must be hashable.

        Returns:
            The completed process result.
        """
        return run_subprocess_cached((*self, *args), tuple(sorted(kwargs.items())))


@cache
def run_subprocess_cached(
    args: tuple[str, ...], kwargs: tuple[tuple[str, Any], ...] = ()
) -> subprocess.CompletedProcess[Any]:
    """Execute a subprocess command and cache the result.

    Repeated calls with identical arguments return the cached result without
    spawning a new process.

    Args:
        args: Command and arguments as a tuple (e.g., `("git", "status")`).
        kwargs: Keyword arguments forwarded to the subprocess runner as a
            sorted tuple of ``(key, value)`` pairs. All values must be
            hashable. Pass ``tuple(sorted(kwargs.items()))`` from the caller.

    Returns:
        The completed process result.
    """
    return run_subprocess(args, **dict(kwargs))


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
    """Execute a subprocess command with automatic failure logging.

    Forbids `shell=True` to prevent shell-injection vulnerabilities. When
    `subprocess.CalledProcessError` is raised, logs the command, exit code,
    stdout, and stderr at `ERROR` level before re-raising.

    Args:
        args: Command and arguments as a sequence (e.g., `["git", "status"]`).
        input_: Data sent to stdin.
        capture_output: When `True` (the default), captures stdout and stderr.
        timeout: Maximum seconds to wait. `None` means no limit.
        check: When `True` (the default), raises `subprocess.CalledProcessError`
            on non-zero exit.
        cwd: Working directory for the subprocess. Defaults to the current
            directory when `None`.
        shell: Must be `False`. Passing `True` raises `ValueError` immediately.
        text: When `True` (the default), decodes stdout and stderr as strings.
        **kwargs: Additional keyword arguments forwarded to `subprocess.run`.

    Returns:
        The completed process result.

    Raises:
        ValueError: If `shell=True` is passed.
        subprocess.CalledProcessError: If the process exits with a non-zero
            return code and `check=True`.
        subprocess.TimeoutExpired: If the process exceeds `timeout`.
    """
    if shell:
        msg = f"{shell=} is forbidden for security reasons."
        raise ValueError(msg)
    if cwd is None:
        cwd = Path()
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

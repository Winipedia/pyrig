"""Subprocess execution with shell-injection guards and result caching.

Provides a thin wrapper around the standard `subprocess` module that
enforces `shell=False`, logs failures automatically, and exposes an immutable
command container with a fluent execution interface.
"""

import logging
import subprocess  # nosec: B404
from collections.abc import Sequence
from functools import cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Args(tuple[str, ...]):
    """Immutable command-line argument container with execution capabilities.

    A `tuple` subclass that represents a complete subprocess command.
    Returned by every `Tool.*_args` method (e.g., `args` on a [Tool][] subclass)
    to provide a consistent interface for building, inspecting, and running
    subprocess commands.

    Example:
        >>> args = Args(["uv", "sync"])
        >>> str(args)
        'uv sync'
    """

    __slots__ = ()

    def __str__(self) -> str:
        """Return the command as a single space-separated string."""
        return " ".join(self)

    def run(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        """Execute the command via subprocess.

        Appends any extra positional arguments to the command, then passes the
        combined command to [run_subprocess][].

        Args:
            *args: Additional arguments to append to the command.
            **kwargs: Keyword arguments forwarded to [run_subprocess][]
                (e.g., `check`, `capture_output`, `cwd`).

        Returns:
            The completed process from the subprocess call.

        Raises:
            subprocess.CalledProcessError: If `check=True` and the command
                exits with a non-zero return code.
        """
        return run_subprocess((*self, *args), **kwargs)

    def run_cached(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        """Execute the command via a cached subprocess call.

        Identical to [run][Args.run], but uses [run_subprocess_cached][] so that
        repeated calls with the same arguments return the cached result without
        spawning a new process. Useful for idempotent read commands (e.g.,
        `git config`) that are invoked many times during a session.

        Args:
            *args: Additional arguments to append to the command.
            **kwargs: Keyword arguments forwarded to [run_subprocess_cached][]
                (e.g., `check`, `capture_output`, `cwd`). All values must
                be hashable.

        Returns:
            The completed process from the subprocess call.

        Raises:
            subprocess.CalledProcessError: If `check=True` and the command
                exits with a non-zero return code.
        """
        return run_subprocess_cached((*self, *args), **kwargs)


@cache
def run_subprocess_cached(
    args: tuple[str, ...], **kwargs: Any
) -> subprocess.CompletedProcess[Any]:
    """Execute a subprocess command and cache the result.

    A `functools.cache`-backed wrapper around [run_subprocess][]. Because the
    cache key is derived from the arguments, `args` must be a `tuple` (hashable)
    rather than a list, and all `kwargs` values must also be hashable (e.g.,
    `bool`, `int`, `str`, `None`).

    Caching avoids redundant process spawning for idempotent commands such as
    `git config --get remote.origin.url` that are called multiple times within
    a single session. The cache persists for the lifetime of the process.

    Args:
        args: Command and arguments as a tuple (e.g., `("git", "status")`).
        **kwargs: Keyword arguments forwarded to [run_subprocess][].
            All values must be hashable.

    Returns:
        The completed process with the command output. On repeated calls with
        identical arguments the cached instance is returned without spawning a
        new process.

    Raises:
        subprocess.CalledProcessError: If the command exits with a non-zero
            return code and `check=True` (the default).
        subprocess.TimeoutExpired: If the process exceeds the configured timeout.
    """
    return run_subprocess(args, **kwargs)


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

    A thin wrapper around `subprocess.run` that:

    * Forbids `shell=True` to prevent shell-injection vulnerabilities.
    * Logs the command, exit code, stdout, and stderr at `ERROR` level
      whenever `subprocess.CalledProcessError` is raised, then re-raises.
    * Defaults `cwd` to the current directory when not provided.

    This is the underlying execution primitive used by all [Tool][] wrappers.

    Args:
        args: Command and arguments as a sequence (e.g., `["git", "status"]`).
        input_: Data sent to stdin.
        capture_output: Capture stdout and stderr.
        timeout: Maximum seconds to wait before raising
            `subprocess.TimeoutExpired`. `None` means no limit.
        check: Raise `subprocess.CalledProcessError` on non-zero exit.
        cwd: Working directory for the subprocess. Defaults to the current
            directory.
        shell: Must be `False`. Passing `True` raises `ValueError`
            immediately, as shell execution is forbidden for security reasons.
        text: Decode stdout and stderr as text strings.
        **kwargs: Additional keyword arguments forwarded to `subprocess.run`.

    Returns:
        The completed process with `args`, `returncode`, `stdout`, and
        `stderr`.

    Raises:
        ValueError: If `shell=True` is passed.
        subprocess.CalledProcessError: If the process exits with a non-zero
            return code and `check=True`. Failure details are logged before
            re-raising.
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

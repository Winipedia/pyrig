"""Utilities for safe subprocess execution."""

import logging
import subprocess  # nosec: B404
from collections.abc import Sequence
from functools import cache
from pathlib import Path
from typing import Any, Self

logger = logging.getLogger(__name__)


class Args(tuple[str, ...]):
    """Immutable sequence of command-line tokens that can execute itself.

    Each token is one argument, so a value containing spaces stays a single
    token and is never shell-quoted.
    When converted to a string, the tokens are joined with spaces to
    form a single command.

    Example:
        >>> args = Args("git", "commit", "-m", "my commit message")
        >>> args == ("git", "commit", "-m", "my commit message")
        True
        >>> str(args)
        'git commit -m my commit message'
    """

    __slots__ = ()

    def __new__(cls, *args: str) -> Self:
        """Create an `Args` instance from individual string tokens.

        Args:
            *args: Command-line tokens.

        Returns:
            New `Args` instance containing the given tokens.
        """
        return super().__new__(cls, args)

    def __getnewargs__(self) -> tuple[str, ...]:
        """Return the constructor arguments used to rebuild this instance.

        `copy.copy`, `copy.deepcopy`, and `pickle` reconstruct immutable objects
        by calling `Args(*result)`. The inherited `tuple.__getnewargs__` wraps the
        tokens in a single tuple to match `tuple.__new__`, but `__new__` takes the
        tokens as varargs, so the tokens must be returned unwrapped instead.

        Returns:
            The individual tokens, so `Args(*tokens)` rebuilds this instance.
        """
        return tuple(self)

    def __str__(self) -> str:
        """Return the command as a single space-separated string."""
        return " ".join(self)

    def run(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        """Execute the command with any extra positional arguments appended.

        Args:
            *args: Additional command-line arguments appended to the command.
            **kwargs: Keyword arguments forwarded to the subprocess runner.

        Returns:
            The completed process result.
        """
        return run_subprocess((*self, *args), **kwargs)

    def run_cached(self, *args: str, **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        """Execute the command, caching the result for identical arguments.

        Args:
            *args: Additional command-line arguments appended to the command.
            **kwargs: Keyword arguments forwarded to the subprocess runner.
                All values must be hashable.

        Returns:
            The completed process result.
        """
        return run_subprocess_cached((*self, *args), **kwargs)


@cache
def run_subprocess_cached(
    args: tuple[str, ...], **kwargs: Any
) -> subprocess.CompletedProcess[Any]:
    """Execute a subprocess command and cache the result.

    Repeated calls with identical arguments return the cached result without
    spawning a new process.

    Args:
        args: Command and arguments as a tuple (e.g., `("git", "status")`).
        **kwargs: Keyword arguments forwarded to the subprocess runner.
            All values must be hashable.

    Returns:
        The completed process result.
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

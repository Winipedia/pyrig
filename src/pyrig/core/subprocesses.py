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

    def __str__(self) -> str:
        """Return the command as a single space-separated string."""
        return " ".join(self)

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


@cache
def run_subprocess_cached(
    args: tuple[str, ...],
    **kwargs: Any,
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


def run_subprocess(
    args: Sequence[str],
    *,
    check: bool = True,
    **kwargs: Any,
) -> subprocess.CompletedProcess[Any]:
    """Execute a subprocess command with automatic failure logging.

    The command always runs without a shell in the current working directory,
    capturing stdout and stderr and decoding them as text. On a non-zero exit
    with `check=True`, the command, exit code, stdout, and stderr are logged at
    `ERROR` level before the error propagates.

    Args:
        args: Command and arguments as a sequence (e.g., `["git", "status"]`).
        check: When `True` (the default), raise `subprocess.CalledProcessError`
            on a non-zero exit.
        **kwargs: Additional keyword arguments forwarded to `subprocess.run`.

    Returns:
        The completed process, with `stdout` and `stderr` as decoded strings.

    Raises:
        subprocess.CalledProcessError: If the command exits with a non-zero
            return code and `check` is `True`.
    """
    try:
        result = subprocess.run(  # noqa: S603  # nosec: B603
            args,
            check=check,
            capture_output=True,
            cwd=Path(),
            shell=False,
            text=True,
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

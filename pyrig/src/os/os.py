"""OS utilities for finding commands and paths.

This module provides utility functions for working with the operating system,
including finding the path to commands and managing environment variables.
These utilities help with system-level operations and configuration.
"""

import logging
import shutil
import subprocess  # nosec: B404
from collections.abc import Sequence
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def which_with_raise(cmd: str, *, raise_error: bool = True) -> str | None:
    """Give the path to the given command.

    Args:
        cmd: The command to find
        raise_error: Whether to raise an error if the command is not found

    Returns:
        The path to the command

    Raises:
        FileNotFoundError: If the command is not found

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
    """Run a subprocess.

    Args:
        args: The arguments to pass to the subprocess
        input_: The input to pass to the subprocess
        capture_output: Whether to capture the output of the subprocess
        timeout: The timeout for the subprocess
        check: to raise an exception if the subprocess returns a non-zero exit code
        cwd: The working directory to run the subprocess in
        kwargs: Any other arguments to pass to subprocess.run()

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

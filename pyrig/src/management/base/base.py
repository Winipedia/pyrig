"""Project management utilities for Python projects.

This module provides utilities for managing Python projects using various tools
including uv (package manager), git (version control), pre-commit (code quality),
and podman (containerization). It centralizes command construction for common
project management tasks.
"""

import logging
from abc import ABC, abstractmethod
from subprocess import CompletedProcess  # nosec: B404
from typing import Any

from pyrig.src.os.os import run_subprocess

logger = logging.getLogger(__name__)


class Args(tuple[str, ...]):
    """Command-line arguments container with execution capabilities.

    A tuple subclass that represents command-line arguments and provides
    convenient methods for string representation and subprocess execution.
    """

    __slots__ = ()

    def __str__(self) -> str:
        """Convert arguments to a space-separated string.

        Returns:
            str: Space-separated string of all arguments.
        """
        return " ".join(self)

    def run(self, *args: str, **kwargs: Any) -> CompletedProcess[Any]:
        """Execute the command represented by these arguments.

        Args:
            *args: Additional positional arguments to pass to run_subprocess.
            **kwargs: Additional keyword arguments to pass to run_subprocess.

        Returns:
            CompletedProcess[Any]: The completed process result containing
                return code, stdout, and stderr.
        """
        return run_subprocess(self, *args, **kwargs)


class Tool(ABC):
    """Abstract base class for tool command argument construction.

    Subclasses must implement the ``name`` method to provide the tool name.
    They can then use the ``get_args`` method to construct command arguments
    starting with the tool name.
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Get the name of the tool.

        Returns:
            str: The name of the tool.
        """

    @classmethod
    def get_args(cls, *args: str) -> Args:
        """Construct base command arguments.

        Args:
            *args: Additional arguments to append to the command.

        Returns:
            Args: Command arguments starting with the tool name.
        """
        return Args((cls.name(), *args))

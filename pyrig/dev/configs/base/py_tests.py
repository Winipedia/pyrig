"""Configuration management for Python test files.

This module provides the PythonTestsConfigFile class for managing
Python test files in the tests directory.
"""

from pathlib import Path

from pyrig.dev.configs.base.python import PythonConfigFile
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


class PythonTestsConfigFile(PythonConfigFile):
    """Abstract base class for Python files in the tests directory."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the tests directory path.

        Returns:
            Path to the tests package.
        """
        return Path(TESTS_PACKAGE_NAME)

"""Configuration for the test_zero.py placeholder test.

This module provides the ZeroTestConfigFile class for creating
a minimal test file that ensures pytest runs even when no other
tests exist.
"""

from pyrig.dev.configs.base.base import PythonTestsConfigFile


class ZeroTestConfigFile(PythonTestsConfigFile):
    """Configuration file manager for test_zero.py.

    Creates a placeholder test file that ensures pytest runs
    successfully even when no other tests have been written.
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the test filename with reversed prefix.

        Returns:
            The string "test_zero" (reversed from "zero_test").
        """
        filename = super().get_filename()
        return "_".join(reversed(filename.split("_")))

    @classmethod
    def get_content_str(cls) -> str:
        """Get the placeholder test content.

        Returns:
            Python code with an empty test function.
        """
        return '''"""Contains an empty test."""


def test_zero() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
'''

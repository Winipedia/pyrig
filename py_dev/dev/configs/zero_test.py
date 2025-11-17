"""Config utilities for test_zero.py."""

from py_dev.dev.configs.base.base import PythonTestsConfigFile
from py_dev.utils.os.os import run_subprocess
from py_dev.utils.projects.poetry.poetry import get_poetry_run_module_args
from py_dev.utils.testing import create_tests


class ZeroTestConfigFile(PythonTestsConfigFile):
    """Config file for test_zero.py."""

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        filename = super().get_filename()
        return "_".join(reversed(filename.split("_")))

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config."""
        return '''"""Contains an empty test."""


def test_zero() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
'''

    @classmethod
    def create_tests(cls) -> None:
        """Create the tests."""
        run_subprocess(get_poetry_run_module_args(create_tests))

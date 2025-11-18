"""Config utilities for test_zero.py."""

from pyrig.dev.configs.base.base import PythonTestsConfigFile
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.poetry.poetry import get_poetry_run_module_args
from pyrig.src.testing import create_tests


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

"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.base.py_tests import PythonTestsConfigFile
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


@pytest.fixture
def my_test_python_tests_config_file(
    config_file_factory: Callable[
        [type[PythonTestsConfigFile]], type[PythonTestsConfigFile]
    ],
) -> type[PythonTestsConfigFile]:
    """Create a test python tests config file class with tmp_path."""

    class MyTestPythonTestsConfigFile(config_file_factory(PythonTestsConfigFile)):  # type: ignore [misc]
        """Test python tests config file with tmp_path override."""

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return '"""Test content."""\n'

    return MyTestPythonTestsConfigFile


class TestPythonTestsConfigFile:
    """Test class."""

    def test_get_parent_path(
        self, my_test_python_tests_config_file: type[PythonTestsConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        expected = Path(TESTS_PACKAGE_NAME)
        actual = my_test_python_tests_config_file.get_parent_path()
        assert actual == expected, f"Expected {expected}, got {actual}"

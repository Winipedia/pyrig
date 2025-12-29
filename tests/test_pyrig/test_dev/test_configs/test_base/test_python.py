"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.base.python import PythonConfigFile


@pytest.fixture
def my_test_python_config_file(
    config_file_factory: Callable[[type[PythonConfigFile]], type[PythonConfigFile]],
) -> type[PythonConfigFile]:
    """Create a test python config file class with tmp_path."""

    class MyTestPythonConfigFile(config_file_factory(PythonConfigFile)):  # type: ignore [misc]
        """Test python config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return '"""Test content."""\n'

    return MyTestPythonConfigFile


class TestPythonConfigFile:
    """Test class."""

    def test_get_file_extension(
        self, my_test_python_config_file: type[PythonConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        expected = "py"
        actual = my_test_python_config_file.get_file_extension()
        assert actual == expected, f"Expected {expected}, got {actual}"

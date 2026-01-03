"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.dev.configs.dot_python_version import DotPythonVersionConfigFile


@pytest.fixture
def my_test_dot_python_version_config_file(
    config_file_factory: Callable[
        [type[DotPythonVersionConfigFile]], type[DotPythonVersionConfigFile]
    ],
) -> type[DotPythonVersionConfigFile]:
    """Create a test .python-version config file class with tmp_path."""

    class MyTestDotPythonVersionConfigFile(
        config_file_factory(DotPythonVersionConfigFile)  # type: ignore [misc]
    ):
        """Test .python-version config file with tmp_path override."""

    return MyTestDotPythonVersionConfigFile


class TestDotPythonVersionConfigFile:
    """Test class."""

    def test_override_content(self) -> None:
        """Test method."""
        assert DotPythonVersionConfigFile.override_content(), "Expected True"

    def test_get_content_str(self) -> None:
        """Test method."""
        content_str = DotPythonVersionConfigFile.get_content_str()
        assert len(content_str) > 0, "Expected non-empty string"

    def test_get_filename(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for get_filename."""
        expected = ""
        actual = my_test_dot_python_version_config_file.get_filename()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_get_file_extension(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        expected = "python-version"
        actual = my_test_dot_python_version_config_file.get_file_extension()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_get_parent_path(
        self,
        my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method for get_parent_path."""
        with chdir(tmp_path):
            expected = Path()
            actual = my_test_dot_python_version_config_file.get_parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"

    def test__load(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for load."""
        my_test_dot_python_version_config_file()
        loaded = my_test_dot_python_version_config_file.load()
        assert DotPythonVersionConfigFile.CONTENT_KEY in loaded, (
            "Expected 'version' key in loaded config"
        )
        assert len(loaded[DotPythonVersionConfigFile.CONTENT_KEY]) > 0, (
            "Expected version to be non-empty"
        )

    def test__dump(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for dump."""
        my_test_dot_python_version_config_file()
        config = {DotPythonVersionConfigFile.CONTENT_KEY: "3.11"}
        my_test_dot_python_version_config_file.dump(config)
        loaded = my_test_dot_python_version_config_file.load()
        assert loaded[DotPythonVersionConfigFile.CONTENT_KEY] == "3.11", (
            "Expected version to be 3.11"
        )

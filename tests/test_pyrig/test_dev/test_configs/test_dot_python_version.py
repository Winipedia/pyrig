"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.dot_python_version import DotPythonVersionConfigFile
from pyrig.src.testing.assertions import assert_with_msg


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
    """Test class for DotPythonVersionConfigFile."""

    def test_get_filename(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for get_filename."""
        expected = ""
        actual = my_test_dot_python_version_config_file.get_filename()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_get_file_extension(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for get_file_extension."""
        expected = "python-version"
        actual = my_test_dot_python_version_config_file.get_file_extension()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_get_parent_path(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        expected = Path()
        actual = my_test_dot_python_version_config_file.get_parent_path()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_load(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for load."""
        my_test_dot_python_version_config_file()
        loaded = my_test_dot_python_version_config_file.load()
        assert_with_msg(
            DotPythonVersionConfigFile.VERSION_KEY in loaded,
            "Expected 'version' key in loaded config",
        )
        assert_with_msg(
            len(loaded[DotPythonVersionConfigFile.VERSION_KEY]) > 0,
            "Expected version to be non-empty",
        )

    def test_dump(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for dump."""
        my_test_dot_python_version_config_file()
        config = {DotPythonVersionConfigFile.VERSION_KEY: "3.11"}
        my_test_dot_python_version_config_file.dump(config)
        loaded = my_test_dot_python_version_config_file.load()
        assert_with_msg(
            loaded[DotPythonVersionConfigFile.VERSION_KEY] == "3.11",
            "Expected version to be 3.11",
        )

    def test_dump_raises_type_error(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for dump with invalid type."""
        my_test_dot_python_version_config_file()
        with pytest.raises(TypeError, match=r"Cannot dump .* to \.python-version file"):
            my_test_dot_python_version_config_file.dump(["invalid"])

    def test_get_configs(
        self, my_test_dot_python_version_config_file: type[DotPythonVersionConfigFile]
    ) -> None:
        """Test method for get_configs."""
        my_test_dot_python_version_config_file()
        configs = my_test_dot_python_version_config_file.get_configs()
        assert_with_msg(
            DotPythonVersionConfigFile.VERSION_KEY in configs,
            "Expected 'version' key in configs",
        )

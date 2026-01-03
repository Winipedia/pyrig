"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.configs.base.py_package import PythonPackageConfigFile


@pytest.fixture
def my_test_python_package_config_file(
    config_file_factory: Callable[
        [type[PythonPackageConfigFile]], type[PythonPackageConfigFile]
    ],
) -> type[PythonPackageConfigFile]:
    """Create a test python package config file class with tmp_path."""

    class MyTestPythonPackageConfigFile(config_file_factory(PythonPackageConfigFile)):  # type: ignore [misc]
        """Test python package config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_lines(cls) -> list[str]:
            """Get the content string."""
            return ['"""Test content."""', ""]

    return MyTestPythonPackageConfigFile


class TestPythonPackageConfigFile:
    """Test class."""

    def test__dump(
        self, my_test_python_package_config_file: type[PythonPackageConfigFile]
    ) -> None:
        """Test method for dump."""
        my_test_python_package_config_file()
        assert (
            my_test_python_package_config_file.get_path().parent / "__init__.py"
        ).exists(), "Expected __init__.py to be created"

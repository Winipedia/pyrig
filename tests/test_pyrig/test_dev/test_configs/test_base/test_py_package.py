"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any

import pytest

from pyrig.dev.configs.base.py_package import PythonPackageConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_python_package_config_file(
    config_file_factory: Callable[
        [type[PythonPackageConfigFile]], type[PythonPackageConfigFile]
    ],
    tmp_path: Path,
) -> type[PythonPackageConfigFile]:
    """Create a test python package config file class with tmp_path."""

    class MyTestPythonPackageConfigFile(config_file_factory(PythonPackageConfigFile)):  # type: ignore [misc]
        """Test python package config file with tmp_path override."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def get_content_str(cls) -> str:
            """Get the content string."""
            return '"""Test content."""\n'

        @classmethod
        def dump(cls, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config file."""
            with chdir(tmp_path):
                super().dump(config)

    return MyTestPythonPackageConfigFile


class TestPythonPackageConfigFile:
    """Test class."""

    def test_dump(
        self, my_test_python_package_config_file: type[PythonPackageConfigFile]
    ) -> None:
        """Test method for dump."""
        my_test_python_package_config_file()
        assert_with_msg(
            (
                my_test_python_package_config_file.get_path().parent / "__init__.py"
            ).exists(),
            "Expected __init__.py to be created",
        )

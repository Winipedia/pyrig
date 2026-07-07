"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.rig.configs.base.package import PythonPackageConfigFile
from pyrig.rig.tools.package_manager import PackageManager


@pytest.fixture
def my_test_python_package_config_file(
    config_file_factory: Callable[
        [type[PythonPackageConfigFile]], type[PythonPackageConfigFile]
    ],
) -> type[PythonPackageConfigFile]:
    """Create a test python package config file class with tmp_path."""

    class MyTestPythonPackageConfigFile(config_file_factory(PythonPackageConfigFile)):  # ty: ignore[unsupported-base]
        """Test python package config file with tmp_path override."""

        def stem(self) -> str:
            """Get the stem."""
            return "test_package"

        def parent_path(self) -> Path:
            """Get the parent path under the package root."""
            return PackageManager.I.package_root() / "parent_package"

        def lines(self) -> list[str]:
            """Get the content string."""
            return ['"""Test content."""']

    return MyTestPythonPackageConfigFile


class TestPythonPackageConfigFile:
    """Test class."""

    def test_package_root(
        self, my_test_python_package_config_file: type[PythonPackageConfigFile]
    ) -> None:
        """Test method."""
        assert (
            my_test_python_package_config_file().package_root()
            == PackageManager.I.package_root()
        )

    def test_source_root(
        self, my_test_python_package_config_file: type[PythonPackageConfigFile]
    ) -> None:
        """Test method."""
        assert (
            my_test_python_package_config_file().source_root()
            == PackageManager.I.source_root()
        )

    def test__dump(
        self,
        my_test_python_package_config_file: type[PythonPackageConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_python_package_config_file().validate()
            assert (
                my_test_python_package_config_file().path().parent / "__init__.py"
            ).exists()
            assert my_test_python_package_config_file().path().exists()
            assert (
                my_test_python_package_config_file().path().read_text()
                == '"""Test content."""'
            )
            assert (
                my_test_python_package_config_file().source_root()
                == PackageManager.I.source_root()
            )
            assert not (
                my_test_python_package_config_file().source_root() / "__init__.py"
            ).exists()

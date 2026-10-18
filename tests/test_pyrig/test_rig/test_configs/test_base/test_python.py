"""module."""

import ast
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest
from pyrig_fixtures.rig.configs.conftest import ConftestConfigFile

from pyrig.rig.configs.base.python import PythonConfigFile, PythonPackageConfigFile
from pyrig.rig.configs.scratch import ScratchConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


class TestPythonConfigFile:
    """Test class."""

    def test_source_root(self) -> None:
        """Test method."""
        assert ConftestConfigFile.I.source_root() == Path()
        assert ScratchConfigFile.I.source_root() == Path()

    def test_extension(self) -> None:
        """Test method."""
        expected = "py"
        assert issubclass(ConftestConfigFile, PythonConfigFile)
        actual = ConftestConfigFile().extension()
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_tree(
        self,
        my_test_python_package_config_file: type[PythonPackageConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            config = my_test_python_package_config_file()
            content = '"""Test module."""\n\nvalue = 1\n'
            config.write_content(content)
            tree = config.tree()
            assert isinstance(tree, ast.Module)
            assert ast.dump(tree) == ast.dump(ast.parse(content))

            config.write_content("value = 2\n")
            assert ast.dump(config.tree()) == ast.dump(ast.parse("value = 2\n"))


@pytest.fixture
def my_test_python_package_config_file(
    config_file_factory: Callable[
        [type[PythonPackageConfigFile]],
        type[PythonPackageConfigFile],
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

        def content(self) -> str:
            """Get the content string."""
            return '"""Test content."""'

    return MyTestPythonPackageConfigFile


class TestPythonPackageConfigFile:
    """Test class."""

    def test_package_root(
        self,
        my_test_python_package_config_file: type[PythonPackageConfigFile],
    ) -> None:
        """Test method."""
        assert (
            my_test_python_package_config_file().package_root()
            == PackageManager.I.package_root()
        )

    def test_source_root(
        self,
        my_test_python_package_config_file: type[PythonPackageConfigFile],
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

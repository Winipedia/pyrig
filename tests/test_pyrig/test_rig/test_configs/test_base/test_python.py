"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest
from pyrig_fixtures.rig.configs.conftest import ConftestConfigFile
from pytest_mock import MockerFixture

from pyrig.rig.configs.base.python import PythonConfigFile, PythonPackageConfigFile
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.package_init import PackageInitConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


class TestPythonConfigFile:
    """Test class."""

    def test_source_root(self) -> None:
        """Test method."""
        assert ConftestConfigFile.I.source_root() == Path()

    def test_import_path(self) -> None:
        """Test method."""
        assert ConftestConfigFile.I.import_path() == Path("tests/conftest.py")

    def test__dump(self, mocker: MockerFixture) -> None:
        """Test method."""
        module_before = ConftestConfigFile.I.module()
        dump_mock = mocker.patch.object(StringConfigFile, "_dump")
        ConftestConfigFile.I._dump([])  # noqa: SLF001
        dump_mock.assert_called_once()
        module_after = ConftestConfigFile.I.module()
        assert module_before is not module_after
        assert module_before.__name__ == module_after.__name__
        assert module_before.__file__ == module_after.__file__

    def test_module(self) -> None:
        """Test method."""
        assert ConftestConfigFile.I.module().__name__ == "tests.conftest"

        assert PackageInitConfigFile.I.module().__name__ == "pyrig"

    def test_extension(self) -> None:
        """Test method."""
        expected = "py"
        assert issubclass(ConftestConfigFile, PythonConfigFile)
        actual = ConftestConfigFile().extension()
        assert actual == expected, f"Expected {expected}, got {actual}"


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

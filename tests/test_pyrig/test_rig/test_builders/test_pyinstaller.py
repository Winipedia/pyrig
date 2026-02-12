"""Test module."""

import random
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest
from PIL import Image
from pytest_mock import MockFixture

from pyrig.rig.builders import pyinstaller
from pyrig.rig.builders.pyinstaller import PyInstallerBuilder
from pyrig.src.modules.module import make_obj_importpath


@pytest.fixture
def my_test_pyinstaller_builder(
    config_file_factory: Callable[[type[PyInstallerBuilder]], type[PyInstallerBuilder]],
    tmp_path: Path,
) -> type[PyInstallerBuilder]:
    """Create a test PyInstaller builder class."""

    class MyTestPyInstallerBuilder(config_file_factory(PyInstallerBuilder)):  # type: ignore [misc]
        """Test PyInstaller builder class."""

        @classmethod
        def get_additional_resource_pkgs(cls) -> list[ModuleType]:
            """Get the resource packages."""
            return []

        @classmethod
        def get_app_icon_png_path(cls) -> Path:
            """Get the app icon path."""
            path = tmp_path / "icon.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            r = random.randint(0, 255)  # nosec: B311  # noqa: S311
            g = random.randint(0, 255)  # nosec: B311  # noqa: S311
            b = random.randint(0, 255)  # nosec: B311  # noqa: S311

            img = Image.new("RGB", (256, 256), (r, g, b))
            img.save(path, format="PNG")
            return Path(path)

    return MyTestPyInstallerBuilder


class TestPyInstallerBuilder:
    """Test class."""

    def test_get_default_additional_resource_pkgs(self) -> None:
        """Test method."""
        # Test that default additional resource packages are discovered
        result = PyInstallerBuilder.get_default_additional_resource_pkgs()
        # Should return a list of modules
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        # All items should be modules
        for pkg in result:
            assert hasattr(pkg, "__name__"), f"Expected module, got {pkg}"

    def test_get_all_resource_pkgs(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        # Test that all resource packages includes both default and resources
        result = my_test_pyinstaller_builder.get_all_resource_pkgs()
        # Should return a list of modules
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        # Should include at least the resources package
        assert len(result) > 0, f"Expected at least one resource package, got {result}"

    def test_get_additional_resource_pkgs(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        additional_pkgs = my_test_pyinstaller_builder.get_additional_resource_pkgs()
        assert len(additional_pkgs) == 0, "Expected no additional packages"

    def test_get_temp_distpath(self, tmp_path: Path) -> None:
        """Test method."""
        result = PyInstallerBuilder.get_temp_distpath(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_get_temp_workpath(self, tmp_path: Path) -> None:
        """Test method."""
        result = PyInstallerBuilder.get_temp_workpath(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_get_temp_specpath(self, tmp_path: Path) -> None:
        """Test method."""
        result = PyInstallerBuilder.get_temp_specpath(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_get_add_datas(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder.get_add_datas()
        # should contain the resource.py and __init__.py from the resources pkg
        assert len(result) > 1, f"Expected at least two files, got {result}"

    def test_get_pyinstaller_options(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        options = my_test_pyinstaller_builder.get_pyinstaller_options(tmp_path)
        assert "--name" in options, "Expected --name option"

    def test_get_app_icon_png_path(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder.get_app_icon_png_path()
        assert result.name == "icon.png", "Expected icon.ico"

    def test_create_artifacts(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        mocker: MockFixture,
        tmp_path: Path,
    ) -> None:
        """Test method."""
        mock_run = mocker.patch(make_obj_importpath(pyinstaller) + ".run")
        my_test_pyinstaller_builder.create_artifacts(tmp_path)
        mock_run.assert_called_once()

    def test_convert_png_to_format(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder.convert_png_to_format("ico", tmp_path)
        assert result.name == "icon.ico", "Expected icon.ico"

    def test_get_app_icon_path(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder.get_app_icon_path(tmp_path)
        assert result.stem == "icon", "Expected icon"

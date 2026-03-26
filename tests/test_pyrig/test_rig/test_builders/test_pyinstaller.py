"""Test module."""

import random
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest
from PIL import Image
from pytest_mock import MockFixture

from pyrig.rig.builders import pyinstaller
from pyrig.rig.builders.pyinstaller import PyInstallerBuilder
from pyrig.src.modules.module import create_module, make_obj_importpath


@pytest.fixture
def my_test_pyinstaller_builder(
    config_file_factory: Callable[[type[PyInstallerBuilder]], type[PyInstallerBuilder]],
    tmp_path: Path,
) -> type[PyInstallerBuilder]:
    """Create a test PyInstaller builder class."""
    with chdir(tmp_path):
        path = tmp_path / "entry_point.py"
        module = create_module(path)
        path.write_text(
            """
def main():
    print("Hello, PyInstaller!")


if __name__ == "__main__":
    main()
"""
        )

    class MyTestPyInstallerBuilder(config_file_factory(PyInstallerBuilder)):  # ty: ignore[unsupported-base]
        """Test PyInstaller builder class."""

        def entry_point_module(self) -> ModuleType:
            return module

        def app_icon_png_path(self) -> Path:
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

    def test_entry_point_module(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        module = my_test_pyinstaller_builder().entry_point_module()
        assert isinstance(module, ModuleType), f"Expected module, got {type(module)}"

    def test_entry_point_path(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        path = my_test_pyinstaller_builder().entry_point_path()
        assert path.exists(), f"Expected path to exist, got {path}"
        assert "def main():" in path.read_text()

    def test_resource_packages(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        # Test that default additional resource packages are discovered
        result = my_test_pyinstaller_builder().resource_packages()
        # All items should be modules
        for package in result:
            assert hasattr(package, "__name__"), f"Expected module, got {package}"

    def test_temp_distpath(
        self, tmp_path: Path, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder().temp_distpath(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_temp_workpath(
        self, tmp_path: Path, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder().temp_workpath(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_temp_specpath(
        self, tmp_path: Path, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder().temp_specpath(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_add_datas(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder().add_datas()
        # should contain the resource.py and __init__.py from the resources package
        result_list = list(result)
        assert len(result_list) > 1, f"Expected at least two files, got {result_list}"

    def test_pyinstaller_options(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        options = my_test_pyinstaller_builder().pyinstaller_options(tmp_path)
        assert "--name" in options, "Expected --name option"

    def test_app_icon_png_path(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder().app_icon_png_path()
        assert result.name == "icon.png", "Expected icon.ico"

    def test_create_artifacts(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        mocker: MockFixture,
        tmp_path: Path,
    ) -> None:
        """Test method."""
        mock_run = mocker.patch(make_obj_importpath(pyinstaller) + ".run")
        my_test_pyinstaller_builder().create_artifacts(tmp_path)
        mock_run.assert_called_once()

    def test_convert_png_to_format(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder().convert_png_to_format("ico", tmp_path)
        assert result.name == "icon.ico", "Expected icon.ico"

    def test_app_icon_path(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        result = my_test_pyinstaller_builder().app_icon_path(tmp_path)
        assert result.stem == "icon", "Expected icon"

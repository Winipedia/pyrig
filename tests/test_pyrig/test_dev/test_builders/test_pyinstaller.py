"""Test module."""

import random
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest
from PIL import Image
from pytest_mock import MockFixture

from pyrig.dev.builders import pyinstaller
from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
from pyrig.src.modules.module import make_obj_importpath
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_pyinstaller_builder(
    builder_factory: Callable[[type[PyInstallerBuilder]], type[PyInstallerBuilder]],
    tmp_path: Path,
) -> type[PyInstallerBuilder]:
    """Create a test PyInstaller builder class."""

    class MyTestPyInstallerBuilder(builder_factory(PyInstallerBuilder)):  # type: ignore [misc]
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
        assert_with_msg(
            isinstance(result, list),
            f"Expected list, got {type(result)}",
        )
        # All items should be modules
        for pkg in result:
            assert_with_msg(
                hasattr(pkg, "__name__"),
                f"Expected module, got {pkg}",
            )

    def test_get_all_resource_pkgs(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        # Test that all resource packages includes both default and resources
        result = my_test_pyinstaller_builder.get_all_resource_pkgs()
        # Should return a list of modules
        assert_with_msg(
            isinstance(result, list),
            f"Expected list, got {type(result)}",
        )
        # Should include at least the resources package
        assert_with_msg(
            len(result) > 0,
            f"Expected at least one resource package, got {result}",
        )

    def test_get_additional_resource_pkgs(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method."""
        additional_pkgs = my_test_pyinstaller_builder.get_additional_resource_pkgs()
        assert len(additional_pkgs) == 0, "Expected no additional packages"

    def test_get_temp_distpath(self, tmp_path: Path) -> None:
        """Test method for get_temp_distpath."""
        result = PyInstallerBuilder.get_temp_distpath(tmp_path)
        assert_with_msg(result.exists(), "Expected path to exist")

    def test_get_temp_workpath(self, tmp_path: Path) -> None:
        """Test method for get_temp_workpath."""
        result = PyInstallerBuilder.get_temp_workpath(tmp_path)
        assert_with_msg(result.exists(), "Expected path to exist")

    def test_get_temp_specpath(self, tmp_path: Path) -> None:
        """Test method for get_temp_specpath."""
        result = PyInstallerBuilder.get_temp_specpath(tmp_path)
        assert_with_msg(result.exists(), "Expected path to exist")

    def test_get_add_datas(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method for get_add_datas."""
        result = my_test_pyinstaller_builder.get_add_datas()
        # should contain the resource.py and __init__.py from the resources pkg
        expected = 1
        assert len(result) == expected, "Expected no additional data"

    def test_get_pyinstaller_options(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method for get_pyinstaller_options."""
        options = my_test_pyinstaller_builder.get_pyinstaller_options(tmp_path)
        assert_with_msg("--name" in options, "Expected --name option")

    def test_get_app_icon_png_path(
        self, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method for get_app_icon_path."""
        result = my_test_pyinstaller_builder.get_app_icon_png_path()
        assert_with_msg(result.name == "icon.png", "Expected icon.ico")

    def test_create_artifacts(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        mocker: MockFixture,
    ) -> None:
        """Test method for create_artifacts."""
        mock_run = mocker.patch(make_obj_importpath(pyinstaller) + ".run")
        spy = mocker.spy(
            my_test_pyinstaller_builder,
            my_test_pyinstaller_builder.create_artifacts.__name__,
        )
        with pytest.raises(FileNotFoundError):
            my_test_pyinstaller_builder()

        spy.assert_called_once()
        mock_run.assert_called_once()

    def test_convert_png_to_format(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method for convert_png_to_format."""
        result = my_test_pyinstaller_builder.convert_png_to_format("ico", tmp_path)
        assert_with_msg(result.name == "icon.ico", "Expected icon.ico")

    def test_get_app_icon_path(
        self,
        my_test_pyinstaller_builder: type[PyInstallerBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method for get_app_icon_path."""
        result = my_test_pyinstaller_builder.get_app_icon_path(tmp_path)
        assert_with_msg(result.stem == "icon", "Expected icon")

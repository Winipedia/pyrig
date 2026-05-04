"""Test module."""

import random
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest
from PIL import Image
from pytest_mock import MockerFixture

from pyrig.core.introspection.packages import (
    import_package_from_dir,
)
from pyrig.rig.builders.base import executable
from pyrig.rig.builders.base.executable import ExecutableBuilder


@pytest.fixture
def my_test_executable_builder(
    config_file_factory: Callable[[type[ExecutableBuilder]], type[ExecutableBuilder]],
    tmp_path: Path,
    create_module: Callable[[Path], ModuleType],
) -> type[ExecutableBuilder]:
    """Create a test ExecutableBuilder class."""
    with chdir(tmp_path):
        path = Path("builder_package/entry_point.py")
        module = create_module(path)
        package = import_package_from_dir(
            Path("builder_package"), name="builder_package"
        )  # type: ignore[return-value]
        path.write_text(
            """
def main():
    print("Hello, PyInstaller!")


if __name__ == "__main__":
    main()
"""
        )

    class MyTestExecutableBuilder(config_file_factory(ExecutableBuilder)):  # ty: ignore[unsupported-base]
        """Test PyInstaller builder class."""

        def entry_point_module(self) -> ModuleType:
            return module

        def app_icon_png_location(self) -> tuple[str, ModuleType]:
            """Get the app icon path."""
            path = tmp_path / "builder_package" / "icon.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            r = random.randint(0, 255)  # nosec: B311  # noqa: S311
            g = random.randint(0, 255)  # nosec: B311  # noqa: S311
            b = random.randint(0, 255)  # nosec: B311  # noqa: S311

            img = Image.new("RGB", (256, 256), (r, g, b))
            img.save(path, format="PNG")
            return "icon", package  # type: ignore[return-value]

    return MyTestExecutableBuilder


class TestExecutableBuilder:
    """Test class."""

    def test_extension_separator(
        self,
        mocker: MockerFixture,
        my_test_executable_builder: type[ExecutableBuilder],
    ) -> None:
        """Test method."""
        for pf, sep in [("Windows", "."), ("Darwin", ""), ("Linux", "")]:
            mocker.patch("platform.system", return_value=pf)
            assert my_test_executable_builder().extension_separator() == sep

    def test_non_platform_stem(
        self, my_test_executable_builder: type[ExecutableBuilder]
    ) -> None:
        """Test method."""
        assert my_test_executable_builder().non_platform_stem() == "pyrig"

    def test_extension(
        self,
        my_test_executable_builder: type[ExecutableBuilder],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        for pf, ext in [("Windows", "exe"), ("Darwin", ""), ("Linux", "")]:
            mocker.patch("platform.system", return_value=pf)
            assert my_test_executable_builder().extension() == ext

    def test_app_icon_png_path(
        self, my_test_executable_builder: type[ExecutableBuilder], tmp_path: Path
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            assert my_test_executable_builder().app_icon_png_path().exists()
            assert (
                my_test_executable_builder().app_icon_png_path()
                == Path("builder_package") / "icon.png"
            )

    def test_entry_point_module(
        self, my_test_executable_builder: type[ExecutableBuilder]
    ) -> None:
        """Test method."""
        module = my_test_executable_builder().entry_point_module()
        assert isinstance(module, ModuleType), f"Expected module, got {type(module)}"

    def test_entry_point_path(
        self, my_test_executable_builder: type[ExecutableBuilder]
    ) -> None:
        """Test method."""
        path = my_test_executable_builder().entry_point_path()
        assert path.exists(), f"Expected path to exist, got {path}"
        assert "def main():" in path.read_text()

    def test_resource_packages(
        self, my_test_executable_builder: type[ExecutableBuilder]
    ) -> None:
        """Test method."""
        # Test that default additional resource packages are discovered
        result = my_test_executable_builder().resource_packages()
        # All items should be modules
        for package in result:
            assert hasattr(package, "__name__"), f"Expected module, got {package}"

    def test_temp_workpath(
        self, tmp_path: Path, my_test_executable_builder: type[ExecutableBuilder]
    ) -> None:
        """Test method."""
        result = my_test_executable_builder().temp_workpath(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_temp_specpath(
        self, tmp_path: Path, my_test_executable_builder: type[ExecutableBuilder]
    ) -> None:
        """Test method."""
        result = my_test_executable_builder().temp_specpath(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_add_datas(
        self, my_test_executable_builder: type[ExecutableBuilder]
    ) -> None:
        """Test method."""
        result = my_test_executable_builder().add_datas()
        # should contain the resource.py and __init__.py from the resources package
        result_list = list(result)
        assert len(result_list) > 1, f"Expected at least two files, got {result_list}"

    def test_executable_options(
        self,
        my_test_executable_builder: type[ExecutableBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            options = my_test_executable_builder().executable_options(tmp_path)
            assert "--name" in options

    def test_app_icon_png_location(
        self, my_test_executable_builder: type[ExecutableBuilder]
    ) -> None:
        """Test method."""
        name, package = my_test_executable_builder().app_icon_png_location()
        assert name == "icon"
        assert package.__name__ == "builder_package"
        assert (
            Path(package.__file__).parent / "icon.png"  # ty:ignore[invalid-argument-type]
            == my_test_executable_builder().app_icon_png_path()
        )

    def test_create_artifact(
        self,
        my_test_executable_builder: type[ExecutableBuilder],
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            mock_run = mocker.patch(executable.__name__ + ".run")
            my_test_executable_builder().create_artifact(tmp_path)
            mock_run.assert_called_once()

    def test_convert_png_to_format(
        self,
        my_test_executable_builder: type[ExecutableBuilder],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            result = my_test_executable_builder().convert_png_to_format("ico", tmp_path)
            assert result.name == "icon.ico", "Expected icon.ico"

    def test_app_icon_path(
        self,
        my_test_executable_builder: type[ExecutableBuilder],
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            result = my_test_executable_builder().app_icon_path(tmp_path)
            assert result.stem == "icon"

            # mock platform.system to return each platform once
            platforms = ["Windows", "Darwin", "Linux"]
            for pf in platforms:
                mocker.patch("platform.system", return_value=pf)
                result = my_test_executable_builder().app_icon_path(tmp_path)
                if pf == "Windows":
                    assert result.suffix == ".ico", "Expected .ico for Windows"
                elif pf == "Darwin":
                    assert result.suffix == ".icns", "Expected .icns for macOS"
                else:
                    assert result.suffix == ".png", "Expected .png for Linux"


def test_module_docstring() -> None:
    """Test function."""
    assert (
        executable.__doc__
        == """PyInstaller-based artifact builder for creating standalone executables."""
    )

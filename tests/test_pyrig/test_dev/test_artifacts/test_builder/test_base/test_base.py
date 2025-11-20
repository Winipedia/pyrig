"""module."""

import platform
import random
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import PyInstaller.__main__ as pyinstaller_main
import pytest
from PIL import Image
from pytest_mock import MockFixture

from pyrig.dev.artifacts.builder.base.base import Builder, PyInstallerBuilder
from pyrig.src.modules.module import make_obj_importpath
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_builder(
    builder_factory: Callable[[type[Builder]], type[Builder]],
) -> type[Builder]:
    """Create a test build class."""

    class MyTestBuilder(builder_factory(Builder)):  # type: ignore [misc]
        """Test build class."""

        @classmethod
        def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
            """Build the project."""
            paths = [temp_artifacts_dir / "build.txt"]
            for path in paths:
                path.write_text("Hello World!")

    return MyTestBuilder


class TestBuilder:
    """Test class."""

    def test_get_resources_path(self) -> None:
        """Test method."""
        assert isinstance(Builder.get_resources_path(), Path)

    def test_get_resources_path_from_src_pkg(self) -> None:
        """Test method."""
        assert isinstance(Builder.get_resources_path_from_src_pkg(), Path)

    def test_get_artifacts_dir(self) -> None:
        """Test method for get_artifacts_dir."""
        # just assert it returns a path
        assert_with_msg(
            isinstance(Builder.get_artifacts_dir(), Path),
            "Expected Path",
        )

    def test_rename_artifacts(
        self, tmp_path: Path, my_test_pyinstaller_builder: type[PyInstallerBuilder]
    ) -> None:
        """Test method for rename_artifacts."""
        # write a file to the temp dir
        (tmp_path / "test.txt").write_text("Hello World!")
        my_test_pyinstaller_builder.rename_artifacts([tmp_path / "test.txt"])
        assert_with_msg(
            (
                my_test_pyinstaller_builder.get_artifacts_dir()
                / f"test-{platform.system()}.txt"
            ).exists(),
            "Expected renamed file",
        )

    def test_get_artifacts(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_artifacts."""
        my_build = my_test_builder()
        artifacts = my_build.get_artifacts()
        assert_with_msg(
            artifacts[0].name == f"build-{platform.system()}.txt",
            "Expected artifact to be built",
        )

    def test_get_temp_artifacts_path(self, tmp_path: Path) -> None:
        """Test method for get_temp_artifacts_path."""
        result = Builder.get_temp_artifacts_path(tmp_path)
        assert_with_msg(result.exists(), "Expected path to exist")

    def test_create_artifacts(
        self, my_test_builder: type[Builder], mocker: MockFixture
    ) -> None:
        """Test method for get_artifacts."""
        # spy on create_artifacts
        spy = mocker.spy(my_test_builder, my_test_builder.create_artifacts.__name__)

        my_build = my_test_builder()

        spy.assert_called_once()

        artifacts = my_build.get_artifacts()
        assert_with_msg(
            artifacts[0].name == f"build-{platform.system()}.txt",
            "Expected artifact to be built",
        )

    def test___init__(
        self, my_test_builder: type[Builder], mocker: MockFixture
    ) -> None:
        """Test method for __init__."""
        # spy on build and assert its called
        my_build_spy = mocker.spy(my_test_builder, my_test_builder.build.__name__)
        my_test_builder()
        my_build_spy.assert_called_once()

    def test_build(self, my_test_builder: type[Builder], mocker: MockFixture) -> None:
        """Test method for build."""
        create_spy = mocker.spy(
            my_test_builder, my_test_builder.create_artifacts.__name__
        )
        get_artifacts_spy = mocker.spy(
            my_test_builder, my_test_builder.get_temp_artifacts.__name__
        )
        rename_spy = mocker.spy(
            my_test_builder, my_test_builder.rename_artifacts.__name__
        )
        my_test_builder.build()
        create_spy.assert_called_once()
        get_artifacts_spy.assert_called_once()
        rename_spy.assert_called_once()

    def test_get_temp_artifacts(self, tmp_path: Path) -> None:
        """Test method for get_artifacts."""
        # write a file to the temp dir
        (tmp_path / "test.txt").write_text("Hello World!")
        artifacts = Builder.get_temp_artifacts(tmp_path)
        assert_with_msg(
            len(artifacts) == 1,
            "Expected one artifact",
        )

    def test_get_non_abstract_subclasses(self) -> None:
        """Test method for get_non_abstract_builders."""
        builders = Builder.get_non_abstract_subclasses()
        assert_with_msg(
            len(builders) == 0,
            "Expected one builder",
        )

    def test_init_all_non_abstract_subclasses(
        self, my_test_builder: type[Builder], mocker: MockFixture
    ) -> None:
        """Test method for init_all_non_abstract."""
        # mock get_non_abstract_subclasses to return my_test_builder
        mocker.patch.object(
            Builder,
            Builder.get_non_abstract_subclasses.__name__,
            return_value={my_test_builder},
        )
        Builder.init_all_non_abstract_subclasses()
        artifacts = my_test_builder.get_artifacts()
        assert_with_msg(
            artifacts[0].name == f"build-{platform.system()}.txt",
            "Expected artifact to be built",
        )

    def test_get_app_name(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_app_name."""
        result = my_test_builder.get_app_name()
        assert_with_msg(len(result) > 0, "Expected non-empty string")

    def test_get_main_path_from_src_pkg(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_main_path_from_src_pkg."""
        result = my_test_builder.get_main_path_from_src_pkg()
        assert_with_msg(result == Path("main.py"), "Expected main.py")

    def test_get_root_path(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_root_path."""
        result = my_test_builder.get_root_path()
        assert_with_msg(result.exists(), "Expected path to exist")

    def test_get_src_pkg_path(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_src_pkg_path."""
        result = my_test_builder.get_src_pkg_path()
        assert_with_msg(result.exists(), "Expected path to exist")

    def test_get_main_path(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_main_path."""
        result = my_test_builder.get_main_path()
        assert_with_msg(result.name == "main.py", "Expected main.py")


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
        expected = 2
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
        mock_run = mocker.patch(make_obj_importpath(pyinstaller_main) + ".run")
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

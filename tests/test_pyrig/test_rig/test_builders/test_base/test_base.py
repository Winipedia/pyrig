"""module."""

import platform
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest
from pytest_mock import MockFixture

from pyrig.rig import builders
from pyrig.rig.builders.base.base import BuilderConfigFile


@pytest.fixture
def my_test_builder_config_file(
    config_file_factory: Callable[[type[BuilderConfigFile]], type[BuilderConfigFile]],
) -> type[BuilderConfigFile]:
    """Create a test builder config file class with tmp_path."""

    class MyTestBuilderConfigFile(
        config_file_factory(BuilderConfigFile)  # type: ignore [misc]
    ):
        """Test builder config file with tmp_path override."""

        @classmethod
        def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
            """Create the artifacts."""
            file = temp_artifacts_dir / cls.filename()
            file.write_text(cls.__name__)

    return MyTestBuilderConfigFile


class TestBuilderConfigFile:
    """Test class."""

    def test_create_artifacts(
        self,
        my_test_builder_config_file: type[BuilderConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        my_test_builder_config_file()
        with chdir(tmp_path):
            platform_file = my_test_builder_config_file.get_platform_specific_path(
                Path(my_test_builder_config_file.filename())
            )
            assert platform_file.exists()
            loaded = my_test_builder_config_file.load()
            assert loaded == [platform_file]

    def test_parent_path(self) -> None:
        """Test method."""
        assert BuilderConfigFile.parent_path() == Path("dist")

    def test__load(self, my_test_builder_config_file: type[BuilderConfigFile]) -> None:
        """Test method."""
        my_test_builder_config_file()
        loaded = my_test_builder_config_file.load()
        assert isinstance(loaded, list)
        assert len(loaded) == 1
        assert all(isinstance(item, Path) for item in loaded)

    def test__dump(self, mocker: MockFixture) -> None:
        """Test method."""
        # assert calls build
        mock_build = mocker.patch.object(
            BuilderConfigFile, BuilderConfigFile.build.__name__
        )
        BuilderConfigFile._dump(BuilderConfigFile.configs())  # noqa: SLF001
        mock_build.assert_called_once()

    def test_extension(self) -> None:
        """Test method."""
        assert BuilderConfigFile.extension() == ""

    def test__configs(self) -> None:
        """Test method."""
        assert BuilderConfigFile.configs() == []

    def test_is_correct(
        self,
        my_test_builder_config_file: type[BuilderConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method."""
        assert not my_test_builder_config_file.is_correct()
        # mock create artifacts to not do anything
        mocker.patch.object(
            my_test_builder_config_file,
            my_test_builder_config_file.create_artifacts.__name__,
            return_value=None,
        )
        with pytest.raises(ValueError, match="not correct"):
            my_test_builder_config_file()

    def test_create_file(
        self,
        my_test_builder_config_file: type[BuilderConfigFile],
    ) -> None:
        """Test method."""
        my_test_builder_config_file.create_file()
        assert my_test_builder_config_file.parent_path().exists()
        assert not my_test_builder_config_file.path().exists()

    def test_definition_package(self) -> None:
        """Test method."""
        assert BuilderConfigFile.definition_package() is builders

    def test_build(
        self,
        my_test_builder_config_file: type[BuilderConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method."""
        spy = mocker.spy(
            my_test_builder_config_file, my_test_builder_config_file.build.__name__
        )
        my_test_builder_config_file()
        spy.assert_called_once()

    def test_rename_artifacts(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            BuilderConfigFile.create_file()
            file = tmp_path / "test.txt"
            file.write_text("test")
            files = [file]
            BuilderConfigFile.rename_artifacts(files)
            assert not file.exists()
            pltform_specific_path = BuilderConfigFile.get_platform_specific_path(file)
            assert pltform_specific_path.exists()

    def test_get_platform_specific_path(self) -> None:
        """Test method."""
        path = Path("test.txt")
        platform_specific_path = BuilderConfigFile.get_platform_specific_path(path)
        assert platform_specific_path == BuilderConfigFile.parent_path() / (
            f"test-{platform.system()}.txt"
        )

    def test_rename_artifact(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            BuilderConfigFile.create_file()
            file = tmp_path / "test.txt"
            file.write_text("test")
            BuilderConfigFile.rename_artifact(file)
            assert not file.exists()
            pltform_specific_path = BuilderConfigFile.get_platform_specific_path(file)
            assert pltform_specific_path.exists()

    def test_get_platform_specific_name(self) -> None:
        """Test method."""
        path = Path("test.txt")
        platform_specific_name = BuilderConfigFile.get_platform_specific_name(path)
        assert platform_specific_name == f"test-{platform.system()}.txt"

    def test_get_temp_artifacts(self, tmp_path: Path) -> None:
        """Test method."""
        # write a file to tmp_path
        file = tmp_path / "test.txt"
        file.write_text("test")
        artifacts = BuilderConfigFile.get_temp_artifacts(tmp_path)
        assert artifacts == [file]

    def test_get_temp_artifacts_path(self, tmp_path: Path) -> None:
        """Test method."""
        temp_artifacts_path = BuilderConfigFile.get_temp_artifacts_path(tmp_path)
        assert temp_artifacts_path == tmp_path / BuilderConfigFile.ARTIFACTS_DIR_NAME
        assert temp_artifacts_path.exists()

    def test_get_app_name(self) -> None:
        """Test method."""
        app_name = BuilderConfigFile.get_app_name()
        assert app_name == "pyrig"

    def test_get_root_path(self) -> None:
        """Test method."""
        root_path = BuilderConfigFile.get_root_path()
        assert root_path == Path.cwd()

    def test_get_main_path(self) -> None:
        """Test method."""
        main_path = BuilderConfigFile.get_main_path()
        assert main_path == Path.cwd() / "pyrig" / "main.py"

    def test_get_resources_path(self) -> None:
        """Test method."""
        resources_path = BuilderConfigFile.get_resources_path()
        assert resources_path == Path.cwd() / "pyrig" / "resources"

    def test_get_src_pkg_path(self) -> None:
        """Test method."""
        src_pkg_path = BuilderConfigFile.get_src_pkg_path()
        assert src_pkg_path == Path.cwd() / "pyrig"

    def test_get_main_path_relative_to_src_pkg(self) -> None:
        """Test method."""
        main_path = BuilderConfigFile.get_main_path_relative_to_src_pkg()
        assert main_path == Path("main.py")

    def test_get_resources_path_relative_to_src_pkg(self) -> None:
        """Test method."""
        resources_path = BuilderConfigFile.get_resources_path_relative_to_src_pkg()
        assert resources_path == Path("resources")

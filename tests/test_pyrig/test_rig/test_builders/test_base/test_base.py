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

        def create_artifacts(self, temp_artifacts_dir: Path) -> None:
            """Create the artifacts."""
            file = temp_artifacts_dir / self.filename()
            file.write_text(self.__class__.__name__)

    return MyTestBuilderConfigFile


class TestBuilderConfigFile:
    """Test class."""

    def test_dist_dir_name(self) -> None:
        """Test method."""
        result = BuilderConfigFile.dist_dir_name()
        assert result == "dist"

    def test_create_artifacts(
        self,
        my_test_builder_config_file: type[BuilderConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        my_test_builder_config_file().validate()
        with chdir(tmp_path):
            platform_file = my_test_builder_config_file().platform_specific_path(
                Path(my_test_builder_config_file().filename())
            )
            assert platform_file.exists()
            loaded = my_test_builder_config_file().load()
            assert loaded == [platform_file]

    def test_parent_path(
        self, my_test_builder_config_file: type[BuilderConfigFile], tmp_path: Path
    ) -> None:
        """Test method."""
        assert my_test_builder_config_file().parent_path() == tmp_path / "dist"

    def test__load(self, my_test_builder_config_file: type[BuilderConfigFile]) -> None:
        """Test method."""
        my_test_builder_config_file().validate()
        loaded = my_test_builder_config_file().load()
        assert isinstance(loaded, list)
        assert len(loaded) == 1
        assert all(isinstance(item, Path) for item in loaded)

    def test__dump(
        self, mocker: MockFixture, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        # assert calls build
        mock_build = mocker.patch.object(
            my_test_builder_config_file, my_test_builder_config_file().build.__name__
        )
        my_test_builder_config_file()._dump(my_test_builder_config_file().configs())  # noqa: SLF001
        mock_build.assert_called_once()

    def test_extension(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        assert my_test_builder_config_file().extension() == ""

    def test__configs(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        assert my_test_builder_config_file().configs() == []

    def test_is_correct(
        self,
        my_test_builder_config_file: type[BuilderConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method."""
        assert not my_test_builder_config_file().is_correct()
        # mock create artifacts to not do anything
        mocker.patch.object(
            my_test_builder_config_file,
            my_test_builder_config_file().create_artifacts.__name__,
            return_value=None,
        )
        with pytest.raises(ValueError, match="not correct"):
            my_test_builder_config_file().validate()

    def test_create_file(
        self,
        my_test_builder_config_file: type[BuilderConfigFile],
    ) -> None:
        """Test method."""
        my_test_builder_config_file().create_file()
        assert my_test_builder_config_file().parent_path().exists()
        assert not my_test_builder_config_file().path().exists()

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
            my_test_builder_config_file, my_test_builder_config_file().build.__name__
        )
        my_test_builder_config_file().validate()
        spy.assert_called_once()

    def test_rename_artifacts(
        self, tmp_path: Path, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_builder_config_file().create_file()
            file = tmp_path / "test.txt"
            file.write_text("test")
            files = [file]
            my_test_builder_config_file().rename_artifacts(files)
            assert not file.exists()
            pltform_specific_path = (
                my_test_builder_config_file().platform_specific_path(file)
            )
            assert pltform_specific_path.exists()

    def test_platform_specific_path(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        path = Path("test.txt")
        platform_specific_path = my_test_builder_config_file().platform_specific_path(
            path
        )
        assert platform_specific_path == my_test_builder_config_file().parent_path() / (
            f"test-{platform.system()}.txt"
        )

    def test_rename_artifact(
        self, tmp_path: Path, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_builder_config_file().create_file()
            file = tmp_path / "test.txt"
            file.write_text("test")
            my_test_builder_config_file().rename_artifact(file)
            assert not file.exists()
            pltform_specific_path = (
                my_test_builder_config_file().platform_specific_path(file)
            )
            assert pltform_specific_path.exists()

    def test_platform_specific_name(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        path = Path("test.txt")
        platform_specific_name = my_test_builder_config_file().platform_specific_name(
            path
        )
        assert platform_specific_name == f"test-{platform.system()}.txt"

    def test_temp_artifacts(
        self, tmp_path: Path, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        # write a file to tmp_path
        file = tmp_path / "test.txt"
        file.write_text("test")
        artifacts = my_test_builder_config_file().temp_artifacts(tmp_path)
        assert artifacts == [file]

    def test_temp_artifacts_path(
        self, tmp_path: Path, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        temp_artifacts_path = my_test_builder_config_file().temp_artifacts_path(
            tmp_path
        )
        assert (
            temp_artifacts_path
            == tmp_path / my_test_builder_config_file().dist_dir_name()
        )
        assert temp_artifacts_path.exists()

    def test_app_name(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        app_name = my_test_builder_config_file().app_name()
        assert app_name == "pyrig"

    def test_root_path(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        root_path = my_test_builder_config_file().root_path()
        assert root_path == Path.cwd()

    def test_main_path(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        main_path = my_test_builder_config_file().main_path()
        assert main_path == Path.cwd() / "pyrig" / "main.py"

    def test_resources_path(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        resources_path = my_test_builder_config_file().resources_path()
        assert resources_path == Path.cwd() / "pyrig" / "resources"

    def test_src_package_path(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        src_package_path = my_test_builder_config_file().src_package_path()
        assert src_package_path == Path.cwd() / "pyrig"

    def test_main_path_relative_to_src_package(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        main_path = my_test_builder_config_file().main_path_relative_to_src_package()
        assert main_path == Path("main.py")

    def test_resources_path_relative_to_src_package(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        resources_path = (
            my_test_builder_config_file().resources_path_relative_to_src_package()
        )
        assert resources_path == Path("resources")

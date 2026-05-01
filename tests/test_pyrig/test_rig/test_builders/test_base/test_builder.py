"""module."""

import platform
from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pyrig.rig import builders
from pyrig.rig.builders.base.builder import BuilderConfigFile


@pytest.fixture
def my_test_builder_config_file(
    config_file_factory: Callable[[type[BuilderConfigFile]], type[BuilderConfigFile]],
) -> type[BuilderConfigFile]:
    """Create a test builder config file class with tmp_path."""

    class MyTestBuilderConfigFile(
        config_file_factory(BuilderConfigFile)  # ty: ignore[unsupported-base]
    ):
        """Test builder config file with tmp_path override."""

        def non_platform_stem(self) -> str:
            """Get the stem."""
            return "my-file"

        def extension(self) -> str:
            """Get the extension."""
            return "txt"

        def create_artifact(self, tmp_path: Path) -> None:
            """Create the artifacts."""
            file = tmp_path / self.filename()
            file.write_text("My File Content")

    return MyTestBuilderConfigFile


class TestBuilderConfigFile:
    """Test class."""

    def test_non_platform_stem(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        assert my_test_builder_config_file().non_platform_stem() == "my-file"

    def test_create_artifact(
        self, my_test_builder_config_file: type[BuilderConfigFile], tmp_path: Path
    ) -> None:
        """Test method."""
        my_test_builder_config_file().create_artifact(tmp_path)
        artifact_path = tmp_path / my_test_builder_config_file().filename()
        assert artifact_path.exists()
        assert artifact_path.read_text() == "My File Content"

    def test_definition_package(self) -> None:
        """Test method."""
        assert BuilderConfigFile.definition_package() is builders

    def test_dist_dir_name(self) -> None:
        """Test method."""
        assert BuilderConfigFile.dist_dir_name() == "dist"

    def test_dist_dir_path(self) -> None:
        """Test method."""
        assert BuilderConfigFile.dist_dir_path() == Path("dist")

    def test_stem(self, my_test_builder_config_file: type[BuilderConfigFile]) -> None:
        """Test method."""
        assert my_test_builder_config_file().stem() == f"my-file-{platform.system()}"

    def test_parent_path(
        self, my_test_builder_config_file: type[BuilderConfigFile], tmp_path: Path
    ) -> None:
        """Test method."""
        assert my_test_builder_config_file().parent_path() == tmp_path / "dist"

    def test__configs(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        assert my_test_builder_config_file()._configs() == [  # noqa: SLF001
            my_test_builder_config_file().path()
        ]

    def test__load(
        self, my_test_builder_config_file: type[BuilderConfigFile], tmp_path: Path
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            assert my_test_builder_config_file()._load() == []  # noqa: SLF001

            my_test_builder_config_file().validate()

            assert my_test_builder_config_file()._load() == [  # noqa: SLF001
                my_test_builder_config_file().path()
            ]

    def test__dump(
        self,
        my_test_builder_config_file: type[BuilderConfigFile],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        build_mock = mocker.patch.object(
            my_test_builder_config_file,
            BuilderConfigFile.build.__name__,
        )
        my_test_builder_config_file()._dump([])  # noqa: SLF001
        build_mock.assert_called_once_with()

    def test_create_file(
        self, my_test_builder_config_file: type[BuilderConfigFile]
    ) -> None:
        """Test method."""
        assert my_test_builder_config_file().parent_path().exists() is False
        my_test_builder_config_file().create_file()
        assert my_test_builder_config_file().parent_path().exists() is True

    def test_build(
        self, my_test_builder_config_file: type[BuilderConfigFile], tmp_path: Path
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_builder_config_file().create_file()
            my_test_builder_config_file().build()
            assert my_test_builder_config_file().path().exists()

    def test_move_artifact(
        self, my_test_builder_config_file: type[BuilderConfigFile], tmp_path: Path
    ) -> None:
        """Test method."""
        filename = my_test_builder_config_file().filename()
        artifact = tmp_path / filename
        artifact.write_text("My File Content")

        my_test_builder_config_file().create_file()

        my_test_builder_config_file().move_artifact(tmp_path)

        dist_path = my_test_builder_config_file().parent_path() / filename
        assert dist_path.exists()
        assert dist_path.read_text() == "My File Content"

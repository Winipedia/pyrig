"""module."""

import platform
from collections.abc import Callable
from pathlib import Path

import pytest
from pytest_mock import MockFixture

from pyrig.dev.builders.base.base import Builder


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
        assert isinstance(Builder.get_artifacts_dir(), Path), "Expected Path"

    def test_rename_artifacts(
        self, tmp_path: Path, my_test_builder: type[Builder]
    ) -> None:
        """Test method for rename_artifacts."""
        # write a file to the temp dir
        (tmp_path / "test.txt").write_text("Hello World!")
        my_test_builder.rename_artifacts([tmp_path / "test.txt"])
        assert (
            my_test_builder.get_artifacts_dir() / f"test-{platform.system()}.txt"
        ).exists(), "Expected renamed file"

    def test_get_artifacts(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_artifacts."""
        my_build = my_test_builder()
        artifacts = my_build.get_artifacts()
        assert artifacts[0].name == f"build-{platform.system()}.txt", (
            "Expected artifact to be built"
        )

    def test_get_temp_artifacts_path(self, tmp_path: Path) -> None:
        """Test method for get_temp_artifacts_path."""
        result = Builder.get_temp_artifacts_path(tmp_path)
        assert result.exists(), "Expected path to exist"

    def test_create_artifacts(
        self, my_test_builder: type[Builder], mocker: MockFixture
    ) -> None:
        """Test method for get_artifacts."""
        # spy on create_artifacts
        spy = mocker.spy(my_test_builder, my_test_builder.create_artifacts.__name__)

        my_build = my_test_builder()

        spy.assert_called_once()

        artifacts = my_build.get_artifacts()
        assert artifacts[0].name == f"build-{platform.system()}.txt", (
            "Expected artifact to be built"
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
        assert len(artifacts) == 1, "Expected one artifact"

    def test_get_non_abstract_subclasses(self) -> None:
        """Test method for get_non_abstract_builders."""
        builders = Builder.get_non_abstract_subclasses()
        assert len(builders) == 0, "Expected one builder"

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
        assert artifacts[0].name == f"build-{platform.system()}.txt", (
            "Expected artifact to be built"
        )

    def test_get_app_name(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_app_name."""
        result = my_test_builder.get_app_name()
        assert len(result) > 0, "Expected non-empty string"

    def test_get_main_path_from_src_pkg(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_main_path_from_src_pkg."""
        result = my_test_builder.get_main_path_from_src_pkg()
        assert result == Path("main.py"), "Expected main.py"

    def test_get_root_path(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_root_path."""
        result = my_test_builder.get_root_path()
        assert result.exists(), "Expected path to exist"

    def test_get_src_pkg_path(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_src_pkg_path."""
        result = my_test_builder.get_src_pkg_path()
        assert result.exists(), "Expected path to exist"

    def test_get_main_path(self, my_test_builder: type[Builder]) -> None:
        """Test method for get_main_path."""
        result = my_test_builder.get_main_path()
        assert result.name == "main.py", "Expected main.py"

"""test module."""

import platform
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.dev.builders.base.base import Builder
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def sample_config_file(
    config_file_factory: Callable[[type[ConfigFile]], type[ConfigFile]],
) -> type[ConfigFile]:
    """Create a sample config file class for testing the factory."""

    class SampleConfigFile(config_file_factory(ConfigFile)):  # type: ignore [misc]
        """Sample config file for testing."""

        @classmethod
        def get_parent_path(cls) -> Path:
            """Get the parent path."""
            return Path()

        @classmethod
        def load(cls) -> dict[str, Any]:
            """Load the config."""
            return {}

        @classmethod
        def dump(cls, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config."""

        @classmethod
        def get_file_extension(cls) -> str:
            """Get the file extension."""
            return "test"

        @classmethod
        def get_configs(cls) -> dict[str, Any]:
            """Get the configs."""
            return {"key": "value"}

    return SampleConfigFile


def test_config_file_factory(
    sample_config_file: type[ConfigFile], tmp_path: Path
) -> None:
    """Test that config_file_factory wraps get_path to use tmp_path."""
    assert_with_msg(
        issubclass(sample_config_file, ConfigFile),
        "Expected sample_config_file to be a class",
    )
    # The factory should wrap the get_path method to use tmp_path
    path = sample_config_file.get_path()

    # The path should be inside tmp_path
    assert_with_msg(
        str(path).startswith(str(tmp_path)),
        f"Expected path {path} to start with {tmp_path}",
    )

    # The path should have the correct extension
    assert_with_msg(
        path.suffix == ".test",
        f"Expected extension '.test', got {path.suffix}",
    )

    assert_with_msg(
        path.name == "sample.test",
        f"Expected filename 'sample.test', got {path.name}",
    )


@pytest.fixture
def sample_builder(
    builder_factory: Callable[[type[Builder]], type[Builder]],
) -> type[Builder]:
    """Create a sample builder class for testing the factory."""

    class SampleBuilder(builder_factory(Builder)):  # type: ignore [misc]
        """Sample builder for testing."""

        @classmethod
        def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
            """Create artifacts."""
            (temp_artifacts_dir / "sample.txt").write_text("Hello World!")

    return SampleBuilder


def test_builder_factory(sample_builder: type[Builder], tmp_path: Path) -> None:
    """Test func for builder_factory."""
    # check the cls
    assert_with_msg(
        issubclass(sample_builder, Builder),
        "Expected sample_builder to be a class",
    )
    # check get_artifacts_dir returns tmp_path / ARTIFACTS_DIR_NAME
    assert_with_msg(
        sample_builder.get_artifacts_dir() == tmp_path / Builder.ARTIFACTS_DIR_NAME,
        "Expected artifacts dir to be in tmp_path",
    )
    # check artifacts are created in tmp_path
    sample_builder()
    assert_with_msg(
        (
            sample_builder.get_artifacts_dir() / f"sample-{platform.system()}.txt"
        ).exists(),
        "Expected artifact to be created",
    )

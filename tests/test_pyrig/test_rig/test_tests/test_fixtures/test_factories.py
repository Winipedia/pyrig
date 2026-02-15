"""test module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.base import ConfigFile


@pytest.fixture
def sample_config_file(
    config_file_factory: Callable[
        [type[ConfigFile[dict[str, Any]]]], type[ConfigFile[dict[str, Any]]]
    ],
) -> type[ConfigFile[dict[str, Any]]]:
    """Create a sample config file class for testing the factory."""

    class SampleConfigFile(config_file_factory(ConfigFile)):  # type: ignore [misc]
        """Sample config file for testing."""

        def parent_path(self) -> Path:
            """Get the parent path."""
            return Path()

        def _load(self) -> dict[str, Any]:
            """Load the config."""
            return {}

        def _dump(self, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config."""

        def extension(self) -> str:
            """Get the file extension."""
            return "test"

        def _configs(self) -> dict[str, Any]:
            """Get the configs."""
            return {"key": "value"}

    return SampleConfigFile


def test_config_file_factory(
    sample_config_file: type[ConfigFile[dict[str, Any]]], tmp_path: Path
) -> None:
    """Test that config_file_factory wraps path to use tmp_path."""
    assert issubclass(sample_config_file, ConfigFile), (
        "Expected sample_config_file to be a class"
    )
    # The factory should wrap the path method to use tmp_path
    path = sample_config_file().path()

    # The path should be inside tmp_path
    assert str(path).startswith(str(tmp_path)), (
        f"Expected path {path} to start with {tmp_path}"
    )

    # The path should have the correct extension
    assert path.suffix == ".test", f"Expected extension '.test', got {path.suffix}"

    assert path.name == "sample.test", (
        f"Expected filename 'sample.test', got {path.name}"
    )

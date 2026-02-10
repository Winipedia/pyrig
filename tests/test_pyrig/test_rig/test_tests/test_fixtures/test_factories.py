"""test module."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.base import ConfigFile


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
        def _load(cls) -> dict[str, Any]:
            """Load the config."""
            return {}

        @classmethod
        def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config."""

        @classmethod
        def get_file_extension(cls) -> str:
            """Get the file extension."""
            return "test"

        @classmethod
        def _get_configs(cls) -> dict[str, Any]:
            """Get the configs."""
            return {"key": "value"}

    return SampleConfigFile


def test_config_file_factory(
    sample_config_file: type[ConfigFile], tmp_path: Path
) -> None:
    """Test that config_file_factory wraps get_path to use tmp_path."""
    assert issubclass(sample_config_file, ConfigFile), (
        "Expected sample_config_file to be a class"
    )
    # The factory should wrap the get_path method to use tmp_path
    path = sample_config_file.get_path()

    # The path should be inside tmp_path
    assert str(path).startswith(str(tmp_path)), (
        f"Expected path {path} to start with {tmp_path}"
    )

    # The path should have the correct extension
    assert path.suffix == ".test", f"Expected extension '.test', got {path.suffix}"

    assert path.name == "sample.test", (
        f"Expected filename 'sample.test', got {path.name}"
    )

"""Factory fixtures for creating test-safe ConfigFile and Builder instances.

Provides factory fixtures that create dynamic subclasses with file operations
redirected to pytest's ``tmp_path``, enabling isolated testing without affecting
real files or build artifacts.

Fixtures:
    config_file_factory: Creates ConfigFile subclasses with ``get_path()``
        redirected to tmp_path.
    builder_factory: Creates Builder subclasses with ``get_artifacts_dir()``
        redirected to tmp_path.
"""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any

import pytest

from pyrig.dev.builders.base.base import Builder
from pyrig.dev.configs.base.base import ConfigFile, ConfigType


@pytest.fixture
def config_file_factory[T: ConfigFile](
    tmp_path: Path,
) -> Callable[[type[T]], type[T]]:
    """Provide a factory for creating test-safe ConfigFile subclasses.

    Creates dynamic subclasses that redirect ``get_path()`` to pytest's
    tmp_path for isolated testing.

    Args:
        tmp_path: Pytest's temporary directory, auto-provided per test.

    Returns:
        Factory function ``(type[T]) -> type[T]`` that wraps a ConfigFile
        subclass with tmp_path-based file operations.
    """

    def _make_test_config(
        base_class: type[T],
    ) -> type[T]:
        """Create a test config class that uses tmp_path.

        Args:
            base_class: The ConfigFile subclass to wrap.

        Returns:
            A subclass with get_path() redirected to tmp_path.
        """

        class TestConfigFile(base_class):  # type: ignore [misc, valid-type]
            """Test config file with tmp_path override."""

            @classmethod
            def get_parent_path(cls) -> Path:
                """Get the parent path in tmp_path.

                Returns:
                    Path within tmp_path.
                """
                path = super().get_parent_path()
                return Path(tmp_path / path)

            @classmethod
            def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
                """Dump the config file."""
                with chdir(tmp_path):
                    super()._dump(config)

            @classmethod
            def _load(cls) -> ConfigType:
                """Load the config file."""
                with chdir(tmp_path):
                    return super()._load()

        return TestConfigFile  # ty:ignore[invalid-return-type]

    return _make_test_config


@pytest.fixture
def builder_factory[T: Builder](tmp_path: Path) -> Callable[[type[T]], type[T]]:
    """Provide a factory for creating test-safe Builder subclasses.

    Creates dynamic subclasses that redirect ``get_artifacts_dir()`` to pytest's
    tmp_path for isolated artifact generation testing.

    Args:
        tmp_path: Pytest's temporary directory, auto-provided per test.

    Returns:
        Factory function ``(type[T]) -> type[T]`` that wraps a Builder
        subclass with tmp_path-based artifact output.
    """

    def _make_test_builder(base_class: type[T]) -> type[T]:
        """Create a test builder class that uses tmp_path.

        Args:
            base_class: The Builder subclass to wrap.

        Returns:
            A subclass with get_artifacts_dir() redirected to tmp_path.
        """

        class TestBuilder(base_class):  # type: ignore [misc, valid-type]
            """Test builder with tmp_path override."""

            @classmethod
            def get_artifacts_dir(cls) -> Path:
                """Get the artifacts directory in tmp_path.

                Returns:
                    Path within tmp_path.
                """
                return Path(tmp_path / cls.ARTIFACTS_DIR_NAME)

        return TestBuilder  # ty:ignore[invalid-return-type]

    return _make_test_builder

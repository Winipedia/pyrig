"""Factory fixtures for creating test-safe ConfigFile instances.

Provides factory fixtures that create dynamic subclasses with file operations
redirected to pytest's ``tmp_path``, enabling isolated testing without affecting
real files or build artifacts.

Fixtures:
    config_file_factory: Creates ConfigFile subclasses with ``get_path()``
        redirected to tmp_path. Also works for BuilderConfigFile subclasses.
"""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any

import pytest

from pyrig.dev.configs.base.base import ConfigFile


@pytest.fixture
def config_file_factory[T: ConfigFile](
    tmp_path: Path,
) -> Callable[[type[T]], type[T]]:
    """Provide a factory for creating test-safe ConfigFile subclasses.

    Creates dynamic subclasses that redirect all file operations to pytest's
    tmp_path for isolated testing. Overrides ``get_path()``, ``get_parent_path()``,
    ``_dump()``, ``_load()``, and ``create_file()`` to ensure complete isolation.

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
            def get_path(cls) -> Path:
                """Get the file path redirected to tmp_path.

                Returns:
                    Path within tmp_path.
                """
                path = super().get_path()
                # append tmp_path to path if not already in tmp_path
                if not (path.is_relative_to(tmp_path) or Path.cwd() == tmp_path):
                    path = tmp_path / path
                return path

            @classmethod
            def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
                """Write config to tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    super()._dump(config)

            @classmethod
            def _load(cls) -> dict[str, Any] | list[Any]:
                """Load config from tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    return super()._load()

            @classmethod
            def get_parent_path(cls) -> Path:
                """Get parent path redirected to tmp_path for test isolation."""
                # append tmp_path to path if not already in tmp_path
                path = super().get_parent_path()
                if not (path.is_relative_to(tmp_path) or Path.cwd() == tmp_path):
                    path = tmp_path / path
                return path

            @classmethod
            def create_file(cls) -> None:
                """Create file in tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    super().create_file()

        return TestConfigFile  # ty:ignore[invalid-return-type]

    return _make_test_config

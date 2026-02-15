"""Factory fixtures for creating test-safe ConfigFile instances.

Provides factory fixtures that create dynamic subclasses with file operations
redirected to pytest's ``tmp_path``, enabling isolated testing without affecting
real files or build artifacts.

Fixtures:
    config_file_factory: Creates ConfigFile subclasses with ``path()``
        redirected to tmp_path. Also works for BuilderConfigFile subclasses.
"""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any

import pytest

from pyrig.rig.configs.base.base import ConfigFile


@pytest.fixture
def config_file_factory[T: ConfigFile[dict[str, Any] | list[Any]]](
    tmp_path: Path,
) -> Callable[[type[T]], type[T]]:
    """Provide a factory for creating test-safe ConfigFile subclasses.

    Creates dynamic subclasses that redirect all file operations to pytest's
    tmp_path for isolated testing. Overrides ``path()``, ``parent_path()``,
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
            A subclass with path() redirected to tmp_path.
        """

        class TestConfigFile(base_class):  # type: ignore [misc, valid-type]
            """Test config file with tmp_path override."""

            def path(self) -> Path:
                """Get the file path redirected to tmp_path.

                Returns:
                    Path within tmp_path.
                """
                path = super().path()
                # append tmp_path to path if not already in tmp_path
                if not (path.is_relative_to(tmp_path) or Path.cwd() == tmp_path):
                    path = tmp_path / path
                return path

            def _dump(self, config: dict[str, Any] | list[Any]) -> None:
                """Write config to tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    super()._dump(config)

            def _load(self) -> dict[str, Any] | list[Any]:
                """Load config from tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    return super()._load()

            def parent_path(self) -> Path:
                """Get parent path redirected to tmp_path for test isolation."""
                # append tmp_path to path if not already in tmp_path
                path = super().parent_path()
                if not (path.is_relative_to(tmp_path) or Path.cwd() == tmp_path):
                    path = tmp_path / path
                return path

            def create_file(self) -> None:
                """Create file in tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    super().create_file()

        return TestConfigFile  # ty:ignore[invalid-return-type]

    return _make_test_config

"""Shared pytest fixtures for testing ``ConfigFile`` subclasses in isolation.

Provides a factory that redirects a ``ConfigFile`` subclass's file operations
to pytest's ``tmp_path`` so tests never touch real project files.
"""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.rig.configs.base.config_file import ConfigData, ConfigFile


@pytest.fixture
def config_file_factory[T: ConfigFile[ConfigData]](
    tmp_path: Path,
) -> Callable[[type[T]], type[T]]:
    """Return a factory that wraps a ``ConfigFile`` subclass for isolated testing.

    The factory creates a dynamic subclass that redirects all file operations
    to pytest's ``tmp_path``. This prevents tests from reading or writing
    real project files. The following methods are overridden to enforce
    isolation:

    - ``path()`` and ``parent_path()``: prepend ``tmp_path`` to the original
      path if it is not already inside ``tmp_path`` and the current working
      directory is not ``tmp_path``.
    - ``_dump()`` and ``_load()``: change the working directory to
      ``tmp_path`` before delegating to the parent implementation.
    - ``create_file()``: changes the working directory to ``tmp_path`` before
      delegating to the parent implementation.

    Args:
        tmp_path: Pytest's per-test temporary directory.

    Returns:
        A callable ``(type[T]) -> type[T]`` that accepts a ``ConfigFile``
        subclass and returns a test-safe subclass with ``tmp_path``-based
        file operations.
    """

    def _make_test_config(
        base_class: type[T],
    ) -> type[T]:
        """Wrap ``base_class`` with ``tmp_path``-redirected file operations.

        Args:
            base_class: The ``ConfigFile`` subclass to wrap.

        Returns:
            A subclass of ``base_class`` with all file paths redirected to
            ``tmp_path``.
        """

        class TestConfigFile(base_class):  # ty: ignore[unsupported-base]
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

            def _dump(self, configs: ConfigData) -> None:
                """Write config to tmp_path, ensuring isolated test execution."""
                with chdir(tmp_path):
                    super()._dump(configs)

            def _load(self) -> ConfigData:
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

"""Shared pytest fixtures for creating temporary modules and packages.

Provides callables that build real Python modules and packages on disk (with
the appropriate ``__init__.py`` hierarchy) and import them, for tests that need
live module objects to introspect.
"""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest

from pyrig.core.introspection.modules import import_module_with_file_fallback
from pyrig.core.introspection.packages import (
    import_package_with_dir_fallback,
    make_package_dir,
)
from pyrig.core.introspection.paths import path_as_module_name


@pytest.fixture
def create_source_package(
    tmp_source_root_path: Path, create_package: Callable[[Path], ModuleType]
) -> Callable[[Path], ModuleType]:
    """Return a callable that creates a Python package under the temporary source root.

    Wraps ``create_package`` with a ``chdir`` to ``tmp_source_root_path``
    so that all relative path operations resolve within the temporary source
    tree.

    Args:
        tmp_source_root_path: Temporary source root directory.
        create_package: Fixture that creates a package from a relative path.

    Returns:
        A callable ``(path) -> ModuleType`` that creates and imports the
        package at ``path`` relative to the temporary source root.
    """

    def create(path: Path) -> ModuleType:
        """Create the package relative to the source root."""
        with chdir(tmp_source_root_path):
            return create_package(path)

    return create


@pytest.fixture
def create_package() -> Callable[[Path], ModuleType]:
    """Return a callable that creates a Python package at a given path.

    The returned function initializes the full directory tree as a package
    hierarchy by adding ``__init__.py`` files up to the current working
    directory, then imports and returns the package.

    Returns:
        A callable ``(path) -> ModuleType`` that creates and imports the
        package at ``path``.
    """

    def create(path: Path) -> ModuleType:
        """Create a package from the given path."""
        make_package_dir(path, until=(), content="")
        return import_package_with_dir_fallback(path, name=path_as_module_name(path))

    return create


@pytest.fixture
def create_module() -> Callable[[Path], ModuleType]:
    """Return a callable that creates a Python module at a given path.

    The returned function ensures the parent directory is a proper package
    hierarchy (adding ``__init__.py`` files up to the current working
    directory), touches the module file, and imports it.

    Returns:
        A callable ``(path) -> ModuleType`` that creates and imports the
        module at ``path``.
    """

    def create(path: Path) -> ModuleType:
        """Create a module from the given path."""
        make_package_dir(path.parent, until=(), content="")
        path.touch()
        return import_module_with_file_fallback(path, name=path_as_module_name(path))

    return create

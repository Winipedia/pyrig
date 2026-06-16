"""Shared pytest fixtures providing temporary project/source/package roots.

Builds a temporary directory tree mirroring the project's layout (project root
→ source root → package root) so tests can operate on a realistic, isolated
copy of the project structure.
"""

from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

from pyrig.rig.tools.package_manager import PackageManager


@pytest.fixture
def tmp_package_root_path(
    tmp_project_root_path: Path,
    tmp_source_root_path: Path,
    create_source_package: Callable[[Path], ModuleType],
) -> tuple[Path, ModuleType]:
    """Provide the temporary package root directory and its imported package module.

    Creates the package root directory under the temporary source root,
    initializes it as a Python package, and returns both the path and the
    imported module.

    Args:
        tmp_project_root_path: Temporary project root directory.
        tmp_source_root_path: Temporary source root directory.
        create_source_package: Fixture for creating packages in the source root.

    Returns:
        Tuple of ``(path, package)`` where ``path`` is the package root
        directory and ``package`` is the imported package module.
    """
    path = tmp_project_root_path / PackageManager.I.package_root()

    package = create_source_package(path.relative_to(tmp_source_root_path))
    return path, package


@pytest.fixture
def tmp_source_root_path(tmp_project_root_path: Path) -> Path:
    """Provide the temporary source root directory.

    Creates the source root directory inside the temporary project root.

    Args:
        tmp_project_root_path: Temporary project root directory.

    Returns:
        Path to the temporary source root directory.
    """
    path = tmp_project_root_path / PackageManager.I.source_root()
    path.mkdir()
    return path


@pytest.fixture
def tmp_project_root_path(tmp_path: Path) -> Path:
    """Provide a temporary project root directory named after the current project.

    Args:
        tmp_path: Pytest's per-test temporary directory.

    Returns:
        Path to the temporary project root directory.
    """
    path = tmp_path / PackageManager.I.project_name()
    path.mkdir()
    return path

"""test module."""

from pathlib import Path
from types import ModuleType

import pyrig


def test_tmp_project_root_path(tmp_path: Path, tmp_project_root_path: Path) -> None:
    """Test function."""
    assert tmp_project_root_path == tmp_path / "pyrig"


def test_tmp_source_root_path(
    tmp_project_root_path: Path, tmp_source_root_path: Path
) -> None:
    """Test function."""
    assert tmp_source_root_path == tmp_project_root_path / "src"


def test_tmp_package_root_path(
    tmp_source_root_path: Path, tmp_package_root_path: tuple[Path, ModuleType]
) -> None:
    """Test function."""
    package_root, package = tmp_package_root_path
    assert package_root == tmp_source_root_path / "pyrig"
    assert isinstance(package, ModuleType)
    assert package.__name__ == pyrig.__name__

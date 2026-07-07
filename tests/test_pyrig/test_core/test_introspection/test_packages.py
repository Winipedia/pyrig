"""Test module."""

from contextlib import chdir
from pathlib import Path

import pyrig
from pyrig.core import introspection
from pyrig.core.introspection import packages
from pyrig.core.introspection.packages import (
    discover_modules,
    make_init_file,
    make_init_files,
    make_package_dir,
)
from pyrig.rig.tests import mirror_test


def test_make_init_file(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        path = Path.cwd() / "__init__.py"
        assert not path.exists()
        make_init_file(Path.cwd(), content="Hello")
        assert path.exists()
        assert path.read_text() == "Hello"


def test_make_package_dir(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        path = Path() / "test" / "package" / "sub_package"
        make_package_dir(path, root=Path() / "test", content="")
        # `root` is the last directory processed and receives an __init__.py.
        assert (Path() / "test" / "__init__.py").exists()
        assert (Path() / "test" / "package" / "__init__.py").exists()
        assert (Path() / "test" / "package" / "sub_package" / "__init__.py").exists()
        assert not (Path() / "__init__.py").exists()


def test_discover_modules() -> None:
    """Test function."""
    modules = list(discover_modules(pyrig))
    assert pyrig not in modules
    # modules should be included, but not the package itself
    assert mirror_test in modules
    assert packages in modules
    # is a package module, not a regular module, so should be excluded
    assert introspection not in modules


def test_make_init_files(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        assert not Path("__init__.py").exists()
        folder = Path("folder")
        folder2 = Path("folder2")
        folder_init = folder / "__init__.py"
        assert not folder_init.exists()
        folder.mkdir()
        folder2.mkdir()
        make_init_files((Path(),), content="")
        assert Path("__init__.py").exists()
        make_init_files((folder, folder2), content="")
        assert folder_init.exists()
        assert (folder2 / "__init__.py").exists()

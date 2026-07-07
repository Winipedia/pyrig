"""Test module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

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
        path = Path.cwd() / "test" / "package" / "sub_package"
        make_package_dir(path, until=(Path.cwd() / "test",), content="")
        assert not (Path.cwd() / "test" / "__init__.py").exists()
        assert (Path.cwd() / "test" / "package" / "__init__.py").exists()
        assert (
            Path.cwd() / "test" / "package" / "sub_package" / "__init__.py"
        ).exists()
        assert not (Path.cwd() / "__init__.py").exists()


def test_make_package_dir_path_not_under_cwd(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    """Test the loop exhausts when the path shares no ancestor with cwd."""
    cwd_dir = tmp_path / "cwd"
    cwd_dir.mkdir()
    elsewhere = tmp_path / "elsewhere" / "deep" / "pkg"

    # Mock make_init_file so the test does not write __init__.py files into
    # ancestor directories like /tmp or /.
    make_init_file_mock = mocker.patch(
        make_init_file.__module__ + "." + make_init_file.__name__, return_value=None
    )

    with chdir(cwd_dir):
        make_package_dir(elsewhere, until=(), content="")

    assert elsewhere.exists()
    # The for loop should have iterated over the path and every ancestor
    # without breaking, since neither cwd nor Path() appear in the chain.
    expected_call_count = 1 + len(elsewhere.parents)
    assert make_init_file_mock.call_count == expected_call_count


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

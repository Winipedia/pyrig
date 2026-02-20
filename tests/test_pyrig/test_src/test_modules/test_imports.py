"""tests module."""

import sys
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest

import pyrig
from pyrig.rig.tests import mirror_test
from pyrig.src.modules import imports
from pyrig.src.modules.imports import (
    import_package_from_dir,
    import_package_with_dir_fallback,
    import_package_with_dir_fallback_with_default,
    iter_modules,
    module_is_package,
    walk_package,
)
from tests.test_pyrig.test_rig.test_tests import test_mirror_test


def test_iter_modules(tmp_path: Path) -> None:
    """Test function."""
    # Create a temporary package with known content
    with chdir(tmp_path):
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        module_file = package_dir / "test_module.py"
        module_file.write_text('"""Test module."""\n')
        package = import_package_from_dir(package_dir)

        modules = iter_modules(package)
        modules_names = [m.__name__ for m, _ in modules]
        assert modules_names == [package.__name__ + ".test_module"], (
            f"Expected [package.test_module], got {modules}"
        )


def test_walk_package() -> None:
    """Test function."""
    modules = list(walk_package(pyrig))

    module_types = {m for m, _ in modules}

    assert pyrig in module_types
    assert mirror_test in module_types
    assert imports in module_types

    assert test_mirror_test not in module_types


def test_module_is_package() -> None:
    """Test function."""
    # Create a mock module with __path__ attribute (package)
    mock_package = ModuleType("test_package")
    mock_package.__path__ = ["some/path"]

    # Create a mock module without __path__ attribute (regular module)
    mock_module = ModuleType("test_module")

    assert module_is_package(mock_package) is True, (
        "Expected module with __path__ to be identified as package"
    )

    assert module_is_package(mock_module) is False, (
        "Expected module without __path__ to not be identified as package"
    )


def test_import_package_with_dir_fallback(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_package_with_dir_fallback(non_existing_dir)
        # import nonexisting againto ccheck if somehow cached in sy
        with pytest.raises(FileNotFoundError):
            import_package_with_dir_fallback(non_existing_dir)

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        init_file = existing_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_with_dir_fallback(existing_dir)
        assert package.__name__ == "existing"


def test_import_package_from_dir(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_package_from_dir(non_existing_dir)

        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_from_dir(package_dir)
        assert package.__name__ == "test_package"

        subdir = package_dir / "subdir"
        subdir.mkdir()
        init_file = subdir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_from_dir(subdir)
        assert package.__name__ == "test_package.subdir"

        # check all are now registered in sys.modules
        assert "test_package" in sys.modules
        assert "test_package.subdir" in sys.modules


def test_import_package_with_dir_fallback_with_default() -> None:
    """Test function."""
    assert import_package_with_dir_fallback_with_default(Path("non_existing")) is None
    assert (
        import_package_with_dir_fallback_with_default(
            Path("non_existing"), default="default"
        )
        == "default"
    )

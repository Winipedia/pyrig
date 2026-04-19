"""tests module."""

import re
import sys
from contextlib import chdir
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

import pyrig
from pyrig.core.introspection import imports
from pyrig.core.introspection.imports import (
    import_package_from_dir,
    import_package_with_dir_fallback,
    iter_modules,
    walk_package,
)
from pyrig.rig.tests import mirror_test


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
        package = import_package_from_dir(package_dir, name="test_package")

        modules = iter_modules(package)
        modules_names = [m.__name__ for m, _ in modules]
        assert modules_names == [package.__name__ + ".test_module"], (
            f"Expected [package.test_module], got {modules}"
        )

        exclude_pattern = re.compile(r"^test_package\.test_module$")
        modules = iter_modules(package, exclude=(exclude_pattern,))
        assert list(modules) == [], f"Expected no modules, got {modules}"


def test_import_package_with_dir_fallback(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_package_with_dir_fallback(non_existing_dir, name="non_existing")
        # import nonexisting again to check if somehow cached in sys
        with pytest.raises(FileNotFoundError):
            import_package_with_dir_fallback(non_existing_dir, name="non_existing")

        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        init_file = existing_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_with_dir_fallback(existing_dir, name="existing")
        assert package.__name__ == "existing"

        import_package_from_dir_mock = mocker.patch(
            import_package_from_dir.__module__ + "." + import_package_from_dir.__name__,
            return_value=None,
        )
        # test that if the package is already imported it doesn't call the fallback
        package = import_package_with_dir_fallback(existing_dir, name="existing")
        assert package.__name__ == "existing"
        import_package_from_dir_mock.assert_not_called()


def test_import_package_from_dir(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_package_from_dir(non_existing_dir, name="non_existing")

        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_from_dir(package_dir, name="test_package")
        assert package.__name__ == "test_package"

        subdir = package_dir / "subdir"
        subdir.mkdir()
        init_file = subdir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_from_dir(subdir, name="test_package.subdir")
        assert package.__name__ == "test_package.subdir"

        # check all are now registered in sys.modules
        assert "test_package" in sys.modules
        assert "test_package.subdir" in sys.modules

        # check if loader is None that it raises ImportError
        # patch the func spec_from_loader to return None
        spec_from_loader_mock = mocker.patch(
            "importlib.util.spec_from_loader", return_value=None
        )
        with pytest.raises(ImportError):
            import_package_from_dir(subdir, name="test_package.subdir")

        spec_from_loader_mock.assert_called_once()


def test_walk_package() -> None:
    """Test function."""
    modules = list(walk_package(pyrig))

    module_types = {m for m, _ in modules}

    assert pyrig not in module_types
    assert mirror_test in module_types
    assert imports in module_types

"""Test module."""

import sys
from contextlib import chdir
from pathlib import Path

import pytest
import typer
from pytest_mock import MockerFixture

import pyrig
from pyrig.core import introspection
from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.introspection import packages
from pyrig.core.introspection.packages import (
    discover_all_subclasses_across_package,
    discover_modules,
    import_package_from_dir,
    import_package_with_dir_fallback,
    make_init_file,
    make_package_dir,
    src_package_is_package,
    src_package_is_pyrig,
    walk_package,
)
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests import mirror_test
from pyrig.rig.tools.base.tool import Tool


def test_make_init_file(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        make_init_file(Path.cwd(), content="")
        assert (Path.cwd() / "__init__.py").exists(), (
            "Expected __init__.py file to be created"
        )


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


def test_src_package_is_pyrig() -> None:
    """Test function."""
    assert src_package_is_pyrig()


def test_src_package_is_package() -> None:
    """Test function."""
    assert src_package_is_package(pyrig)
    assert not src_package_is_package(typer)


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

        dir_name = test_import_package_with_dir_fallback.__name__
        existing_dir = tmp_path / dir_name
        existing_dir.mkdir()
        init_file = existing_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_with_dir_fallback(existing_dir, name=dir_name)
        assert package.__name__ == dir_name

        import_package_from_dir_mock = mocker.patch(
            import_package_from_dir.__module__ + "." + import_package_from_dir.__name__,
            return_value=None,
        )
        # test that if the package is already imported it doesn't call the fallback
        package = import_package_with_dir_fallback(existing_dir, name=dir_name)
        assert package.__name__ == dir_name
        import_package_from_dir_mock.assert_not_called()


def test_import_package_from_dir(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        non_existing_dir = tmp_path / "non_existing"
        assert not non_existing_dir.exists()
        with pytest.raises(FileNotFoundError):
            import_package_from_dir(non_existing_dir, name="non_existing")

        dir_name = test_import_package_from_dir.__name__
        package_dir = tmp_path / dir_name
        package_dir.mkdir()
        init_file = package_dir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_from_dir(package_dir, name=dir_name)
        assert package.__name__ == dir_name

        subdir = package_dir / "subdir"
        subdir.mkdir()
        init_file = subdir / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        package = import_package_from_dir(subdir, name=f"{dir_name}.subdir")
        assert package.__name__ == f"{dir_name}.subdir"

        # check all are now registered in sys.modules
        assert dir_name in sys.modules
        assert f"{dir_name}.subdir" in sys.modules


def test_walk_package() -> None:
    """Test function."""
    modules = list(walk_package(pyrig))

    module_types = {m for m, _ in modules}

    assert pyrig not in module_types
    assert mirror_test in module_types
    assert packages in module_types


def test_discover_all_subclasses_across_package() -> None:
    """Test function."""
    subclasses = tuple(
        discover_all_subclasses_across_package(cls=DependencySubclass, package=pyrig)
    )
    assert ConfigFile in subclasses
    assert Tool in subclasses

    assert all(issubclass(subcls, DependencySubclass) for subcls in subclasses)


def test_discover_modules() -> None:
    """Test function."""
    modules = list(discover_modules(pyrig))
    assert pyrig not in modules
    # modules should be included, but not the package itself
    assert mirror_test in modules
    assert packages in modules
    # is a package module, not a regular module, so should be excluded
    assert introspection not in modules

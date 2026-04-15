"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.core.introspection.paths import (
    module_file_path,
    module_name_as_path,
    package_dir_path,
    package_name_as_path,
    path_as_module_name,
)
from pyrig.rig import tools
from pyrig.rig.tests import mirror_test


def test_module_file_path(
    create_module: Callable[[Path], ModuleType], tmp_path: Path
) -> None:
    """Test function."""
    with chdir(tmp_path):
        expected_path = Path(test_module_file_path.__name__) / Path(
            "subpackage/module.py"
        )
        module = create_module(expected_path)
        assert module_file_path(module) == expected_path.resolve()

    assert (
        module_file_path(mirror_test)
        == Path("src/pyrig/rig/tests/mirror_test.py").resolve()
    )


def test_package_dir_path(
    create_package: Callable[[Path], ModuleType], tmp_path: Path
) -> None:
    """Test function."""
    with chdir(tmp_path):
        expected_dir = Path(test_package_dir_path.__name__) / "subpackage"
        package = create_package(expected_dir)
        assert package_dir_path(package) == expected_dir.resolve()

    assert package_dir_path(tools) == Path("src/pyrig/rig/tools").resolve()


def test_package_name_as_path() -> None:
    """Test function."""
    name = "package.subpackage.module"
    expected_path = Path("package/subpackage/module")
    assert package_name_as_path(name) == expected_path


def test_module_name_as_path() -> None:
    """Test function."""
    name = "package.subpackage.module"
    expected_path = Path("package/subpackage/module.py")
    assert module_name_as_path(name) == expected_path


def test_path_as_module_name() -> None:
    """Test function."""
    path = Path("package/subpackage/module.py")
    expected_name = "package.subpackage.module"
    assert path_as_module_name(path) == expected_name

    # path with no .py suffix
    path_no_suffix = Path("package/subpackage/module")
    assert path_as_module_name(path_no_suffix) == expected_name

"""module."""

from pathlib import Path
from types import ModuleType

import pytest

from pyrig.core.introspection.paths import (
    module_file_path,
    module_name_as_path,
    package_name_as_path,
)
from pyrig.rig.tests import mirror


def test_module_file_path(tmp_path: Path) -> None:
    """Test function."""
    expected_path = tmp_path / "subpackage/module.py"
    module = ModuleType("subpackage.module")
    module.__file__ = str(expected_path)
    assert module_file_path(module) == expected_path

    assert module_file_path(mirror) == Path("src/pyrig/rig/tests/mirror.py").resolve()

    # make ModuleType with __file__ attribute as None
    module_no_file = ModuleType("module_no_file")
    module_no_file.__file__ = None
    with pytest.raises(AttributeError, match=r"module .* has no __file__"):
        module_file_path(module_no_file)


def test_module_name_as_path() -> None:
    """Test function."""
    name = "package.subpackage.module"
    expected_path = Path("package/subpackage/module.py")
    assert module_name_as_path(name) == expected_path


def test_package_name_as_path() -> None:
    """Test function."""
    name = "package.subpackage.module"
    expected_path = Path("package/subpackage/module")
    assert package_name_as_path(name) == expected_path

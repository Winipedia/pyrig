"""Test module."""

from pytest_mock import MockerFixture

import pyrig
from pyrig import core, rig
from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.introspection.dependencies import (
    all_deps_depending_on_dep,
    discover_equivalent_modules_across_dependents,
    discover_subclasses_across_dependencies,
)
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tools.base.tool import Tool


def test_discover_equivalent_modules_across_dependents(mocker: MockerFixture) -> None:
    """Test function."""
    # Test getting the same module from all packages depending on pyrig
    modules = discover_equivalent_modules_across_dependents(core, pyrig)
    assert core not in modules

    # mock all_deps_depending_on_dep to return a fake dependent package
    # the following is mostly to get 100% test coverage
    mock_all_deps = mocker.patch(
        all_deps_depending_on_dep.__module__ + "." + all_deps_depending_on_dep.__name__,
        return_value=[pyrig],
    )
    modules = tuple(discover_equivalent_modules_across_dependents(core, pyrig))
    assert core in modules
    mock_all_deps.assert_called_once()


def test_discover_subclasses_across_dependencies() -> None:
    """Test func."""
    subclasses = tuple(
        discover_subclasses_across_dependencies(DependencySubclass, pyrig, rig)
    )
    assert ConfigFile in subclasses
    assert Tool in subclasses


def test_all_deps_depending_on_dep() -> None:
    """Test function."""
    packages = [*all_deps_depending_on_dep(pyrig), pyrig]
    assert pyrig in packages, f"Expected pyrig in packages, got {packages}"

"""Test module."""

import pyrig
from pyrig import core, rig
from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.introspection.dependencies import (
    all_deps_depending_on_dep,
    discover_equivalent_modules_across_dependents,
    discover_subclasses_across_dependents,
    pyrig_dependency_graph,
)
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tools.base.tool import Tool


def test_discover_equivalent_modules_across_dependents() -> None:
    """Test function."""
    # Test getting the same module from all packages depending on pyrig
    # until_package is only defined to get 100% test coverage
    # practically its only needed for subsequent dependent projects
    modules = discover_equivalent_modules_across_dependents(
        core, pyrig, until_package=pyrig
    )
    # Should at least include pyrig.src itself
    assert core in modules, f"Expected pyrig.src in modules, got {modules}"


def test_discover_subclasses_across_dependents() -> None:
    """Test func."""
    subclasses = tuple(
        discover_subclasses_across_dependents(DependencySubclass, pyrig, rig)
    )
    assert ConfigFile in subclasses
    assert Tool in subclasses


def test_all_deps_depending_on_dep() -> None:
    """Test function."""
    packages = [*all_deps_depending_on_dep(pyrig), pyrig]
    assert pyrig in packages, f"Expected pyrig in packages, got {packages}"


def test_pyrig_dependency_graph() -> None:
    """Test function."""
    graph = pyrig_dependency_graph()

    # should only be pyrig and its dependents, not unrelated packages
    assert graph.nodes() == {pyrig.__name__}

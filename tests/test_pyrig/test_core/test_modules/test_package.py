"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_package
"""

from contextlib import chdir
from pathlib import Path

import pyrig
from pyrig import core, rig
from pyrig.core.dependency_subclass import DependencySubclass
from pyrig.core.modules.package import (
    all_deps_depending_on_dep,
    discover_equivalent_modules_across_dependents,
    discover_subclasses_across_dependents,
    make_init_module,
    make_package_dir,
    pyrig_dependency_graph,
)
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tools.base.tool import Tool


def test_discover_equivalent_modules_across_dependents() -> None:
    """Test function."""
    # Test getting the same module from all packages depending on pyrig

    modules = discover_equivalent_modules_across_dependents(core, pyrig)
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


def test_make_init_module(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        make_init_module(Path.cwd(), content="")
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

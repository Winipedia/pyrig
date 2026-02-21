"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_package
"""

from contextlib import chdir
from pathlib import Path

import pyrig
from pyrig import src
from pyrig.src.modules.package import (
    all_deps_depending_on_dep,
    create_package,
    discover_equivalent_modules_across_dependents,
    discover_subclasses_across_dependents,
)
from tests.test_pyrig.test_src import test_modules
from tests.test_pyrig.test_src.test_modules.test_class_ import (
    AbstractParent,
    ConcreteChild,
)


def test_discover_equivalent_modules_across_dependents() -> None:
    """Test function."""
    # Test getting the same module from all packages depending on pyrig

    modules = discover_equivalent_modules_across_dependents(src, pyrig)
    # Should at least include pyrig.src itself
    assert len(modules) > 0, f"Expected at least one module, got {modules}"
    assert src in modules, f"Expected pyrig.src in modules, got {modules}"


def test_create_package(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        package_dir = tmp_path / "test_package"
        assert not package_dir.exists()
        package = create_package(package_dir)
        assert package_dir.exists()
        assert package.__name__ == "test_package"
        assert package_dir.is_dir()
        assert (package_dir / "__init__.py").exists()


def test_discover_subclasses_across_dependents() -> None:
    """Test func."""
    subclasses = discover_subclasses_across_dependents(
        AbstractParent, pyrig, test_modules
    )
    assert ConcreteChild in subclasses, (
        f"Expected ConcreteChild in non-abstract subclasses, got {subclasses}"
    )


def test_all_deps_depending_on_dep() -> None:
    """Test function."""
    packages = [*all_deps_depending_on_dep(pyrig), pyrig]
    assert pyrig in packages, f"Expected pyrig in packages, got {packages}"

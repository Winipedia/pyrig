"""module."""

from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pyrig
from pyrig.dev.artifacts.resources.resource import (
    get_all_resources_pkgs_from_deps_depen_on_dep,
    get_resource_path,
)
from pyrig.src.modules.module import import_module_from_path


def test_get_resource_path(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # create a pkg
        pkg_path = tmp_path / "pkg"
        pkg_path.mkdir()
        init_file = pkg_path / "__init__.py"
        init_file.write_text('"""Test package."""\n')
        # create a resource
        resource_path = pkg_path / "resource.txt"
        relative_resource_path = resource_path.relative_to(tmp_path)
        resource_path.write_text("Hello World!")
        # import the pkg
        pkg = import_module_from_path(pkg_path)

        assert get_resource_path("resource.txt", pkg) == relative_resource_path


def test_get_all_resources_pkgs_from_deps_depen_on_dep() -> None:
    """Test function."""
    # Test getting all resources packages from dependencies depending on pyrig
    resources_pkgs = get_all_resources_pkgs_from_deps_depen_on_dep(pyrig)
    # Should at least include pyrig's own resources package
    assert len(resources_pkgs) > 0, (
        f"Expected at least one resources package, got {resources_pkgs}"
    )
    # Check that all returned items are modules
    for pkg in resources_pkgs:
        assert isinstance(pkg, ModuleType), f"Expected module, got {pkg}"
        assert pkg.__name__.endswith(".resources"), f"Expected module, got {pkg}"

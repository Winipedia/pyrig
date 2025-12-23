"""A func that creates __init__.py files for all packages and modules."""

from pyrig.dev.utils.packages import get_namespace_packages
from pyrig.src.modules.path import ModulePath, make_init_module


def make_init_files() -> None:
    """Create __init__.py files for all packages and modules.

    Will not overwrite existing files.
    """
    any_namespace_packages = get_namespace_packages()
    if any_namespace_packages:
        # make init files for all namespace packages
        for package in any_namespace_packages:
            pkg_dir = ModulePath.pkg_name_to_relative_dir_path(package)
            make_init_module(pkg_dir)

"""A func that creates __init__.py files for all packages and modules."""

from pyrig.dev.utils.packages import find_packages
from pyrig.src.modules.module import make_init_module, to_path
from pyrig.src.modules.package import DOCS_DIR_NAME


def get_namespace_packages() -> list[str]:
    """Get all namespace packages."""
    packages = find_packages(depth=None)
    namespace_packages = find_packages(depth=None, include_namespace_packages=True)
    namespace_packages = [
        p for p in namespace_packages if not p.startswith(DOCS_DIR_NAME)
    ]
    return list(set(namespace_packages) - set(packages))


def make_init_files() -> None:
    """Create __init__.py files for all packages and modules.

    Will not overwrite existing files.
    """
    any_namespace_packages = get_namespace_packages()
    if any_namespace_packages:
        # make init files for all namespace packages
        for package in any_namespace_packages:
            make_init_module(to_path(package, is_package=True))

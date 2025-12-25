"""A func that creates __init__.py files for all packages and modules."""

import logging
from concurrent.futures import ThreadPoolExecutor

from pyrig.dev.utils.packages import get_namespace_packages
from pyrig.src.modules.path import ModulePath, make_init_module

logger = logging.getLogger(__name__)


def make_init_files() -> None:
    """Create __init__.py files for all packages and modules.

    Will not overwrite existing files.
    """
    logger.info("Starting __init__.py file creation")
    any_namespace_packages = get_namespace_packages()
    if not any_namespace_packages:
        logger.info(
            "No namespace packages found, all packages already have __init__.py files"
        )
        return

    # make init files for all namespace packages
    pkg_paths = [
        ModulePath.pkg_name_to_relative_dir_path(pkg) for pkg in any_namespace_packages
    ]
    with ThreadPoolExecutor() as executor:
        list(executor.map(make_init_module, pkg_paths))

    logger.info("Created __init__.py files for all namespace packages")

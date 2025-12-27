"""__init__.py file creation for namespace packages.

Automatically creates __init__.py files for namespace packages (PEP 420
packages without __init__.py) to ensure proper importability.
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from pyrig.dev.utils.packages import get_namespace_packages
from pyrig.src.modules.path import ModulePath, make_init_module

logger = logging.getLogger(__name__)


def make_init_files() -> None:
    """Create __init__.py files for all namespace packages.

    Scans the project for namespace packages (directories with Python files
    but no __init__.py) and creates minimal __init__.py files for them.

    The function is idempotent and uses parallel execution for performance.

    Note:
        Created __init__.py files contain a minimal docstring. The docs
        directory is excluded from scanning.
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

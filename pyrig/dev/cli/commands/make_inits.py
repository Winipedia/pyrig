"""__init__.py file creation for namespace packages.

This module provides functionality to automatically create __init__.py files
for all namespace packages (PEP 420 packages without __init__.py) in the
project. This ensures all packages are properly importable and follow
traditional Python package conventions.

The creation process:
1. Discovers all namespace packages in the project
2. Creates __init__.py files for each namespace package
3. Uses parallel execution for faster processing
4. Never overwrites existing __init__.py files

Example:
    >>> from pyrig.dev.cli.commands.make_inits import make_init_files
    >>> make_init_files()
    # Creates __init__.py for all namespace packages
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from pyrig.dev.utils.packages import get_namespace_packages
from pyrig.src.modules.path import ModulePath, make_init_module

logger = logging.getLogger(__name__)


def make_init_files() -> None:
    """Create __init__.py files for all namespace packages in the project.

    Scans the project for namespace packages (directories with Python files
    but no __init__.py) and creates minimal __init__.py files for them. This
    ensures all packages follow traditional Python package conventions and
    are properly importable.

    The function is idempotent - it will not overwrite existing __init__.py
    files, only create missing ones. File creation is parallelized for
    performance.

    Example:
        >>> from pyrig.dev.cli.commands.make_inits import make_init_files
        >>> make_init_files()
        # Output: Created __init__.py files for all namespace packages

    Note:
        - This is automatically called by `pyrig init` during project setup.
        - The created __init__.py files contain a minimal docstring.
        - Namespace packages in the docs directory are excluded.

    See Also:
        - `pyrig.dev.utils.packages.get_namespace_packages`: namespace-pkgs discovery.
        - `pyrig.src.modules.path.make_init_module`: __init__.py file creation.
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

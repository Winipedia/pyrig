"""Automatic test skeleton generation for source code.

Generates test files mirroring the source package structure, creating skeleton
test functions and classes with `NotImplementedError` placeholders for all
untested code.
"""

import logging
from importlib import import_module
from types import ModuleType

from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.src.modules.imports import walk_package

logger = logging.getLogger(__name__)


def make_test_skeletons() -> None:
    """Create test skeleton files for all source code.

    Walks the source package hierarchy and creates corresponding test packages,
    modules, classes, and functions for all untested code.
    """
    logger.info("Creating test skeletons")
    src_package = import_module(PackageManager.I.package_name())
    logger.debug("Source package: %s", src_package.__name__)
    create_tests_for_package(src_package)
    logger.info("Test skeleton creation complete")


def create_tests_for_package(package: ModuleType) -> None:
    """Create test files for all modules in a source package.

    Walks the package hierarchy and creates corresponding test packages and
    modules using parallel execution.

    Args:
        package: The source package to create tests for.
    """
    logger.debug("Creating tests for package: %s", package.__name__)
    all_modules = (m for m, is_pkg in walk_package(package) if not is_pkg)
    # create test modules for all modules
    MirrorTestConfigFile.I.create_test_modules(all_modules)

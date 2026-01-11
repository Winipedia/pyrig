"""Automatic test skeleton generation for source code.

Generates test files mirroring the source package structure, creating skeleton
test functions and classes with NotImplementedError placeholders for all
untested code.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from types import ModuleType

from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.dev.tests.mirror_test import MirrorTestConfigFile
from pyrig.src.modules.imports import walk_package
from pyrig.src.modules.package import create_package
from pyrig.src.modules.path import ModulePath

logger = logging.getLogger(__name__)


def make_test_skeletons() -> None:
    """Create test skeleton files for all source code.

    Walks the source package hierarchy and creates corresponding test packages,
    modules, classes, and functions for all untested code.
    """
    logger.info("Creating test skeletons")
    src_package = import_module(PyprojectConfigFile.L.get_package_name())
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
    all_modules: list[ModuleType] = []
    pkgs_without_modules: list[ModuleType] = []
    for pkg, modules in walk_package(package):
        if not modules:
            pkgs_without_modules.append(pkg)
            continue
        all_modules.extend(modules)

    with ThreadPoolExecutor() as executor:
        list(executor.map(create_test_package, pkgs_without_modules))

    # create test modules for all modules
    MirrorTestConfigFile.L.create_test_modules(all_modules)


def create_test_package(package: ModuleType) -> None:
    """Create a test package for a source package.

    Args:
        package: The source package to create a test package for.
    """
    test_package_name = MirrorTestConfigFile.L.get_test_obj_importpath_from_obj(package)
    test_package_path = ModulePath.pkg_name_to_relative_dir_path(test_package_name)
    # create package if it doesn't exist
    create_package(test_package_path)

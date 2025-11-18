"""Session-level test fixtures and utilities.

This module provides fixtures and test functions that operate at the session scope,
ensuring that project-wide conventions are followed and that the overall project
structure is correct. These fixtures are automatically applied to the test session
through pytest's autouse mechanism.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pyrig
from pyrig import dev
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import (
    PyprojectConfigFile,
)
from pyrig.src.modules.module import (
    get_isolated_obj_name,
    import_module_with_default,
    to_path,
)
from pyrig.src.modules.package import (
    find_packages,
    get_src_package,
    walk_package,
)
from pyrig.src.testing.assertions import assert_with_msg
from pyrig.src.testing.convention import (
    TESTS_PACKAGE_NAME,
    make_test_obj_importpath_from_obj,
    make_untested_summary_error_msg,
)
from pyrig.src.testing.create_tests import create_tests
from pyrig.src.testing.fixtures import autouse_session_fixture

if TYPE_CHECKING:
    from types import ModuleType

logger = logging.getLogger(__name__)


@autouse_session_fixture
def assert_dev_dependencies_config_is_correct() -> None:
    """Verify that the dev dependencies in consts.py are correct.

    This fixture runs once per test session and checks that the dev dependencies
    in consts.py are correct by comparing them to the dev dependencies in
    pyproject.toml.

    Raises:
        AssertionError: If the dev dependencies in consts.py are not correct

    """
    if PyprojectConfigFile.get_package_name() != pyrig.__name__:
        # this const is only used in pyrig
        # to be able to install them with setup.py
        return
    actual_dev_dependencies = PyprojectConfigFile.get_dev_dependencies()
    expected_dev_dependencies = PyprojectConfigFile.get_configs()["tool"]["poetry"][
        "group"
    ]["dev"]["dependencies"].keys()
    assert_with_msg(
        set(actual_dev_dependencies) == set(expected_dev_dependencies),
        "Dev dependencies in consts.py are not correct",
    )


@autouse_session_fixture
def assert_config_files_are_correct() -> None:
    """Verify that the dev dependencies are installed.

    This fixture runs once per test session and checks that the dev dependencies
    are installed by trying to import them.

    Raises:
        ImportError: If a dev dependency is not installed

    """
    subclasses = ConfigFile.get_all_subclasses()
    all_correct = all(subclass.is_correct() for subclass in subclasses)
    # subclasses of ConfigFile
    ConfigFile.init_config_files()

    assert_with_msg(
        all_correct,
        "Config files are not correct. Corrected the files. Please verify the changes.",
    )


@autouse_session_fixture
def assert_no_namespace_packages() -> None:
    """Verify that there are no namespace packages in the project.

    This fixture runs once per test session and checks that all packages in the
    project are regular packages with __init__.py files, not namespace packages.

    Raises:
        AssertionError: If any namespace packages are found

    """
    packages = find_packages(depth=None)
    namespace_packages = find_packages(depth=None, include_namespace_packages=True)

    any_namespace_packages = set(namespace_packages) - set(packages)
    assert_with_msg(
        not any_namespace_packages,
        f"Found namespace packages: {any_namespace_packages}. "
        f"All packages should have __init__.py files.",
    )


@autouse_session_fixture
def assert_all_src_code_in_one_package() -> None:
    """Verify that all source code is in a single package.

    This fixture runs once per test session and checks that there is only one
    source package besides the tests package.

    Raises:
        AssertionError: If there are multiple source packages

    """
    packages = find_packages(depth=0)
    src_package = get_src_package().__name__
    expected_packages = {TESTS_PACKAGE_NAME, src_package}
    assert_with_msg(
        set(packages) == expected_packages,
        f"Expected only packages {expected_packages}, but found {packages}",
    )


@autouse_session_fixture
def assert_src_package_correctly_named() -> None:
    """Verify that the source package is correctly named.

    This fixture runs once per test session and checks that the source package
    is correctly named after the project.

    Raises:
        AssertionError: If the source package is not correctly named

    """
    src_package = get_src_package().__name__
    config = PyprojectConfigFile
    expected_package = config.get_package_name()
    assert_with_msg(
        src_package == expected_package,
        f"Expected source package to be named {expected_package}, "
        f"but it is named {src_package}",
    )


@autouse_session_fixture
def assert_all_modules_tested() -> None:
    """Verify that the project structure is mirrored in tests.

    This fixture runs once per test session and checks that for every package and
    module in the source package, there is a corresponding test package and module.

    Raises:
        AssertionError: If any package or module doesn't have a corresponding test

    """
    src_package = get_src_package()

    # we will now go through all the modules in the src package and check
    # that there is a corresponding test module
    missing_tests_to_module: dict[str, ModuleType] = {}
    for package, modules in walk_package(src_package):
        test_package_name = make_test_obj_importpath_from_obj(package)
        test_package = import_module_with_default(test_package_name)
        if test_package is None:
            missing_tests_to_module[test_package_name] = package

        for module in modules:
            test_module_name = make_test_obj_importpath_from_obj(module)
            test_module = import_module_with_default(test_module_name)
            if test_module is None:
                missing_tests_to_module[test_module_name] = module

    if missing_tests_to_module:
        create_tests()

    msg = f"""Found missing tests. Tests skeletons were automatically created for:
    {make_untested_summary_error_msg(missing_tests_to_module.keys())}
"""
    assert_with_msg(
        not missing_tests_to_module,
        msg,
    )


@autouse_session_fixture
def assert_no_unit_test_package_usage() -> None:
    """Verify that the unit test package is not used in the project.

    This fixture runs once per test session and checks that the unit test package
    is not used in the project.

    Raises:
        AssertionError: If the unit test package is used

    """
    for path in Path().rglob("*.py"):
        assert_with_msg(
            "UnitTest".lower() not in path.read_text(encoding="utf-8"),
            f"Found unit test package usage in {path}. Use pytest instead.",
        )


@autouse_session_fixture
def assert_no_dev_usage_in_non_dev_files() -> None:
    """Verify that any utils from the dev folder are not used in non-dev files.

    E.g. utils can be used anywhere, dev not.

    This fixture runs once per test session and checks that any utils from the
    dev folder are not used in non-dev files.

    Raises:
        AssertionError: If any utils from the dev folder are used in non-dev files

    """
    src_pkg = get_src_package().__name__
    dev_pkg = src_pkg + "." + get_isolated_obj_name(dev)
    dev_path = to_path(dev_pkg, is_package=True)
    usages: list[Path] = []
    for path in Path(src_pkg).rglob("*.py"):
        # check if any part of the path contains dev_path
        if dev_path in path.parents:
            continue

        if dev_pkg in path.read_text(encoding="utf-8"):
            usages.append(path)

    msg = "Found dev utils usage in non-dev files."
    for path in usages:
        msg += f"\n    {path}"

    if src_pkg == pyrig.__name__:
        # pyrigis allowed to use itself
        return

    assert_with_msg(
        not usages,
        msg,
    )


@autouse_session_fixture
def assert_dependencies_are_up_to_date() -> None:
    """Verify that the dependencies are up to date.

    This fixture runs once per test session and runs poetry update --with dev
    to make sure the dependencies are up to date.
    """
    PyprojectConfigFile.update_dependencies(check=True)

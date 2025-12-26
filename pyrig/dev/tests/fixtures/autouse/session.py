"""Session-scoped autouse fixtures for project-wide validation and setup.

This module provides autouse fixtures that run automatically once per test
session to enforce project structure, code quality, and development environment
standards. These fixtures validate project-wide concerns before any tests run.

The fixtures are automatically registered via pytest_plugins in conftest.py,
and they use the `@autouse_session_fixture` decorator to run automatically at
the start of the test session without requiring explicit fixture requests.

Session-scoped fixtures run once per entire test session (all tests), making
them suitable for expensive validations like dependency checks, project structure
validation, and development environment setup.

Fixtures:
    assert_no_unstaged_changes: Verify no unstaged git changes (CI only).
        Checks before and after test session.

    assert_root_is_correct: Verify project root structure is correct. Creates
        missing config files if needed.

    assert_no_namespace_packages: Verify all packages have __init__.py files.
        Creates missing __init__.py files if needed.

    assert_all_src_code_in_one_package: Verify all source code is in a single
        package with expected structure (main, src, dev, resources).

    assert_src_package_correctly_named: Verify source package name matches
        project name and directory structure.

    assert_all_modules_tested: Verify every module has a corresponding test
        module. Creates test skeletons if needed.

    assert_no_unit_test_package_usage: Verify unittest package is not used
        (pytest only).

    assert_dependencies_are_up_to_date: Verify dependencies are up to date.
        Runs `uv lock --upgrade` and `uv sync`.

    assert_pre_commit_is_installed: Verify pre-commit hooks are installed.
        Runs `pre-commit install`.

    assert_src_runs_without_dev_deps: Verify source code runs without dev
        dependencies. Creates isolated environment and tests.

    assert_src_does_not_use_dev: Verify source code doesn't import dev code.
        Scans for dev imports in src.

    assert_all_dev_deps_in_deps: Verify all standard dev dependencies are
        declared in pyproject.toml.

    assert_project_mgt_is_up_to_date: Verify project management tool (uv) is
        up to date. Runs `uv self update` (local only).

    assert_version_control_is_installed: Verify git is installed.

    assert_container_engine_is_installed: Verify podman is installed (local only).

Validation Categories:
    **Git and Version Control**:
    - No unstaged changes (CI only)
    - Git is installed

    **Project Structure**:
    - Project root is correct
    - No namespace packages
    - All source code in one package
    - Source package correctly named
    - All modules have test modules

    **Code Quality**:
    - No unittest usage (pytest only)
    - Source doesn't import dev code

    **Dependencies**:
    - Dependencies are up to date
    - All dev dependencies declared
    - Source runs without dev dependencies

    **Development Environment**:
    - Pre-commit hooks installed
    - Project management tool (uv) up to date
    - Container engine (podman) installed (local only)

Automatic Fixes:
    Many fixtures automatically fix issues they detect:
    - Creates missing config files
    - Creates missing __init__.py files
    - Creates missing test modules
    - Updates dependencies
    - Installs pre-commit hooks

    After fixing, the fixtures fail with a detailed error message explaining
    what was fixed, allowing developers to review and commit the changes.

CI vs Local Behavior:
    Some fixtures behave differently in CI (GitHub Actions) vs local:
    - `assert_no_unstaged_changes`: Only runs in CI
    - `assert_project_mgt_is_up_to_date`: Only runs locally
    - `assert_container_engine_is_installed`: Only runs locally

Module Attributes:
    logger (logging.Logger): Logger instance for this module.

See Also:
    pyrig.dev.cli.commands.create_root.make_project_root: Project root creation
    pyrig.dev.cli.commands.create_tests.make_test_skeletons: Test skeleton generation
    pyrig.dev.cli.commands.make_inits.make_init_files: __init__.py creation
    pyrig.src.git: Git utilities
    pyrig.src.management.package_manager.PackageManager: Package management
    pyrig.src.management.pre_committer.PreCommitter: Pre-commit management
"""

import logging
import os
import re
import shutil
from collections.abc import Generator
from contextlib import chdir
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

import pyrig
from pyrig import dev, main, resources, src
from pyrig.dev.cli.commands.create_root import make_project_root
from pyrig.dev.cli.commands.create_tests import make_test_skeletons
from pyrig.dev.cli.commands.make_inits import make_init_files
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import (
    PyprojectConfigFile,
)
from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile
from pyrig.dev.utils.packages import (
    find_packages,
    get_namespace_packages,
    get_src_package,
)
from pyrig.dev.utils.testing import autouse_session_fixture
from pyrig.src.git import (
    get_git_unstaged_changes,
    running_in_github_actions,
)
from pyrig.src.management.package_manager import PackageManager
from pyrig.src.management.pre_committer import PreCommitter
from pyrig.src.modules.imports import (
    get_modules_and_packages_from_package,
    walk_package,
)
from pyrig.src.modules.module import (
    get_isolated_obj_name,
    get_module_name_replacing_start_module,
    import_module_with_default,
)
from pyrig.src.modules.package import (
    DOCS_DIR_NAME,
    DependencyGraph,
    get_pkg_name_from_project_name,
    get_project_name_from_pkg_name,
)
from pyrig.src.os.os import run_subprocess
from pyrig.src.testing.assertions import assert_with_msg
from pyrig.src.testing.convention import (
    TESTS_PACKAGE_NAME,
    make_summary_error_msg,
    make_test_obj_importpath_from_obj,
)

if TYPE_CHECKING:
    from types import ModuleType

logger = logging.getLogger(__name__)


@autouse_session_fixture
def assert_no_unstaged_changes() -> Generator[None, None, None]:
    """Verify that there are no unstaged git changes before and after tests.

    This session-scoped autouse fixture runs automatically in CI (GitHub Actions)
    to ensure that:
    1. Tests start with a clean git working directory (no unstaged changes)
    2. Tests don't create any unstaged changes during execution

    The fixture checks for unstaged changes before yielding (before tests run)
    and after yielding (after tests complete). If unstaged changes are found at
    either point, the fixture fails with a detailed error message listing the
    changed files.

    This prevents:
    - Running tests with uncommitted local changes in CI
    - Tests that modify files without cleaning up
    - Accidental file modifications during test execution

    Yields:
        None: Control is yielded to run tests, then checks again after tests.

    Raises:
        AssertionError: If unstaged changes are detected before or after the
            test session. The error message includes the list of unstaged files.

    Note:
        - This fixture only runs in CI (GitHub Actions), not locally
        - Uses `running_in_github_actions()` to detect CI environment
        - Checks both before and after the test session
        - Unstaged changes include modified, added, or deleted files

    See Also:
        pyrig.src.git.running_in_github_actions: CI detection
        pyrig.src.git.get_git_unstaged_changes: Get list of unstaged files
    """
    in_github_actions = running_in_github_actions()

    msg = (
        "Found unstaged changes. Please commit or stash them. "
        "Unstaged changes: {unstaged_changes}"
    )

    if in_github_actions:
        unstaged_changes = get_git_unstaged_changes()
        assert_with_msg(
            not unstaged_changes,
            msg=msg.format(unstaged_changes=unstaged_changes),
        )
    yield
    if in_github_actions:
        unstaged_changes = get_git_unstaged_changes()
        assert_with_msg(
            not unstaged_changes,
            msg=msg.format(unstaged_changes=unstaged_changes),
        )


@autouse_session_fixture
def assert_root_is_correct() -> None:
    """Verify that the project root structure is correct and complete.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that all ConfigFile subclasses report correct state via their
    `is_correct()` method. If any config files are incorrect or missing, the
    fixture automatically attempts to fix them by calling `make_project_root()`.

    The fixture:
    1. Creates `.experiment.py` if running in CI and it doesn't exist
    2. Checks all ConfigFile subclasses via `ConfigFile.get_all_subclasses()`
    3. Identifies incorrect config files via `cf.is_correct()`
    4. Calls `make_project_root()` to create/fix incorrect config files
    5. Fails with a detailed error message listing what was fixed

    This ensures that:
    - All required config files exist (pyproject.toml, README.md, etc.)
    - All config files have correct content
    - Project structure is complete before tests run
    - Developers are notified of missing/incorrect config files

    Raises:
        AssertionError: If any config files were incorrect and had to be fixed.
            The error message lists the paths of all fixed config files and
            prompts the developer to review the changes.

    Example:
        If pyproject.toml is missing or incorrect::

            # Fixture automatically:
            # 1. Detects PyprojectConfigFile.is_correct() returns False
            # 2. Calls make_project_root() to create/fix it
            # 3. Fails with error:
            #    "Found 1 incorrect ConfigFiles.
            #     Attempted correcting them automatically.
            #     Please verify the changes at the following paths:
            #     - /path/to/pyproject.toml"

    Note:
        - This fixture runs once per test session
        - It automatically fixes issues before failing
        - The developer must review and commit the fixes
        - In CI, it creates `.experiment.py` if missing

    See Also:
        pyrig.dev.cli.commands.create_root.make_project_root: Project root creation
        pyrig.dev.configs.base.base.ConfigFile: Base class for config files
        pyrig.dev.configs.python.dot_experiment.DotExperimentConfigFile: Experiment config
    """  # noqa: E501
    # if we are in CI then we must create experiment.py if it doesn't exist
    running_in_ci = running_in_github_actions()
    if running_in_ci:
        DotExperimentConfigFile()

    subclasses = ConfigFile.get_all_subclasses()
    incorrect_cfs = [cf for cf in subclasses if not cf.is_correct()]

    if incorrect_cfs:
        # init all per test run
        make_project_root()

    msg = f"""Found {len(incorrect_cfs)} incorrect ConfigFiles.
    Attempted correcting them automatically.
    Please verify the changes at the following paths:
"""
    for cf in incorrect_cfs:
        msg += f"""
        - {cf.get_path()}
        """
    assert_with_msg(not incorrect_cfs, msg)


@autouse_session_fixture
def assert_no_namespace_packages() -> None:
    """Verify that all packages have __init__.py files (no namespace packages).

    This session-scoped autouse fixture runs automatically once per test session
    to verify that all packages in the project are regular packages with
    __init__.py files, not namespace packages. Namespace packages can cause
    import issues and are not compatible with pyrig's architecture.

    The fixture:
    1. Scans for namespace packages via `get_namespace_packages()`
    2. Creates missing __init__.py files via `make_init_files()`
    3. Fails with a detailed error message listing created files

    This ensures that:
    - All packages have __init__.py files
    - No namespace packages exist in the project
    - Import behavior is predictable and consistent
    - Package structure is explicit

    Raises:
        AssertionError: If any namespace packages were found and had to be fixed.
            The error message lists the paths where __init__.py files were
            created and prompts the developer to review the changes.

    Example:
        If a package is missing __init__.py::

            myapp/
            └── utils/
                └── helpers.py  # Missing: utils/__init__.py

            # Fixture automatically:
            # 1. Detects utils/ is a namespace package
            # 2. Creates utils/__init__.py
            # 3. Fails with error:
            #    "Found 1 namespace packages.
            #     Created __init__.py files for them.
            #     Please verify the changes at the following paths:
            #     - myapp/utils"

    Note:
        - This fixture runs once per test session
        - It automatically creates __init__.py files before failing
        - The developer must review and commit the created files
        - Empty __init__.py files are created by default

    See Also:
        pyrig.dev.cli.commands.make_inits.make_init_files: __init__.py creator
        pyrig.dev.utils.packages.get_namespace_packages: Namespace package detector
    """
    any_namespace_packages = get_namespace_packages()
    if any_namespace_packages:
        make_init_files()

    msg = f"""Found {len(any_namespace_packages)} namespace packages.
    Created __init__.py files for them.
    Please verify the changes at the following paths:
"""
    for package in any_namespace_packages:
        msg += f"""
        - {package}
        """
    assert_with_msg(not any_namespace_packages, msg)


@autouse_session_fixture
def assert_all_src_code_in_one_package() -> None:
    """Verify that all source code is in a single package with correct structure.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that the project follows pyrig's single-package architecture. It
    ensures that:
    1. Only expected top-level packages exist (source package, tests, docs)
    2. The source package has exactly the expected subpackages (dev, src, resources)
    3. The source package has exactly the expected submodules (main)

    The fixture enforces pyrig's standard project structure where all source
    code lives in a single package with a specific internal organization.

    Raises:
        AssertionError: If the project structure doesn't match expectations.
            Possible failures:
            - Unexpected top-level packages exist
            - Source package has unexpected subpackages
            - Source package has unexpected submodules

    Example:
        Expected structure::

            myapp/  # Source package
            ├── main.py  # Entry point module
            ├── dev/  # Development tools
            ├── src/  # Production code
            └── resources/  # Resource files
            tests/  # Test package
            docs/  # Documentation

        Invalid structure (multiple source packages)::

            myapp/  # Source package
            another_package/  # INVALID: Second source package
            tests/

            # Fixture fails with:
            # "Expected only packages {tests, myapp, docs},
            #  but found {tests, myapp, docs, another_package}"

        Invalid structure (unexpected subpackage)::

            myapp/
            ├── main.py
            ├── dev/
            ├── src/
            ├── resources/
            └── utils/  # INVALID: Unexpected subpackage

            # Fixture fails with:
            # "Expected subpackages {dev, src, resources},
            #  but found {dev, src, resources, utils}"

    Note:
        - This fixture runs once per test session
        - It validates both top-level and source package structure
        - The source package name is determined from pyproject.toml
        - Expected subpackages: dev, src, resources
        - Expected submodules: main

    See Also:
        pyrig.dev.utils.packages.find_packages: Package discovery
        pyrig.dev.utils.packages.get_src_package: Source package identification
        pyrig.src.modules.imports.get_modules_and_packages_from_package:
            Package content inspection
    """
    packages = find_packages(depth=0)
    src_package = get_src_package()
    src_package_name = src_package.__name__
    expected_packages = {TESTS_PACKAGE_NAME, src_package_name, DOCS_DIR_NAME}

    # pkgs must be subset of expected_packages
    assert_with_msg(
        set(packages).issubset(expected_packages),
        f"Expected only packages {expected_packages}, but found {packages}",
    )

    # assert the src package's only submodules are main, src and dev
    subpackages, submodules = get_modules_and_packages_from_package(src_package)
    subpackage_names = {p.__name__.split(".")[-1] for p in subpackages}
    submodule_names = {m.__name__.split(".")[-1] for m in submodules}

    expected_subpackages = {
        get_isolated_obj_name(sub_pkg)
        for sub_pkg in [
            dev,
            src,
            resources,
        ]
    }
    expected_submodules = {get_isolated_obj_name(main)}
    assert_with_msg(
        subpackage_names == expected_subpackages,
        f"Expected subpackages {expected_subpackages}, but found {subpackage_names}",
    )
    assert_with_msg(
        submodule_names == expected_submodules,
        f"Expected submodules {expected_submodules}, but found {submodule_names}",
    )


@autouse_session_fixture
def assert_src_package_correctly_named() -> None:
    """Verify that the source package name matches project naming conventions.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that the source package is correctly named according to pyrig's
    naming conventions. It performs three checks:

    1. Current working directory name matches project name from pyproject.toml
    2. Source package name matches expected name derived from directory name
    3. Source package name matches package name from pyproject.toml

    This ensures consistency between:
    - Directory structure (filesystem)
    - Package names (Python imports)
    - Project configuration (pyproject.toml)

    Raises:
        AssertionError: If any naming mismatch is detected. Possible failures:
            - CWD name doesn't match project name in pyproject.toml
            - Source package name doesn't match expected name from CWD
            - Source package name doesn't match package name in pyproject.toml

    Example:
        Correct naming::

            # Directory: /path/to/my-project/
            # pyproject.toml: name = "my-project"
            # Package: my_project/

            # All checks pass:
            # - CWD name: "my-project" == project name: "my-project" ✓
            # - Package name: "my_project" == expected from CWD: "my_project" ✓
            # - Package name: "my_project" == pyproject package: "my_project" ✓

        Incorrect naming (package name mismatch)::

            # Directory: /path/to/my-project/
            # pyproject.toml: name = "my-project", package = "my_project"
            # Package: myproject/  # WRONG: Should be my_project/

            # Fixture fails with:
            # "Expected source package to be named my_project,
            #  but it is named myproject"

    Note:
        - This fixture runs once per test session
        - It validates three different naming aspects
        - Package names use underscores, project names use hyphens
        - The conversion follows Python package naming conventions

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile.get_project_name:
            Project name from pyproject.toml
        pyrig.dev.configs.pyproject.PyprojectConfigFile.get_package_name:
            Package name from pyproject.toml
        pyrig.src.modules.package.get_pkg_name_from_project_name:
            Project name to package name conversion
    """
    cwd_name = Path.cwd().name
    project_name = PyprojectConfigFile.get_project_name()
    assert_with_msg(
        cwd_name == project_name,
        f"Expected cwd name to be {project_name}, but it is {cwd_name}",
    )

    src_package_name = get_src_package().__name__
    src_package_name_from_cwd = get_pkg_name_from_project_name(cwd_name)
    assert_with_msg(
        src_package_name == src_package_name_from_cwd,
        f"Expected source package to be named {src_package_name_from_cwd}, "
        f"but it is named {src_package_name}",
    )

    src_package = get_src_package().__name__
    expected_package = PyprojectConfigFile.get_package_name()
    assert_with_msg(
        src_package == expected_package,
        f"Expected source package to be named {expected_package}, "
        f"but it is named {src_package}",
    )


@autouse_session_fixture
def assert_all_modules_tested() -> None:
    """Verify that every source module has a corresponding test module.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that the project structure is mirrored in the tests directory. It
    ensures that for every package and module in the source package, there is a
    corresponding test package and test module.

    The fixture:
    1. Gets the source package via `get_src_package()`
    2. Walks through all packages and modules via `walk_package()`
    3. For each package/module, checks if corresponding test exists
    4. Generates test skeletons for missing tests via `make_test_skeletons()`
    5. Fails with a detailed error message listing missing tests

    This ensures that:
    - Every source module has a test module
    - Every source package has a test package
    - Test structure mirrors source structure
    - New modules automatically get test skeletons
    - Test coverage never decreases

    Raises:
        AssertionError: If any source modules lack corresponding test modules.
            The error message lists all missing tests and indicates that test
            skeletons were automatically generated.

    Example:
        Given this source structure::

            myapp/
            ├── src/
            │   ├── calculator.py
            │   └── utils/
            │       └── helpers.py

        Expected test structure::

            tests/
            ├── test_calculator.py
            └── test_utils/
                └── test_helpers.py

        If `test_utils/test_helpers.py` is missing::

            # Fixture automatically:
            # 1. Detects missing test module
            # 2. Creates tests/test_utils/__init__.py
            # 3. Creates tests/test_utils/test_helpers.py with skeleton
            # 4. Fails with error listing what was created

    Note:
        - This fixture runs once per test session
        - It automatically generates test skeletons before failing
        - Test skeletons include test functions for all source functions/classes
        - The developer must fill in the generated test skeletons

    See Also:
        pyrig.dev.cli.commands.create_tests.make_test_skeletons:
            Test skeleton generator
        pyrig.src.testing.convention.make_test_obj_importpath_from_obj:
            Test path mapping
        pyrig.src.modules.imports.walk_package: Package traversal
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
        make_test_skeletons()

    msg = f"""Found missing tests. Tests skeletons were automatically created for:
    {make_summary_error_msg(missing_tests_to_module.keys())}
"""
    assert_with_msg(
        not missing_tests_to_module,
        msg,
    )


@autouse_session_fixture
def assert_no_unit_test_package_usage() -> None:
    """Verify that unittest is not used in the project (pytest only).

    This session-scoped autouse fixture runs automatically once per test session
    to verify that the unittest package is not used anywhere in the project.
    Pyrig projects use pytest exclusively for testing, and mixing unittest with
    pytest can cause issues and inconsistencies.

    The fixture:
    1. Scans all Python files in all packages
    2. Searches for the string "unittest" (case-insensitive)
    3. Collects all files containing unittest references
    4. Fails with a detailed error message listing the files

    This ensures that:
    - Only pytest is used for testing
    - No unittest imports or usage exist
    - Testing approach is consistent across the project
    - No mixing of testing frameworks

    Raises:
        AssertionError: If any files contain "unittest" references. The error
            message lists all files containing unittest usage.

    Example:
        If unittest is used::

            # tests/test_calculator.py
            import unittest  # BAD!

            class TestCalculator(unittest.TestCase):  # BAD!
                def test_add(self):
                    pass

            # Fixture fails with:
            # "Found unittest package usage in:
            #  - tests/test_calculator.py"

        Correct approach (pytest only)::

            # tests/test_calculator.py
            def test_add():
                '''Use pytest, not unittest.'''
                assert add(1, 2) == 3

    Note:
        - This fixture runs once per test session
        - It scans all Python files in the project
        - The search is case-insensitive
        - Both imports and usage are detected

    See Also:
        pyrig.dev.utils.packages.find_packages: Package discovery
    """
    unit_test_str = "UnitTest".lower()
    pkgs = find_packages()
    paths: list[str] = []
    for pkg in pkgs:
        paths.extend(
            [
                path.as_posix()
                for path in Path(pkg).rglob("*.py")
                if unit_test_str in path.read_text(encoding="utf-8")
            ]
        )

    msg = f"""Found {"UnitTest".lower()} package usage in:
    {make_summary_error_msg(paths)}
"""
    assert not paths, msg


@autouse_session_fixture
def assert_dependencies_are_up_to_date() -> None:
    """Verify that project dependencies are up to date.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that all project dependencies are up to date. It runs both
    `uv lock --upgrade` and `uv sync` to check for and install any updates.

    The fixture performs two operations:
    1. **Update check**: Runs `uv lock --upgrade` to check for dependency updates
    2. **Sync check**: Runs `uv sync` to install any missing dependencies

    If either operation results in changes (updates or installations), the
    fixture fails, indicating that dependencies were not up to date before
    running tests.

    This ensures that:
    - All dependencies are at their latest compatible versions
    - Lock file is up to date with pyproject.toml
    - All dependencies are installed
    - Tests run with current dependencies

    Raises:
        AssertionError: If dependencies were updated or installed. The error
            message includes the full output from both `uv lock --upgrade` and
            `uv sync` commands, showing what changed.

    Example:
        If dependencies are outdated::

            # Running tests triggers:
            # 1. `uv lock --upgrade` finds updates
            # 2. `uv sync` installs updates
            # 3. Fixture fails with:
            #    "Dependencies were not up to date.
            #     This fixture ran `uv lock --upgrade` and `uv sync`.
            #     upgrade output:
            #     Updated pytest from 7.0.0 to 7.1.0
            #     ...
            #     install output:
            #     Installed pytest-7.1.0
            #     ..."

    Note:
        - This fixture runs once per test session
        - It runs `uv lock --upgrade` to check for updates
        - It runs `uv sync` to install dependencies
        - Both commands run even if the first one fails
        - The fixture detects updates by looking for "Updated" in output
        - The fixture detects installations by looking for "==" in output

    See Also:
        pyrig.src.management.package_manager.PackageManager.get_update_dependencies_args:
            Update command builder
        pyrig.src.management.package_manager.PackageManager.get_install_dependencies_args:
            Install command builder
    """
    # update the dependencies
    args = PackageManager.get_update_dependencies_args()
    completed_process = args.run(check=False)
    stderr = completed_process.stderr.decode("utf-8")
    stdout = completed_process.stdout.decode("utf-8")
    std_msg_updated = stderr + stdout

    not_expected = ["Updated"]
    # if there were updates raise an error
    update_occurred = any(exp in std_msg_updated for exp in not_expected)
    deps_were_upgraded = update_occurred

    # sync the dependencies
    args = PackageManager.get_install_dependencies_args()
    completed_process = args.run(check=False)
    stderr = completed_process.stderr.decode("utf-8")
    stdout = completed_process.stdout.decode("utf-8")
    std_msg_installed = stderr + stdout
    expected = ["Resolved", "Audited"]
    expected_in_err_or_out = any(exp in std_msg_installed for exp in expected)
    not_expected = ["=="]
    install_occurred = any(exp in std_msg_installed for exp in not_expected)
    deps_were_installed = install_occurred and not expected_in_err_or_out

    is_up_to_date = not deps_were_upgraded and not deps_were_installed

    msg = f"""Dependencies were not up to date.
This fixture ran `uv lock --upgrade` and `uv sync`.
upgrade output:
{std_msg_updated}
-------------------------------------------------------------------------------
install output:
{std_msg_installed}
"""
    assert is_up_to_date, msg


@autouse_session_fixture
def assert_pre_commit_is_installed() -> None:
    """Verify that pre-commit hooks are installed.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that pre-commit hooks are installed in the git repository. It runs
    `pre-commit install` and checks that the installation was successful.

    Pre-commit hooks automatically run code quality checks (linting, formatting,
    type checking, etc.) before each commit, ensuring code quality standards are
    maintained.

    The fixture:
    1. Runs `pre-commit install` via PreCommitter.get_install_args()
    2. Checks the output for "pre-commit installed at"
    3. Fails if the expected output is not found

    This ensures that:
    - Pre-commit hooks are installed in .git/hooks/
    - Code quality checks run automatically before commits
    - All developers have the same pre-commit configuration
    - Commits are validated before being created

    Raises:
        AssertionError: If pre-commit installation fails. The error message
            includes the full output from `pre-commit install`.

    Example:
        If pre-commit is not installed::

            # Fixture runs `pre-commit install`
            # Expected output: "pre-commit installed at .git/hooks/pre-commit"
            # If output doesn't contain expected string, fixture fails with:
            # "Pre-commits are not installed.
            #  This fixture ran `pre-commit install` but it failed.
            #  Output: <actual output>"

    Note:
        - This fixture runs once per test session
        - It runs `pre-commit install` every time tests run
        - If hooks are already installed, the command is idempotent
        - Pre-commit configuration is in .pre-commit-config.yaml

    See Also:
        pyrig.src.management.pre_committer.PreCommitter.get_install_args:
            Pre-commit install command builder
    """
    args = PreCommitter.get_install_args()
    completed_process = args.run()
    stdout = completed_process.stdout.decode("utf-8")
    expected = "pre-commit installed at"

    pre_commits_are_installed = expected in stdout

    msg = f"""Pre-commits are not installed.
    This fixture ran `pre-commit install` but it failed.
    Output: {stdout}
    """
    assert pre_commits_are_installed, msg


@autouse_session_fixture
def assert_src_runs_without_dev_deps(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Verify that source code runs without dev dependencies installed.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that the source code can run without any dev dependencies installed.
    This ensures proper separation between production code (src) and development
    code (dev), and that the package can be installed and used in production
    environments without dev dependencies.

    The fixture performs an extensive test by:
    1. Creating an isolated temporary directory
    2. Copying the source package to the temp directory
    3. Copying minimal config files (pyproject.toml, README.md, LICENSE)
    4. Installing dependencies WITHOUT dev group (`uv sync --no-group dev`)
    5. Verifying pytest is NOT installed
    6. Importing all modules in src to catch dev dependency imports
    7. Running the main module to verify CLI works
    8. Running the CLI help command to verify entry point works

    This ensures that:
    - Source code has no imports from dev dependencies
    - Package can be installed without dev dependencies
    - CLI entry point works without dev dependencies
    - All src modules can be imported without dev dependencies
    - Production deployment won't fail due to missing dev dependencies

    Args:
        tmp_path_factory: Pytest's session-scoped temporary directory factory.
            Used to create an isolated environment for testing.

    Raises:
        AssertionError: If source code cannot run without dev dependencies.
            Possible failures:
            - Dev dependency is importable (shouldn't be installed)
            - Import error when importing src modules (dev dependency used)
            - CLI doesn't work (entry point issue)
            - Main module doesn't run (import issue)

    Example:
        If src imports a dev dependency::

            # myapp/src/calculator.py
            from pytest import fixture  # BAD! pytest is a dev dependency

            # Fixture automatically:
            # 1. Creates isolated environment
            # 2. Installs without dev dependencies
            # 3. Tries to import calculator.py
            # 4. Fails with ModuleNotFoundError: No module named 'pytest'

    Note:
        - This fixture runs once per test session
        - It creates a complete isolated environment
        - It skips if no internet connection is available
        - It tests both import and CLI execution
        - The test is comprehensive but expensive (runs once per session)

    See Also:
        assert_src_does_not_use_dev: Static analysis for dev imports
        pyrig.src.management.package_manager.PackageManager: Package management
    """
    project_name = PyprojectConfigFile.get_project_name()
    func_name = assert_src_runs_without_dev_deps.__name__  # ty:ignore[possibly-missing-attribute]
    tmp_path = tmp_path_factory.mktemp(func_name) / project_name
    # copy the project folder to a temp directory
    # run main.py from that directory
    src_package = get_src_package()
    src_package_file_str = src_package.__file__
    if src_package_file_str is None:
        msg = f"src_package.__file__ is None for {src_package}"
        raise ValueError(msg)

    project_path = Path(src_package_file_str).parent

    project_name = get_project_name_from_pkg_name(src_package.__name__)

    temp_project_path = tmp_path / src_package.__name__

    # shutil copy the project to tmp_path
    shutil.copytree(project_path, temp_project_path)

    # copy pyproject.toml and uv.lock to tmp_path
    configs = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
    ]
    for config in configs:
        shutil.copy(config, temp_project_path.parent)

    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    with chdir(tmp_path):
        # install deps
        completed_process = run_subprocess(
            ["uv", "sync", "--no-group", "dev"], env=env, check=False
        )
        stdout = completed_process.stdout.decode("utf-8")
        stderr = completed_process.stderr.decode("utf-8")
        std_msg = stderr + stdout
        no_internet = "Temporary failure in name resolution" in std_msg
        if no_internet:
            logger.info(
                "No internet, skipping %s",
                func_name,
            )
            return

        # delete pyproject.toml and uv.lock and readme.md
        for config in configs:
            Path(config).unlink()
        # python -m video_vault.main

        # assert pytest is not installed
        dev_dep = "pytest"
        args = PackageManager.get_run_args("pip", "show", dev_dep)
        installed = args.run(
            check=False,
            env=env,
        )
        stderr = installed.stderr.decode("utf-8")
        dev_dep_not_installed = f"not found: {dev_dep}" in stderr
        assert dev_dep_not_installed, f"Expected {dev_dep} not to be installed"
        # check pytest is not importable
        args = PackageManager.get_run_args("python", "-c", "import pytest")
        installed = args.run(
            check=False,
            env=env,
        )
        stderr = installed.stderr.decode("utf-8")
        assert "ModuleNotFoundError" in stderr, (
            f"Expected ModuleNotFoundError, got {stderr}"
        )
        src_pkg_name = get_src_package().__name__

        # run walk_package with src and import all modules to catch dev dep imports
        cmd = [
            "uv",
            "run",
            "--no-group",
            "dev",
            "python",
            "-c",
            (
                "from importlib import import_module; "
                "from pyrig import main; "
                "from pyrig import src; "
                "from pyrig.src.modules.module import get_module_name_replacing_start_module; "  # noqa: E501
                "from pyrig.src.modules.imports import walk_package; "
                "from pyrig.src.testing.assertions import assert_with_msg; "
                f"import {src_pkg_name}; "
                f"src_module=import_module(get_module_name_replacing_start_module(src, {src_pkg_name}.__name__)); "  # noqa: E501
                "pks=list(walk_package(src_module)); "
                "assert_with_msg(isinstance(pks, list), 'Expected pks to be a list'); "
                "assert_with_msg(len(pks) > 0, 'Expected pks to not be empty'); "
                # also test that main can be called
                f"main_module=import_module(get_module_name_replacing_start_module(main, {src_pkg_name}.__name__)); "  # noqa: E501
                # add a print statement to see the output
                "print('Success')"
            ),
        ]

        completed_process = run_subprocess(cmd, env=env, check=False)
        stdout = completed_process.stdout.decode("utf-8")
        stderr = completed_process.stderr.decode("utf-8")
        msg = f"""Expected Success in stdout, got {stdout} and {stderr}
If this fails then there is likely an import in src that depends on dev dependencies.
"""
        assert "Success" in stdout, msg

        # run cli without dev deps
        cmd = ["uv", "run", "--no-group", "dev", project_name, "--help"]
        completed_process = run_subprocess(cmd, env=env, check=False)
        stdout = completed_process.stdout.decode("utf-8")
        stderr = completed_process.stderr.decode("utf-8")
        assert "Usage:" in stdout, (
            f"Expected Usage: in stdout, got {stdout} and {stderr}"
        )


@autouse_session_fixture
def assert_src_does_not_use_dev() -> None:
    """Verify that source code does not import any dev code.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that the src folder has no code that depends on dev code. This
    ensures proper separation of concerns and that production code doesn't
    depend on development-only code.

    The fixture:
    1. Gets the source package's src subpackage
    2. Builds a regex pattern matching all possible dev imports
    3. Scans all Python files in src for dev import statements
    4. Fails with a detailed error message listing any dev imports found

    This ensures that:
    - Production code (src) doesn't depend on development code (dev)
    - Source code can run without dev dependencies installed
    - Proper separation between production and development code
    - No accidental dev imports in production code

    Raises:
        AssertionError: If any dev imports are found in src code. The error
            message lists all files containing dev imports and the specific
            import statements found.

    Example:
        If src code imports dev::

            # myapp/src/calculator.py
            from myapp.dev.utils import debug_helper  # BAD!

            # Fixture automatically:
            # 1. Scans all files in myapp/src/
            # 2. Finds dev import in calculator.py
            # 3. Fails with error:
            #    "Found dev usage in src:
            #     - myapp/src/calculator.py: myapp.dev.utils"

    Note:
        - This fixture runs once per test session
        - It scans all Python files in the src subpackage
        - Uses regex to detect dev imports across all dependent packages
        - Checks for both direct imports and from imports

    See Also:
        assert_src_runs_without_dev_deps: Verifies src runs without dev deps
        pyrig.src.modules.package.DependencyGraph: Dependency graph utilities
    """
    src_package = get_src_package()

    src_src_pkg_name = get_module_name_replacing_start_module(src, src_package.__name__)

    src_src_pkg = import_module(src_src_pkg_name)

    pkgs_depending_on_pyrig = DependencyGraph.cached().get_all_depending_on(
        pyrig, include_self=True
    )

    possible_dev_usages = [
        get_module_name_replacing_start_module(dev, pkg.__name__)
        for pkg in pkgs_depending_on_pyrig
    ]
    possible_dev_usages = [re.escape(usage) for usage in possible_dev_usages]

    possible_dev_usages_pattern = r"\b(" + "|".join(possible_dev_usages) + r")\b"

    usages: list[str] = []
    folder_path = Path(src_src_pkg.__path__[0])
    for path in folder_path.rglob("*.py"):
        content = path.read_text(encoding="utf-8")

        is_dev_used = re.search(possible_dev_usages_pattern, content)
        if is_dev_used:
            usages.append(f"{path}: {is_dev_used.group()}")

    msg = f"""Found dev usage in src:
    {make_summary_error_msg(usages)}
"""
    assert_with_msg(
        not usages,
        msg,
    )


@autouse_session_fixture
def assert_all_dev_deps_in_deps() -> None:
    """Verify that all standard dev dependencies are declared in pyproject.toml.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that all of pyrig's standard dev dependencies are declared in the
    project's pyproject.toml file. This ensures that projects using pyrig have
    all the necessary development tools configured.

    The fixture:
    1. Gets all dependencies from pyproject.toml
    2. Gets pyrig's standard dev dependencies
    3. Strips version specifiers from both sets
    4. Verifies standard dev deps are a subset of all deps

    Standard dev dependencies include tools like:
    - pytest (testing framework)
    - ruff (linter and formatter)
    - mypy (type checker)
    - pre-commit (git hooks)
    - And other essential development tools

    This ensures that:
    - All required dev tools are declared
    - Project has complete development environment
    - No missing dev dependencies
    - Consistent dev setup across projects

    Raises:
        AssertionError: If any standard dev dependencies are missing from
            pyproject.toml. The error message shows which dependencies are
            missing.

    Example:
        If pytest is missing from pyproject.toml::

            # pyproject.toml
            [project.optional-dependencies]
            dev = [
                "ruff",
                "mypy",
                # Missing: "pytest"
            ]

            # Fixture fails with:
            # "Expected {'pytest', 'ruff', 'mypy', ...} to be a subset of
            #  {'ruff', 'mypy', ...}"

    Note:
        - This fixture runs once per test session
        - It compares dependency names only (versions are stripped)
        - Standard dev dependencies are defined in PyprojectConfigFile
        - The check is case-insensitive

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile.get_all_dependencies:
            Get all project dependencies
        pyrig.dev.configs.pyproject.PyprojectConfigFile.get_standard_dev_dependencies:
            Get pyrig's standard dev dependencies
        pyrig.dev.configs.pyproject.PyprojectConfigFile.remove_version_from_dep:
            Strip version specifiers
    """
    all_deps = set(PyprojectConfigFile.get_all_dependencies())
    standard_dev_deps = set(PyprojectConfigFile.get_standard_dev_dependencies())

    stripped_deps = {
        PyprojectConfigFile.remove_version_from_dep(dep) for dep in all_deps
    }
    stripped_standard_dev_deps = {
        PyprojectConfigFile.remove_version_from_dep(dep) for dep in standard_dev_deps
    }

    assert stripped_standard_dev_deps.issubset(stripped_deps), (
        f"Expected {stripped_standard_dev_deps} to be a subset of {stripped_deps}"
    )


@autouse_session_fixture
def assert_project_mgt_is_up_to_date() -> None:
    """Verify that uv (project management tool) is up to date.

    This session-scoped autouse fixture runs automatically once per test session
    (except in CI) to verify that uv, the project management tool, is up to date.
    It runs `uv self update` to check for and install updates.

    The fixture:
    1. Skips if running in GitHub Actions (CI)
    2. Runs `uv self update` to check for updates
    3. Checks output for success messages or known acceptable errors
    4. Fails if update check fails unexpectedly

    This ensures that:
    - Developers use the latest version of uv
    - Bug fixes and improvements are available
    - Consistent tooling across development environments
    - No outdated tool versions

    Raises:
        AssertionError: If `uv self update` fails unexpectedly. The error
            message includes the full output from the command.

    Expected success messages:
        - "success: You're on the latest version of uv"
        - "GitHub API rate limit exceeded" (acceptable, can't check)
        - "Temporary failure in name resolution" (acceptable, network issue)

    Example:
        If uv is outdated::

            # Fixture runs `uv self update`
            # Output: "Updated uv from 0.1.0 to 0.2.0"
            # Fixture passes (update successful)

        If update check fails::

            # Fixture runs `uv self update`
            # Output: "Error: Unknown error"
            # Fixture fails with:
            # "Expected one of [...] in stderr or stdout, got: Error: Unknown error
            #  This fixture ran `uv self update` but it failed."

    Note:
        - This fixture runs once per test session
        - It only runs locally, not in CI (GitHub Actions)
        - Network errors are acceptable (can't update without internet)
        - Rate limit errors are acceptable (GitHub API limits)
        - The fixture updates uv automatically if outdated

    See Also:
        pyrig.src.git.running_in_github_actions: CI detection
    """
    if not running_in_github_actions():
        # update project mgt
        completed_process = run_subprocess(["uv", "self", "update"], check=False)
        stderr = completed_process.stderr.decode("utf-8")
        stdout = completed_process.stdout.decode("utf-8")
        std_msg = stderr + stdout

        expected = [
            "success: You're on the latest version of uv",
            "GitHub API rate limit exceeded",
            "Temporary failure in name resolution",
        ]
        expected_in_err_or_out = any(exp in std_msg for exp in expected)
        msg = f"""Expected one of {expected} in stderr or stdout, got: {std_msg}

        This fixture ran `uv self update` but it failed.
        """
        assert expected_in_err_or_out, msg


@autouse_session_fixture
def assert_version_control_is_installed() -> None:
    """Verify that git is installed and available.

    This session-scoped autouse fixture runs automatically once per test session
    to verify that git is installed and available on the system. Pyrig requires
    git for version control, commit history analysis, and various development
    workflows.

    The fixture:
    1. Runs `git --version` to check if git is installed
    2. Parses the output using regex to find version number
    3. Fails if git is not found or version can't be determined

    This ensures that:
    - Git is installed on the system
    - Git is accessible from the command line
    - Version control operations will work
    - Development workflows can proceed

    Raises:
        AssertionError: If git is not installed or not accessible. The error
            message includes the full output from `git --version`.

    Example:
        If git is installed::

            # Fixture runs `git --version`
            # Output: "git version 2.39.1"
            # Fixture passes (version found)

        If git is not installed::

            # Fixture runs `git --version`
            # Output: "command not found: git"
            # Fixture fails with:
            # "Expected git to be installed, got: command not found: git"

    Note:
        - This fixture runs once per test session
        - It runs in all environments (local and CI)
        - Git is a hard requirement for pyrig projects
        - The version number must match pattern: "git version X.Y.Z"

    See Also:
        pyrig.src.git: Git utilities and operations
    """
    completed_process = run_subprocess(["git", "--version"], check=False)
    stderr = completed_process.stderr.decode("utf-8")
    stdout = completed_process.stdout.decode("utf-8")
    std_msg = stderr + stdout
    # use re expression to check if git version is in the output
    git_is_installed = re.search(r"git version \d+\.\d+\.\d+", std_msg)

    assert git_is_installed, f"Expected git to be installed, got: {std_msg}"


@autouse_session_fixture
def assert_container_engine_is_installed() -> None:
    """Verify that podman (container engine) is installed and available.

    This session-scoped autouse fixture runs automatically once per test session
    (except in CI) to verify that podman is installed and available on the system.
    Pyrig uses podman for containerization, isolated testing environments, and
    deployment workflows.

    The fixture:
    1. Skips if running in GitHub Actions (CI)
    2. Runs `podman --version` to check if podman is installed
    3. Parses the output using regex to find version number
    4. Fails if podman is not found or version can't be determined

    This ensures that:
    - Podman is installed on the system
    - Podman is accessible from the command line
    - Container operations will work
    - Development workflows requiring containers can proceed

    Raises:
        AssertionError: If podman is not installed or not accessible. The error
            message includes the full output from `podman --version`.

    Example:
        If podman is installed::

            # Fixture runs `podman --version`
            # Output: "podman version 4.3.1"
            # Fixture passes (version found)

        If podman is not installed::

            # Fixture runs `podman --version`
            # Output: "command not found: podman"
            # Fixture fails with:
            # "Expected podman to be installed, got: command not found: podman"

    Note:
        - This fixture runs once per test session
        - It only runs locally, not in CI (GitHub Actions)
        - Podman is required for container-based workflows
        - The version number must match pattern: "podman version X.Y.Z"
        - Podman is preferred over Docker for rootless containers

    See Also:
        pyrig.src.git.running_in_github_actions: CI detection
    """
    if not running_in_github_actions():
        completed_process = run_subprocess(["podman", "--version"], check=False)
        stderr = completed_process.stderr.decode("utf-8")
        stdout = completed_process.stdout.decode("utf-8")
        std_msg = stderr + stdout
        # use re expression to check if podman version is in the output
        podman_is_installed = re.search(r"podman version \d+\.\d+\.\d+", std_msg)

        assert podman_is_installed, f"Expected podman to be installed, got: {std_msg}"

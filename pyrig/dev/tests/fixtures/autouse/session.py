"""Session-scoped autouse fixtures for project-wide validation and setup.

Provides autouse fixtures that run once per test session to enforce project
structure, code quality, and development environment standards. Many fixtures
auto-fix issues (creating missing files, updating dependencies) then fail with
a message for developer review.

Fixtures:
    assert_no_unstaged_changes: No unstaged git changes (CI only).
    assert_root_is_correct: Project root structure, auto-creates config files.
    assert_no_namespace_packages: All packages have __init__.py.
    assert_all_src_code_in_one_package: Single source package with expected structure.
    assert_src_package_correctly_named: Package name matches project name.
    assert_all_modules_tested: All modules have test modules, auto-generates skeletons.
    assert_no_unit_test_package_usage: No unittest usage (pytest only).
    assert_dependencies_are_up_to_date: Dependencies current via uv lock/sync.
    assert_src_runs_without_dev_deps: Source runs without dev dependencies.
    assert_src_does_not_use_dev: Source doesn't import dev code.
    assert_project_mgt_is_up_to_date: uv up to date (local only).
"""

import logging
import os
import re
import shutil
from collections.abc import Generator
from contextlib import chdir
from importlib import import_module
from pathlib import Path

import pytest

import pyrig
from pyrig import dev, main, resources, src
from pyrig.dev.cli.commands.make_inits import make_init_files
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.dot_env import DotEnvConfigFile
from pyrig.dev.configs.pyproject import (
    PyprojectConfigFile,
)
from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile
from pyrig.dev.management.package_manager import PackageManager
from pyrig.dev.management.version_controller import VersionController
from pyrig.dev.tests.mirror_test import MirrorTestConfigFile
from pyrig.dev.utils.packages import (
    find_packages,
    get_namespace_packages,
)
from pyrig.dev.utils.testing import autouse_session_fixture
from pyrig.src.git import (
    running_in_github_actions,
)
from pyrig.src.modules.imports import (
    get_modules_and_packages_from_package,
    walk_package,
)
from pyrig.src.modules.module import (
    get_isolated_obj_name,
    get_module_name_replacing_start_module,
)
from pyrig.src.modules.package import (
    DependencyGraph,
    get_pkg_name_from_project_name,
    get_project_name_from_pkg_name,
)
from pyrig.src.modules.path import ModulePath
from pyrig.src.requests import internet_is_available
from pyrig.src.string_ import make_summary_error_msg, re_search_excluding_docstrings

logger = logging.getLogger(__name__)


@autouse_session_fixture
def assert_no_unstaged_changes() -> Generator[None, None, None]:
    """Verify no unstaged git changes before and after tests (CI only).

    Yields:
        None: Control yielded to run tests, then checks again after.

    Raises:
        AssertionError: If unstaged changes detected in CI.
    """
    in_github_actions = running_in_github_actions()

    msg = """Pyrig enforces that no changes are made during tests when running in CI.
    This is to ensure that the tests do not modify any files.
    Found the following unstaged changes:
    {unstaged_changes}
    """

    if in_github_actions:
        unstaged_changes = VersionController.L.has_unstaged_diff()
        assert not unstaged_changes, msg.format(
            unstaged_changes=VersionController.L.get_diff()
        )
    yield
    if in_github_actions:
        unstaged_changes = VersionController.L.has_unstaged_diff()
        assert not unstaged_changes, msg.format(
            unstaged_changes=VersionController.L.get_diff()
        )


@autouse_session_fixture
def assert_root_is_correct() -> None:
    """Verify project root structure is correct, auto-fixing incorrect config files.

    Raises:
        AssertionError: If config files were incorrect (lists fixed paths).
    """
    # if we are in CI then we must create config files that are gitignored
    # as they are not pushed to the repository
    running_in_ci = running_in_github_actions()
    if running_in_ci:
        DotExperimentConfigFile()
        DotEnvConfigFile()

    subclasses = ConfigFile.get_all_subclasses()
    incorrect_cfs = [cf for cf in subclasses if not cf.is_correct()]

    if incorrect_cfs:
        # init all per test run
        ConfigFile.init_subclasses(*incorrect_cfs)

    msg = f"""Found {len(incorrect_cfs)} incorrect ConfigFiles.
    Attempted correcting them automatically.
    Please verify the changes at the following paths:
"""
    for cf in incorrect_cfs:
        msg += f"""
        - {cf.get_path()}
        """
    assert not incorrect_cfs, msg


@autouse_session_fixture
def assert_no_namespace_packages() -> None:
    """Verify all packages have __init__.py, auto-creating missing ones.

    Raises:
        AssertionError: If namespace packages were found (lists created paths).
    """
    any_namespace_packages = get_namespace_packages()
    if any_namespace_packages:
        make_init_files()

    msg = f"""Pyrig enforces that all packages have __init__.py files.
    Found {len(any_namespace_packages)} namespace packages.
    Created __init__.py files for them.
    Please verify the changes at the following paths:
"""
    for package in any_namespace_packages:
        msg += f"""
        - {package}
        """
    assert not any_namespace_packages, msg


@autouse_session_fixture
def assert_all_src_code_in_one_package() -> None:
    """Verify source code is in a single package with expected structure.

    Checks that only expected top-level packages exist (source and tests)
    and source package has exactly dev, src, resources subpackages and main module.

    Raises:
        AssertionError: If unexpected packages/subpackages/submodules found.
    """
    packages = find_packages(depth=0)
    src_package = import_module(PyprojectConfigFile.L.get_package_name())
    src_package_name = src_package.__name__
    expected_packages = {
        MirrorTestConfigFile.L.get_tests_package_name(),
        src_package_name,
    }

    # pkgs must be exactly the expected packages
    assert (
        set(packages) == expected_packages
    ), f"""Pyrig enforces a single source package with a specific structure.
    Found unexpected packages: {set(packages) - expected_packages}
    Expected packages: {expected_packages}
    Only folders with __init__.py files are considered packages.
    Please move all code and login into the designated src package.
"""

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
    assert (
        subpackage_names == expected_subpackages
    ), f"""Pyrig enforces a single source package with a specific structure.
        Found unexpected subpackages: {subpackage_names - expected_subpackages}
        Expected subpackages: {expected_subpackages}
        Please move all code and login into the designated src package.
    """

    assert (
        submodule_names == expected_submodules
    ), f"""Pyrig enforces a single source package with a specific structure.
        Found unexpected submodules: {submodule_names - expected_submodules}
        Expected submodules: {expected_submodules}
        Please move all code and login into the designated src package.
        """


@autouse_session_fixture
def assert_src_package_correctly_named() -> None:
    """Verify source package name matches project naming conventions.

    Checks CWD name matches pyproject.toml project name and package name.

    Raises:
        AssertionError: If any naming mismatch detected.
    """
    cwd_name = Path.cwd().name
    project_name = PyprojectConfigFile.L.get_project_name()
    assert cwd_name == project_name, (
        f"Expected cwd name to be {project_name}, but it is {cwd_name}"
    )

    src_package = import_module(PyprojectConfigFile.L.get_package_name())

    src_package_name = src_package.__name__
    src_package_name_from_cwd = get_pkg_name_from_project_name(cwd_name)
    msg = (
        f"Expected source package to be named {src_package_name_from_cwd}, "
        f"but it is named {src_package_name}"
    )
    assert src_package_name == src_package_name_from_cwd, msg

    src_package = src_package.__name__
    expected_package = PyprojectConfigFile.L.get_package_name()
    msg = (
        f"Expected source package to be named {expected_package}, "
        f"but it is named {src_package}"
    )
    assert src_package == expected_package, msg


@autouse_session_fixture
def assert_all_modules_tested() -> None:
    """Verify every source module has a corresponding test module.

    Auto-generates test skeletons for missing test modules/packages.

    Raises:
        AssertionError: If any source modules lack corresponding tests.
    """
    src_package = import_module(PyprojectConfigFile.L.get_package_name())

    # we will now go through all the modules in the src package and check
    # that there is a corresponding test module
    all_modules = []
    for _, modules in walk_package(src_package):
        all_modules.extend(modules)

    mirror_test_cls = MirrorTestConfigFile.L
    subclasses = mirror_test_cls.make_subclasses_for_modules(all_modules)
    incorrect_subclasses = [sc for sc in subclasses if not sc.is_correct()]

    if incorrect_subclasses:
        mirror_test_cls.init_subclasses(*incorrect_subclasses)

    msg = f"""Found incorrect test modules.
    Test skeletons were automatically created for:
    {make_summary_error_msg([sc.get_path().as_posix() for sc in incorrect_subclasses])}
"""
    assert not incorrect_subclasses, msg


@autouse_session_fixture
def assert_no_unit_test_package_usage() -> None:
    """Verify unittest is not used in the project (pytest only).

    Raises:
        AssertionError: If any files contain unittest references.
    """
    unit_test_str = "UnitTest".lower()
    unit_test_pattern = re.compile(unit_test_str)
    pkgs = find_packages()
    usages: list[str] = []
    for pkg in pkgs:
        pkg_path = ModulePath.pkg_name_to_relative_dir_path(pkg)
        for path in pkg_path.rglob("*.py"):
            content = path.read_text(encoding="utf-8")
            is_unit_test_used = re_search_excluding_docstrings(
                unit_test_pattern, content
            )
            if is_unit_test_used:
                usages.append(f"{path}: {is_unit_test_used.group()}")

    msg = f"""Found {unit_test_str} package usage in:
    {make_summary_error_msg(usages)}
"""
    assert not usages, msg


@autouse_session_fixture
def assert_dependencies_are_up_to_date() -> None:
    """Verify dependencies are up to date via ``uv lock --upgrade`` and ``uv sync``.

    Skipped if no internet connection is available.

    Raises:
        AssertionError: If dependency update or sync commands fail.
    """
    if not internet_is_available():
        logger.warning(
            "No internet, skipping %s",
            assert_dependencies_are_up_to_date.__name__,  # ty:ignore[possibly-missing-attribute]
        )
        return
    # update the dependencies
    args = PackageManager.L.get_update_dependencies_args()
    completed_process = args.run(check=False)
    stderr = completed_process.stderr
    stdout = completed_process.stdout
    std_msg_updated = stderr + stdout
    deps_updated_successfully = completed_process.returncode == 0
    msg_updated = (
        f"Dependencies were updated successfully by `{args}`."
        if deps_updated_successfully
        else f"""Failed to update dependencies.
    This fixture ran `{args}` but it failed.
    Output:
    {std_msg_updated}
    """
    )

    # sync the dependencies
    args = PackageManager.L.get_install_dependencies_args()
    completed_process = args.run(check=False)
    stderr = completed_process.stderr
    stdout = completed_process.stdout
    std_msg_installed = stderr + stdout
    deps_installed_successfully = completed_process.returncode == 0
    msg_installed = (
        f"Dependencies were installed successfully by `{args}`."
        if deps_installed_successfully
        else f"""Failed to install dependencies.
    This fixture ran `{args}` but it failed.
    Output:
    {std_msg_installed}
    """
    )

    successful = deps_updated_successfully and deps_installed_successfully

    msg = f"""Dependencies are not up to date.
    {msg_updated}
    --------------------------------------------------------------------------------
    {msg_installed}
    """
    assert successful, msg


@autouse_session_fixture
def assert_src_runs_without_dev_deps(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Verify source code runs in isolated environment without dev dependencies.

    Creates temp environment, installs without dev group, imports all src modules,
    and runs CLI to catch any dev dependency usage.

    Args:
        tmp_path_factory: Session-scoped temp directory factory.

    Raises:
        AssertionError: If source code cannot run without dev dependencies.
    """
    base_msg = """Source code cannot run without dev dependencies.
    This fixture created a temp environment and installed the project without
    the dev group and attempted to import all src modules.
    However, it failed with the following error:
    """
    if not internet_is_available():
        logger.warning(
            "No internet, skipping %s",
            assert_src_runs_without_dev_deps.__name__,  # ty:ignore[possibly-missing-attribute]
        )
        return
    project_name = PyprojectConfigFile.L.get_project_name()
    func_name = assert_src_runs_without_dev_deps.__name__  # ty:ignore[possibly-missing-attribute]
    tmp_path = tmp_path_factory.mktemp(func_name) / project_name
    # copy the project folder to a temp directory
    # run main.py from that directory
    src_package = import_module(PyprojectConfigFile.L.get_package_name())
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

    # pop the venv from the environment
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    with chdir(tmp_path):
        # install deps
        completed_process = PackageManager.L.get_install_dependencies_no_dev_args().run(
            check=False,
            env=env,
        )
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        std_msg = stderr + stdout

        dev_dep = PyprojectConfigFile.L.get_standard_dev_dependencies()[0]
        assert dev_dep not in std_msg, base_msg + f"{std_msg}"

        # delete pyproject.toml and uv.lock and readme.md
        for config in configs:
            Path(config).unlink()

        # run walk_package with src and import all modules to catch dev dep imports
        src_pkg_name = PyprojectConfigFile.L.get_package_name()
        script_args = [
            "python",
            "-c",
            "; ".join(
                (
                    "from pyrig.src.modules.imports import walk_package",
                    f"from {src_pkg_name} import main",
                    f"from {src_pkg_name} import src",
                    "packages=list(walk_package(src))",
                    # verify packages is a list
                    "assert isinstance(packages, list)",
                    # verify packages is not empty
                    "assert len(packages) > 0",
                    # also test that main can be called
                    "assert callable(main.main)",
                    # add a print statement to see the output
                    "print('Success')",
                )
            ),
        ]
        args = PackageManager.L.get_run_no_dev_args(*script_args)

        completed_process = args.run(
            check=False,
            env=env,
        )
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        msg = f"""Expected Success in stdout, got {stdout} and {stderr}
If this fails then there is likely an import in src that depends on dev dependencies.
"""
        assert "Success" in stdout, base_msg + msg

        # run cli without dev deps
        args = PackageManager.L.get_run_no_dev_args(project_name, "--help")
        completed_process = args.run(
            check=False,
        )
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        std_msg = stderr + stdout
        successful = completed_process.returncode == 0
        assert successful, base_msg + f"Expected {args} to succeed, got {std_msg}"


@autouse_session_fixture
def assert_src_does_not_use_dev() -> None:
    """Verify source code does not import any dev code.

    Scans src subpackage for dev import statements to ensure production/dev
    separation.

    Raises:
        AssertionError: If any dev imports found in src code.
    """
    src_package = import_module(PyprojectConfigFile.L.get_package_name())

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

        is_dev_used = re_search_excluding_docstrings(
            possible_dev_usages_pattern, content
        )
        if is_dev_used:
            usages.append(f"{path}: {is_dev_used.group()}")

    msg = f"""Found dev usage in src:
    {make_summary_error_msg(usages)}
"""
    assert not usages, msg


@autouse_session_fixture
def assert_project_mgt_is_up_to_date() -> None:
    """Verify uv is up to date via ``uv self update`` (skipped in CI).

    Raises:
        AssertionError: If ``uv self update`` fails unexpectedly.
    """
    if not internet_is_available():
        logger.warning(
            "No internet, skipping %s",
            assert_project_mgt_is_up_to_date.__name__,  # ty:ignore[possibly-missing-attribute]
        )
        return
    if not running_in_github_actions():
        # update project mgt
        completed_process = PackageManager.L.get_update_self_args().run(check=False)
        returncode = completed_process.returncode

        stderr = completed_process.stderr
        stdout = completed_process.stdout
        std_msg = stderr + stdout

        allowed_errors = [
            "GitHub API rate limit exceeded",
        ]

        allowed_error_in_err_or_out = any(exp in std_msg for exp in allowed_errors)

        is_up_to_date = returncode == 0 or allowed_error_in_err_or_out

        msg = f"""The tool {PackageManager.L.name()} is not up to date.
        This fixture ran `{PackageManager.L.get_update_self_args()}` but it failed.
        Output: {std_msg}
        """
        assert is_up_to_date, msg

"""Session-scoped autouse fixtures for project-wide validation and setup.

Provides autouse fixtures that run once per test session to enforce project
structure, code quality, and development environment standards. Many fixtures
auto-fix issues (creating missing files, updating dependencies) then fail with
a message for developer review.
"""

import logging
import os
import shutil
from collections.abc import Generator
from contextlib import chdir
from importlib import import_module
from pathlib import Path

import pytest

from pyrig.rig.cli.commands.make_inits import make_init_files
from pyrig.rig.configs.base.base import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.base.base import Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.packages import (
    find_namespace_packages,
)
from pyrig.rig.utils.version_control import ignored_config_files
from pyrig.src.git import (
    running_in_github_actions,
)
from pyrig.src.iterate import generator_has_items
from pyrig.src.modules.imports import (
    walk_package,
)
from pyrig.src.requests import internet_is_available
from pyrig.src.string_ import (
    make_summary_error_msg,
    snake_to_kebab_case,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
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
        unstaged_changes = VersionController.I.has_unstaged_diff()
        assert not unstaged_changes, msg.format(
            unstaged_changes=VersionController.I.diff()
        )
    yield
    if in_github_actions:
        unstaged_changes = VersionController.I.has_unstaged_diff()
        assert not unstaged_changes, msg.format(
            unstaged_changes=VersionController.I.diff()
        )


@pytest.fixture(scope="session", autouse=True)
def assert_root_is_correct() -> None:
    """Verify project root structure is correct, auto-fixing incorrect config files.

    Raises:
        AssertionError: If config files were incorrect (lists fixed paths).
    """
    # if we are in CI then we must create config files that are gitignored
    # as they are not pushed to the repository
    running_in_ci = running_in_github_actions()
    if running_in_ci:
        tuple(cf.validate() for cf in ignored_config_files())

    subclasses = ConfigFile.subclasses()
    incorrect_cfs = tuple(cf for cf in subclasses if not cf().is_correct())

    if incorrect_cfs:
        # init all per test run
        ConfigFile.validate_subclasses(incorrect_cfs)

    msg = f"""Found incorrect ConfigFiles.
Attempted correcting them automatically.
Please verify the changes at the following paths.
{make_summary_error_msg(cf().path().as_posix() for cf in incorrect_cfs)}
"""
    assert not incorrect_cfs, msg


@pytest.fixture(scope="session", autouse=True)
def assert_no_namespace_packages() -> None:
    """Verify all packages have __init__.py, auto-creating missing ones.

    Raises:
        AssertionError: If namespace packages were found (lists created paths).
    """
    namespace_packages = find_namespace_packages()
    has_namespace_packages, namespace_packages = generator_has_items(namespace_packages)
    if has_namespace_packages:
        make_init_files()

    msg = f"""Pyrig enforces that all packages have __init__.py files.
Found namespace packages.
Created __init__.py files for them.
Please verify the changes at the following paths:
{make_summary_error_msg(namespace_packages)}
"""
    assert not has_namespace_packages, msg


@pytest.fixture(scope="session", autouse=True)
def assert_all_modules_tested() -> None:
    """Verify every source module has a corresponding test module.

    Auto-generates test skeletons for missing test modules/packages.

    Raises:
        AssertionError: If any source modules lack corresponding tests.
    """
    src_package = import_module(PackageManager.I.package_name())

    # we will now go through all the modules in the src package and check
    # that there is a corresponding test module
    all_modules = (m for m, is_pkg in walk_package(src_package) if not is_pkg)

    subclasses = MirrorTestConfigFile.I.make_subclasses_for_modules(all_modules)
    incorrect_subclasses = tuple(sc for sc in subclasses if not sc().is_correct())

    if incorrect_subclasses:
        MirrorTestConfigFile.I.validate_subclasses(incorrect_subclasses)

    msg = f"""Found incorrect test modules.
Test skeletons were automatically created.
{make_summary_error_msg(sc().path().as_posix() for sc in incorrect_subclasses)}
"""
    assert not incorrect_subclasses, msg


@pytest.fixture(scope="session", autouse=True)
def assert_dependencies_are_up_to_date() -> None:
    """Verify dependencies are up to date via ``uv lock --upgrade`` and ``uv sync``.

    Skipped if no internet connection is available.

    Raises:
        AssertionError: If dependency update or sync commands fail.
    """
    if not internet_is_available():
        logger.warning(
            "No internet, skipping %s",
            assert_dependencies_are_up_to_date.__name__,
        )
        return
    # update the dependencies
    args = PackageManager.I.update_dependencies_args()
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
    args = PackageManager.I.install_dependencies_args()
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


@pytest.fixture(scope="session", autouse=True)
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
            assert_src_runs_without_dev_deps.__name__,
        )
        return
    project_name = PackageManager.I.project_name()
    func_name = assert_src_runs_without_dev_deps.__name__
    tmp_path = tmp_path_factory.mktemp(func_name) / project_name
    # copy the project folder to a temp directory
    # run main.py from that directory
    src_package = import_module(PackageManager.I.package_name())
    src_package_file_str = src_package.__file__
    if src_package_file_str is None:
        msg = f"src_package.__file__ is None for {src_package}"
        raise ValueError(msg)

    project_path = Path(src_package_file_str).parent

    project_name = snake_to_kebab_case(src_package.__name__)

    temp_project_path = tmp_path / src_package.__name__

    # shutil copy the project to tmp_path
    shutil.copytree(project_path, temp_project_path)

    # copy pyproject.toml and uv.lock to tmp_path
    configs = (
        "pyproject.toml",
        "README.md",
        "LICENSE",
    )
    for config in configs:
        shutil.copy(config, temp_project_path.parent)

    # pop the venv from the environment
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    with chdir(tmp_path):
        # install deps
        completed_process = PackageManager.I.install_dependencies_no_dev_args().run(
            check=False,
            env=env,
        )
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        std_msg = stderr + stdout

        dev_dep = Tool.subclasses_dev_dependencies()[0]
        assert dev_dep not in std_msg, base_msg + f"{std_msg}"

        # delete pyproject.toml and uv.lock and readme.md
        for config in configs:
            Path(config).unlink()

        # run walk_package with src and import all modules to catch dev dep imports
        src_package_name = PackageManager.I.package_name()
        script_args = (
            "python",
            "-c",
            "; ".join(
                (
                    "from pyrig.src.modules.imports import walk_package",
                    f"from {src_package_name} import src",
                    "packages=tuple(walk_package(src))",
                    # add a print statement to see the output
                    "print('Success')",
                )
            ),
        )
        args = PackageManager.I.run_no_dev_args(*script_args)

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
        args = PackageManager.I.run_no_dev_args(project_name, "--help")
        completed_process = args.run(
            check=False,
        )
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        std_msg = stderr + stdout
        successful = completed_process.returncode == 0
        assert successful, base_msg + f"Expected {args} to succeed, got {std_msg}"


@pytest.fixture(scope="session", autouse=True)
def assert_package_manager_is_up_to_date() -> None:
    """Verify uv is up to date via ``uv self update`` (skipped in CI).

    Raises:
        AssertionError: If ``uv self update`` fails unexpectedly.
    """
    if not internet_is_available():
        logger.warning(
            "No internet, skipping %s",
            assert_package_manager_is_up_to_date.__name__,
        )
        return
    if not running_in_github_actions():
        # update project mgt
        completed_process = PackageManager.I.update_self_args().run(check=False)
        returncode = completed_process.returncode

        stderr = completed_process.stderr
        stdout = completed_process.stdout
        std_msg = stderr + stdout

        allowed_errors = ("GitHub API rate limit exceeded",)

        allowed_error_in_err_or_out = any(exp in std_msg for exp in allowed_errors)

        is_up_to_date = returncode == 0 or allowed_error_in_err_or_out

        msg = f"""The tool {PackageManager.I.name()} is not up to date.
This fixture ran `{PackageManager.I.update_self_args()}` but it failed.
Output: {std_msg}
"""
        assert is_up_to_date, msg

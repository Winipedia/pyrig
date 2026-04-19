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

from pyrig.core.introspection.packages import (
    walk_package,
)
from pyrig.core.requests import internet_is_available
from pyrig.core.strings import (
    make_summary_error_msg,
    pyrig_project_name,
    snake_to_kebab_case,
)
from pyrig.rig.cli.commands.make_inits import (
    make_init_files_for_namespace_packages,
)
from pyrig.rig.cli.subcommands import mkinits, mktests
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.markdown.readme import ReadmeConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.packages import (
    find_namespace_packages,
)
from pyrig.rig.utils.path import package_name_as_root_path

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def no_unstaged_changes_in_ci() -> Generator[None, None, None]:
    """Verify no unstaged git changes before and after tests (CI only).

    Yields:
        None: Control yielded to run tests, then checks again after.

    Raises:
        AssertionError: If unstaged changes detected in CI.
    """
    in_ci = RemoteVersionController.I.running_in_ci()

    msg = """Found unstaged changes during tests.
There should not be made any unstaged changes during tests.
This chekc only runs in CI to allow a normal development worklfow locally
where you may have unstaged changes. If xou want make changes during tests
then you must stage them to avoid this assertion error.

Found the following unstaged changes:
{unstaged_changes}
"""

    if in_ci:
        unstaged_changes = VersionController.I.has_unstaged_diff()
        assert not unstaged_changes, msg.format(
            unstaged_changes=VersionController.I.diff()
        )
    yield
    if in_ci:
        unstaged_changes = VersionController.I.has_unstaged_diff()
        assert not unstaged_changes, msg.format(
            unstaged_changes=VersionController.I.diff()
        )


@pytest.fixture(scope="session", autouse=True)
def all_config_files_correct() -> None:
    """Verify project root structure is correct, auto-fixing incorrect config files.

    Raises:
        AssertionError: If config files were incorrect (lists fixed paths).
    """
    # if we are in CI then we must create config files that are gitignored
    # as they are not pushed to the repository
    running_in_ci = RemoteVersionController.I.running_in_ci()
    if running_in_ci:
        tuple(cf().validate() for cf in ConfigFile.version_control_ignored_subclasses())

    incorrect_cfs = tuple(ConfigFile.incorrect_subclasses())

    if incorrect_cfs:
        # init all per test run
        ConfigFile.validate_subclasses(incorrect_cfs)

    msg = f"""Found incorrect {ConfigFile.__name__}s.
It was attempted to auto-fix them via their {ConfigFile.validate.__name__} method.
This should have created or updated the config files to be correct.

Please verify the changes at the following paths:
{make_summary_error_msg(cf().path() for cf in incorrect_cfs)}
"""
    assert not incorrect_cfs, msg


@pytest.fixture(scope="session", autouse=True)
def no_namespace_packages() -> None:
    """Verify all packages have __init__.py, auto-creating missing ones.

    Raises:
        AssertionError: If namespace packages were found (lists created paths).
    """
    namespace_packages = tuple(find_namespace_packages())
    if namespace_packages:
        make_init_files_for_namespace_packages(namespace_packages)

    msg = f"""Found namespace packages.
Namespace packages are packages that do not have an __init__.py file.
This fixture attempted to auto-fix this by creating the files for any namespace packages found.
Consider using the proper command to create __init__.py files for any namespace packages in the source directory:
    '{pyrig_project_name()} {snake_to_kebab_case(mkinits.__name__)}'

Please verify the changes at the following paths:
{make_summary_error_msg(package_name_as_root_path(package_name) / "__init__.py" for package_name in namespace_packages)}
"""  # noqa: E501
    assert not namespace_packages, msg


@pytest.fixture(scope="session", autouse=True)
def all_modules_tested() -> None:
    """Verify every source module has a corresponding test module.

    Auto-generates test skeletons for missing test modules/packages.

    Raises:
        AssertionError: If any source modules lack corresponding tests.
    """
    src_package = import_module(PackageManager.I.package_name())

    # we will now go through all the modules in the src package and check
    # that there is a corresponding test module
    all_modules = (m for m, is_pkg in walk_package(src_package) if not is_pkg)

    subclasses = MirrorTestConfigFile.L.generate_subclasses(all_modules)
    incorrect_subclasses = tuple(sc for sc in subclasses if not sc().is_correct())

    if incorrect_subclasses:
        MirrorTestConfigFile.L.validate_subclasses(incorrect_subclasses)

    msg = f"""Found incorrect test modules.
It is enforced that every module in src has a corresponding test module in tests.
The test module should mirror the structure package under the source directory.

Attempted to auto-generate test skeletons for any missing test modules via {MirrorTestConfigFile.L.__name__}

Consider using the proper command to create test skeletons for any missing test modules:
    '{pyrig_project_name()} {snake_to_kebab_case(mktests.__name__)}'

Please verify the changes at the following paths:
{make_summary_error_msg(sc().path() for sc in incorrect_subclasses)}
"""  # noqa: E501
    assert not incorrect_subclasses, msg


@pytest.fixture(scope="session", autouse=True)
def all_dependencies_updated(standard_output_error_template: str) -> None:
    """Verify dependencies are up to date via ``uv lock --upgrade`` and ``uv sync``.

    Skipped if no internet connection is available.

    Raises:
        AssertionError: If dependency update or sync commands fail.
    """
    if not internet_is_available():
        logger.warning(
            "No internet, skipping fixture: %s",
            all_dependencies_updated.__name__,
        )
        return

    # update the dependencies
    args = PackageManager.I.update_dependencies_args()
    completed_process = args.run(check=False)
    stderr = completed_process.stderr
    stdout = completed_process.stdout
    success = completed_process.returncode == 0

    msg = f"""Failed to update dependencies.

This fixture ran `{args}` to automatically update the dependencies to the latest versions.
However, it failed. See the output below for details.

{standard_output_error_template.format(stdout=stdout, stderr=stderr)}
"""  # noqa: E501
    assert success, msg

    # sync the dependencies
    args = PackageManager.I.install_dependencies_args()
    completed_process = args.run(check=False)
    stderr = completed_process.stderr
    stdout = completed_process.stdout
    success = completed_process.returncode == 0
    msg = f"""Failed to install dependencies.

This fixture ran `{args}` to automatically install the dependencies.
However, it failed. See the output below for details.

{standard_output_error_template.format(stdout=stdout, stderr=stderr)}
"""
    assert success, msg


@pytest.fixture(scope="session", autouse=True)
def no_dev_deps_in_source_code(
    tmp_path_factory: pytest.TempPathFactory, standard_output_error_template: str
) -> None:
    """Verify source code runs in isolated environment without dev dependencies.

    Creates temp environment, installs without dev group, imports all src modules,
    and runs CLI to catch any dev dependency usage.

    Args:
        tmp_path_factory: Session-scoped temp directory factory.
        standard_output_error_template: Template for formatting
            standard output and error messages.

    Raises:
        AssertionError: If source code cannot run without dev dependencies.
    """
    base_msg = f"""Failed to import all source modules without the development dependencies being installed.

This fixture attempts to create a temporary environment and install the project without
the development dependencies and to import all modules of the source code.
The most likely reason for this failure is that there is an import in the source code
that depends on a development dependency directly or indirectly.
This is not allowed as the source code should not depend on any development dependencies.

However, it failed. See the output below for details.

{standard_output_error_template}
"""  # noqa: E501
    if not internet_is_available():
        logger.warning(
            "No internet, skipping fixture: %s",
            no_dev_deps_in_source_code.__name__,
        )
        return

    project_name = PackageManager.I.project_name()
    tmp_project_root = (
        tmp_path_factory.mktemp(no_dev_deps_in_source_code.__name__) / project_name
    )
    # copy the project folder to a temp directory
    temp_source_root = tmp_project_root / PackageManager.I.source_root()

    # shutil copy the project to tmp_project_root
    shutil.copytree(PackageManager.I.source_root(), temp_source_root)

    # copy pyproject.toml and uv.lock to tmp_path
    configs = (
        PyprojectConfigFile.I.path(),
        ReadmeConfigFile.I.path(),
        LicenseConfigFile.I.path(),
    )
    for config in configs:
        shutil.copy(config, tmp_project_root)

    # pop the venv from the environment
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    with chdir(tmp_project_root):
        # install deps
        completed_process = PackageManager.I.install_dependencies_no_dev_args().run(
            check=False,
            env=env,
        )
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        std_msg = stderr + stdout

        dev_dep = Tool.subclasses_dev_dependencies()[0]
        assert dev_dep not in std_msg, base_msg.format(stdout=stdout, stderr=stderr)

        # delete pyproject.toml and uv.lock and readme.md
        for config in configs:
            Path(config).unlink()

        # run walk_package with src and import all modules to catch dev dep imports
        src_package_name = PackageManager.I.package_name()
        exclude_rig_pattern = rf"^{src_package_name}\.rig"
        script_args = (
            "python",
            "-c",
            "; ".join(
                (
                    f"from {walk_package.__module__} import {walk_package.__name__}",
                    f"import {src_package_name}",
                    f"exclude_rig_pattern = r'{exclude_rig_pattern}'",
                    f"packages = tuple(walk_package({src_package_name}, exclude=(exclude_rig_pattern,)))",  # noqa: E501
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

        assert "Success" in stdout, base_msg.format(stdout=stdout, stderr=stderr)

        # run cli without dev deps
        args = PackageManager.I.run_no_dev_args(project_name, "--help")
        completed_process = args.run(
            check=False,
        )
        stdout = completed_process.stdout
        stderr = completed_process.stderr
        std_msg = stderr + stdout
        successful = completed_process.returncode == 0
        assert successful, base_msg.format(stdout=stdout, stderr=stderr)


@pytest.fixture(scope="session", autouse=True)
def package_manager_updated(standard_output_error_template: str) -> None:
    """Verify uv is up to date via ``uv self update`` (skipped in CI).

    Raises:
        AssertionError: If ``uv self update`` fails unexpectedly.
    """
    if not internet_is_available():
        logger.warning(
            "No internet, skipping fixture: %s",
            package_manager_updated.__name__,
        )
        return

    # this only needed locally, in CI the latest version is used automatically
    # by the CI environment, and running self update can cause issues there
    if RemoteVersionController.I.running_in_ci():
        return

    # update the package manager itself
    completed_process = PackageManager.I.update_self_args().run(check=False)
    returncode = completed_process.returncode

    stderr = completed_process.stderr
    stdout = completed_process.stdout
    std_msg = stderr + stdout

    allowed_errors = ("GitHub API rate limit exceeded",)
    allowed_error_in_err_or_out = any(exp in std_msg for exp in allowed_errors)

    is_up_to_date = returncode == 0 or allowed_error_in_err_or_out

    msg = f"""The {PackageManager.I} is not up to date.

This fixture ran `{PackageManager.I.update_self_args()}` to automatically update the package manager to the latest version.
However, it failed. See the output below for details.

{standard_output_error_template.format(stdout=stdout, stderr=stderr)}
"""  # noqa: E501
    assert is_up_to_date, msg

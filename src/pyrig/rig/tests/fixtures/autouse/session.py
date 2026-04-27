"""Session-scoped autouse fixtures for project-wide validation and setup.

These fixtures run automatically once per test session to enforce project
structure, code quality, and development environment standards across every
test run.
"""

import logging
import os
import shutil
from collections.abc import Generator
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.core.introspection.packages import (
    walk_package,
)
from pyrig.core.iterate import generator_has_items
from pyrig.core.requests import internet_is_available
from pyrig.core.strings import (
    make_summary_error_msg,
)
from pyrig.rig.cli.subcommands import mkinits, mkroot, mktests
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.markdown.readme import ReadmeConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.packages import (
    find_namespace_packages,
)
from pyrig.rig.utils.paths import package_name_as_root_path

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def no_unstaged_changes_in_ci() -> Generator[None, None, None]:
    """Fail if the working tree has unstaged changes before or after the test session.

    Wraps the entire test session via a yield. Checks for unstaged git changes
    before tests run and again after they finish. The check is skipped locally
    to allow a normal development workflow with in-progress edits. In CI, any
    unstaged change — whether present before tests or introduced during them —
    is treated as an error that must be reviewed and either committed or
    discarded. Staged (indexed) changes are always permitted.

    Yields:
        None: Control yielded to run the full test session.

    Raises:
        AssertionError: If unstaged changes are detected in CI, either before
            or after the test session.
    """
    in_ci = RemoteVersionController.I.running_in_ci()

    msg = """Found unstaged changes during tests.
There should not be made any unstaged changes during tests in CI.
This check only runs in CI to allow a normal development workflow locally
where you may have unstaged changes. If you want to make changes during tests
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
    """Fail if any version-controlled config files are incorrect.

    Checks all config files that are tracked by version control. Git-ignored
    files (such as ``.env`` and ``.scratch``) are excluded because they are
    not committed and are expected to be managed manually.

    Raises:
        AssertionError: If any version-controlled config files are incorrect,
            listing the affected paths.
    """
    has_incorrect_cfs, incorrect_cfs = generator_has_items(
        ConfigFile.discard_correct_subclasses(
            ConfigFile.version_controlled_subclasses()
        )
    )

    msg = f"""Found incorrect {ConfigFile.__name__}s.
Please run the following command to fix any incorrect config files:
    '{Pyrigger.I.cmd_args(cmd=mkroot)}'

{make_summary_error_msg(cf().path() for cf in incorrect_cfs)}
"""
    assert not has_incorrect_cfs, msg


@pytest.fixture(scope="session", autouse=True)
def no_namespace_packages() -> None:
    """Fail if any packages are missing an ``__init__.py`` file.

    A namespace package is a Python package directory that lacks an
    ``__init__.py`` file. While Python supports them, this project requires
    explicit ``__init__.py`` files everywhere to keep package discovery
    predictable.

    Raises:
        AssertionError: If any namespace packages are found, listing the
            paths of the missing ``__init__.py`` files.
    """
    has_namespace_packages, namespace_packages = generator_has_items(
        find_namespace_packages()
    )

    msg = f"""Found namespace packages.
Namespace packages are packages that do not have an __init__.py file.
All packages should have an __init__.py file to ensure predictable package discovery.
Please run the following command to create __init__.py files for any namespace packages:
    '{Pyrigger.I.cmd_args(cmd=mkinits)}'

{make_summary_error_msg(package_name_as_root_path(package_name) / "__init__.py" for package_name in namespace_packages)}
"""  # noqa: E501
    assert not has_namespace_packages, msg


@pytest.fixture(scope="session", autouse=True)
def all_modules_tested() -> None:
    """Fail if any source module lacks a corresponding test module.

    Enforces a one-to-one mirror between the source package tree and the test
    package tree. The leaf subclass ``MirrorTestConfigFile.L`` is discovered at
    runtime via the cross-package subclass discovery mechanism.

    Raises:
        AssertionError: If any source modules lack a corresponding test
            module, listing the affected paths.
    """
    has_incorrect_subclasses, incorrect_subclasses = generator_has_items(
        MirrorTestConfigFile.L.incorrect_subclasses()
    )

    msg = f"""Found incorrect test modules.
It is enforced that all source code has a corresponding mirrored test.

Please run the following command to generate test skeletons for any missing tests:
    '{Pyrigger.I.cmd_args(cmd=mktests)}'

{make_summary_error_msg(sc().path() for sc in incorrect_subclasses)}
"""
    assert not has_incorrect_subclasses, msg


@pytest.fixture(scope="session", autouse=True)
def package_manager_updated(standard_output_error_template: str) -> None:
    """Update the ``uv`` package manager to the latest version.

    Runs ``uv self update`` locally to keep the package manager current.
    Skipped in CI because the CI environment always provisions the latest
    version of ``uv``, and running a self-update there can cause unexpected
    behaviour. Also skipped when no internet connection is available.

    A GitHub API rate-limit error is treated as a successful outcome because
    the update cannot proceed in that case and there is no actionable fix.

    Args:
        standard_output_error_template: Template for formatting stdout and
            stderr in assertion failure messages.

    Raises:
        AssertionError: If ``uv self update`` fails for any reason other
            than a GitHub API rate limit.
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


@pytest.fixture(scope="session", autouse=True)
def all_dependencies_updated(standard_output_error_template: str) -> None:
    """Update all project dependencies and sync the virtual environment.

    Runs two commands in sequence:

    1. ``uv lock --upgrade`` — resolves the latest compatible versions of
       all dependencies and writes them to ``uv.lock``.
    2. ``uv sync`` — installs packages from the updated lock file, adding
       or removing packages as needed.

    Skipped when no internet connection is available.

    Args:
        standard_output_error_template: Template for formatting stdout and
            stderr in assertion failure messages.

    Raises:
        AssertionError: If either the lock upgrade or the sync command
            exits with a non-zero return code.
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
    """Verify the source code is fully functional without development dependencies.

    This fixture detects accidental imports of development-only packages from
    source code. It performs three checks in an isolated environment:

    1. **Install check** — copies the source tree and project config files to
       a temporary directory, then installs the project without the ``dev``
       dependency group. Asserts that no known dev dependency appears in the
       installation output.

    2. **Import check** — walks all modules under the source package
       (excluding ``rig``) and imports them in the isolated environment.
       Asserts all modules import without error, catching indirect dev
       dependency usage.

    3. **CLI check** — invokes the project's CLI entry point with ``--help``
       in the isolated environment. Asserts the command exits successfully.

    Skipped when no internet connection is available.

    Args:
        tmp_path_factory: Session-scoped temporary directory factory used
            to create the isolated project copy.
        standard_output_error_template: Template for formatting stdout and
            stderr in assertion failure messages.

    Raises:
        AssertionError: If any of the three checks fail, indicating the
            source code has a direct or indirect dependency on a dev-only
            package.
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

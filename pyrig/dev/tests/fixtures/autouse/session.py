"""Session-level test fixtures and utilities.

These fixtures in this module are automatically applied to the test session
through pytest's autouse mechanism. Pyrig automatically adds this module to
pytest_plugins in conftest.py. However you still have decorate the fixture
with @autouse_session_fixture from pyrig.src.testing.fixtures or with pytest's
autouse mechanism @pytest.fixture(scope="session", autouse=True).
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
    """Verify that there are no unstaged changes.

    Checks before and after the test session if there are unstaged changes.
    If there are unstaged changes before the test session, it fails.
    If there are unstaged changes after the test session, it fails.

    Raises:
        AssertionError: If there are unstaged changes

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
    """Verify that the dev dependencies are installed.

    This fixture runs once per test session and checks that the dev dependencies
    are installed by trying to import them.

    Raises:
        ImportError: If a dev dependency is not installed

    """
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
    """Verify that there are no namespace packages in the project.

    This fixture runs once per test session and checks that all packages in the
    project are regular packages with __init__.py files, not namespace packages.

    Raises:
        AssertionError: If any namespace packages are found

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
    """Verify that all source code is in a single package.

    This fixture runs once per test session and checks that there is only one
    source package besides the tests package.

    Raises:
        AssertionError: If there are multiple source packages

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
    """Verify that the source package is correctly named.

    This fixture runs once per test session and checks that the source package
    is correctly named after the project.

    Raises:
        AssertionError: If the source package is not correctly named

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
    """Verify that the unit test package is not used in the project.

    This fixture runs once per test session and checks that the unit test package
    is not used in the project.

    Raises:
        AssertionError: If the unit test package is used

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
    """Verify that the dependencies are up to date.

    This fixture runs once per test session
    to make sure the dependencies are up to date.
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
    """Verify that pre-commit is installed.

    This fixture runs once per test session and runs pre-commit install
    to make sure pre-commit is installed.
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
    """Verify that the source code runs without dev dependencies.

    This fixture runs once per test session and checks that the source code
    runs without dev dependencies.
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
    """Verify that the source code does not import any code from dev.

    This tests that the src folder has no code that depends on dev code.
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
    """Checks that all of pyrigs dev deps are in toml."""
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
    """Verify that the project management tool is up to date."""
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
    """Verify that git is installed.

    As pyrig needs and expects git to be installed.
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
    """Verify that podman is installed.

    As pyrig needs and expects podman to be installed.
    """
    if not running_in_github_actions():
        completed_process = run_subprocess(["podman", "--version"], check=False)
        stderr = completed_process.stderr.decode("utf-8")
        stdout = completed_process.stdout.decode("utf-8")
        std_msg = stderr + stdout
        # use re expression to check if podman version is in the output
        podman_is_installed = re.search(r"podman version \d+\.\d+\.\d+", std_msg)

        assert podman_is_installed, f"Expected podman to be installed, got: {std_msg}"

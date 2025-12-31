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
    assert_pre_commit_is_installed: Pre-commit hooks installed.
    assert_src_runs_without_dev_deps: Source runs without dev dependencies.
    assert_src_does_not_use_dev: Source doesn't import dev code.
    assert_project_mgt_is_up_to_date: uv up to date (local only).
    assert_version_control_is_installed: Git installed.
    assert_container_engine_is_installed: Podman installed (local only).
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
from pyrig.dev.cli.commands.create_root import make_project_root
from pyrig.dev.cli.commands.make_inits import make_init_files
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import (
    PyprojectConfigFile,
)
from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile
from pyrig.dev.tests.mirror_test import MirrorTestConfigFile
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
)
from pyrig.src.modules.package import (
    DOCS_DIR_NAME,
    DependencyGraph,
    get_pkg_name_from_project_name,
    get_project_name_from_pkg_name,
)
from pyrig.src.modules.path import ModulePath
from pyrig.src.os.os import run_subprocess
from pyrig.src.string import re_search_excluding_docstrings
from pyrig.src.testing.convention import (
    TESTS_PACKAGE_NAME,
    make_summary_error_msg,
)

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

    msg = (
        "Found unstaged changes. Please commit or stash them. "
        "Unstaged changes: {unstaged_changes}"
    )

    if in_github_actions:
        unstaged_changes = get_git_unstaged_changes()
        assert not unstaged_changes, msg.format(unstaged_changes=unstaged_changes)
    yield
    if in_github_actions:
        unstaged_changes = get_git_unstaged_changes()
        assert not unstaged_changes, msg.format(unstaged_changes=unstaged_changes)


@autouse_session_fixture
def assert_root_is_correct() -> None:
    """Verify project root structure is correct, auto-fixing incorrect config files.

    Raises:
        AssertionError: If config files were incorrect (lists fixed paths).
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

    msg = f"""Found {len(any_namespace_packages)} namespace packages.
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

    Checks that only expected top-level packages exist (source, tests, docs)
    and source package has exactly dev, src, resources subpackages and main module.

    Raises:
        AssertionError: If unexpected packages/subpackages/submodules found.
    """
    packages = find_packages(depth=0)
    src_package = get_src_package()
    src_package_name = src_package.__name__
    expected_packages = {TESTS_PACKAGE_NAME, src_package_name, DOCS_DIR_NAME}

    # pkgs must be subset of expected_packages
    assert set(packages).issubset(expected_packages), (
        f"Expected only packages {expected_packages}, but found {packages}"
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
    assert subpackage_names == expected_subpackages, (
        f"Expected subpackages {expected_subpackages}, but found {subpackage_names}"
    )
    assert submodule_names == expected_submodules, (
        f"Expected submodules {expected_submodules}, but found {submodule_names}"
    )


@autouse_session_fixture
def assert_src_package_correctly_named() -> None:
    """Verify source package name matches project naming conventions.

    Checks CWD name matches pyproject.toml project name and package name.

    Raises:
        AssertionError: If any naming mismatch detected.
    """
    cwd_name = Path.cwd().name
    project_name = PyprojectConfigFile.get_project_name()
    assert cwd_name == project_name, (
        f"Expected cwd name to be {project_name}, but it is {cwd_name}"
    )

    src_package_name = get_src_package().__name__
    src_package_name_from_cwd = get_pkg_name_from_project_name(cwd_name)
    msg = (
        f"Expected source package to be named {src_package_name_from_cwd}, "
        f"but it is named {src_package_name}"
    )
    assert src_package_name == src_package_name_from_cwd, msg

    src_package = get_src_package().__name__
    expected_package = PyprojectConfigFile.get_package_name()
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
    src_package = get_src_package()

    # we will now go through all the modules in the src package and check
    # that there is a corresponding test module
    all_modules = []
    for _, modules in walk_package(src_package):
        all_modules.extend(modules)

    mirror_test_cls = MirrorTestConfigFile.leaf()
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

    msg = f"""Found {"UnitTest".lower()} package usage in:
    {make_summary_error_msg(usages)}
"""
    assert not usages, msg


@autouse_session_fixture
def assert_dependencies_are_up_to_date() -> None:
    """Verify dependencies are up to date via ``uv lock --upgrade`` and ``uv sync``.

    Raises:
        AssertionError: If dependencies were updated or installed.
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
    """Verify pre-commit hooks are installed via ``pre-commit install``.

    Raises:
        AssertionError: If pre-commit installation fails.
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
    """Verify source code runs in isolated environment without dev dependencies.

    Creates temp environment, installs without dev group, imports all src modules,
    and runs CLI to catch any dev dependency usage.

    Args:
        tmp_path_factory: Session-scoped temp directory factory.

    Raises:
        AssertionError: If source code cannot run without dev dependencies.
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
                f"import {src_pkg_name}; "
                f"src_module=import_module(get_module_name_replacing_start_module(src, {src_pkg_name}.__name__)); "  # noqa: E501
                "pks=list(walk_package(src_module)); "
                "assert isinstance(pks, list), 'Expected pks to be a list'; "
                "assert len(pks) > 0, 'Expected pks to not be empty'; "
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
    """Verify source code does not import any dev code.

    Scans src subpackage for dev import statements to ensure production/dev
    separation.

    Raises:
        AssertionError: If any dev imports found in src code.
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

        This fixture ran `uv self update` but determined that you were not up to date.
        """
        assert expected_in_err_or_out, msg


@autouse_session_fixture
def assert_version_control_is_installed() -> None:
    """Verify git is installed via ``git --version``.

    Raises:
        AssertionError: If git is not installed or not accessible.
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
    """Verify podman is installed via ``podman --version`` (skipped in CI).

    Raises:
        AssertionError: If podman is not installed or not accessible.
    """
    if not running_in_github_actions():
        completed_process = run_subprocess(["podman", "--version"], check=False)
        stderr = completed_process.stderr.decode("utf-8")
        stdout = completed_process.stdout.decode("utf-8")
        std_msg = stderr + stdout
        # use re expression to check if podman version is in the output
        podman_is_installed = re.search(r"podman version \d+\.\d+\.\d+", std_msg)

        assert podman_is_installed, f"Expected podman to be installed, got: {std_msg}"

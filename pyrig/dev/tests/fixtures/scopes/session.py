"""Session-level test fixtures and utilities.

These fixtures in this module are automatically applied to the test session
through pytest's autouse mechanism. Pyrig automatically adds this module to
pytest_plugins in conftest.py. However you still have decorate the fixture
with @autouse_session_fixture from pyrig.src.testing.fixtures or with pytest's
autouse mechanism @pytest.fixture(scope="session", autouse=True).
"""

import logging
import os
import shutil
from contextlib import chdir
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from pyrig.dev.cli.subcommands import create_root
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.git.gitignore import GitIgnoreConfigFile
from pyrig.dev.configs.git.pre_commit import PreCommitConfigConfigFile
from pyrig.dev.configs.pyproject import (
    PyprojectConfigFile,
)
from pyrig.dev.configs.python.experiment import DotExperimentConfigFile
from pyrig.dev.tests.utils.decorators import autouse_session_fixture
from pyrig.src.git.github.github import running_in_github_actions
from pyrig.src.modules.module import (
    import_module_with_default,
    make_init_module,
    to_path,
)
from pyrig.src.modules.package import (
    find_packages,
    get_modules_and_packages_from_package,
    get_src_package,
    walk_package,
)
from pyrig.src.os.os import run_subprocess
from pyrig.src.testing.assertions import assert_with_msg
from pyrig.src.testing.convention import (
    TESTS_PACKAGE_NAME,
    make_test_obj_importpath_from_obj,
    make_untested_summary_error_msg,
)
from pyrig.src.testing.create_tests import create_tests

if TYPE_CHECKING:
    from types import ModuleType

logger = logging.getLogger(__name__)


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
    all_correct = all(subclass.is_correct() for subclass in subclasses)

    if not all_correct:
        create_root()

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
    if any_namespace_packages:
        # make init files for all namespace packages
        for package in any_namespace_packages:
            make_init_module(to_path(package, is_package=True))

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
    expected_packages = {TESTS_PACKAGE_NAME, src_package_name}
    assert_with_msg(
        set(packages) == expected_packages,
        f"Expected only packages {expected_packages}, but found {packages}",
    )

    # assert the src package's only submodules are main, src and dev
    subpackages, submodules = get_modules_and_packages_from_package(src_package)
    subpackage_names = {p.__name__.split(".")[-1] for p in subpackages}
    submodule_names = {m.__name__.split(".")[-1] for m in submodules}
    expected_subpackages = {"src", "dev"}
    expected_submodules = {"main"}
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
        if GitIgnoreConfigFile.path_is_in_gitignore(path):
            continue
        assert_with_msg(
            "UnitTest".lower() not in path.read_text(encoding="utf-8"),
            f"Found unit test package usage in {path}. Use pytest instead.",
        )


@autouse_session_fixture
def assert_dependencies_are_up_to_date() -> None:
    """Verify that the dependencies are up to date.

    This fixture runs once per test session
    to make sure the dependencies are up to date.
    """
    if not running_in_github_actions():
        # update project mgt
        completed_process = run_subprocess(["uv", "self", "update"], check=False)
        stderr = completed_process.stderr.decode("utf-8")
        expected = "success: You're on the latest version of uv"
        expected_err = "GitHub API rate limit exceeded"
        assert_with_msg(
            expected in stderr or expected_err in stderr,
            f"Expected {expected} in uv self update output, got {stderr}",
        )

    # update the dependencies
    completed_process = PyprojectConfigFile.update_dependencies(check=True)
    # if there were updates raise an error
    expected = "Resolved"
    expected2 = "packages"
    stderr = completed_process.stderr.decode("utf-8")
    assert_with_msg(
        expected in stderr and expected2 in stderr,
        f"Expected {expected} and {expected2} in uv update output, got {stderr}",
    )

    # sync the dependencies
    completed_process = PyprojectConfigFile.install_dependencies(check=True)
    stderr = completed_process.stderr.decode("utf-8")
    expected = "Resolved"
    expected2 = "Audited"
    assert_with_msg(
        expected in stderr and expected2 in stderr,
        f"Expected {expected} and {expected2} in uv install output, got {stderr}",
    )


@autouse_session_fixture
def assert_pre_commit_is_installed() -> None:
    """Verify that pre-commit is installed.

    This fixture runs once per test session and runs pre-commit install
    to make sure pre-commit is installed.
    """
    completed_process = PreCommitConfigConfigFile.install()
    stdout = completed_process.stdout.decode("utf-8")
    logger.info("Pre-commit install output: %s", stdout)
    expected = "pre-commit installed at"

    assert_with_msg(
        expected in stdout,
        f"Expected {expected} in pre-commit install output, got {stdout}",
    )


@autouse_session_fixture
def assert_src_runs_without_dev_deps(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Verify that the source code runs without dev dependencies.

    This fixture runs once per test session and checks that the source code
    runs without dev dependencies.
    """
    tmp_path = tmp_path_factory.mktemp(assert_src_runs_without_dev_deps.__name__)
    # copy the project folder to a temp directory
    # run main.py from that directory
    src_package = get_src_package()
    src_package_file_str = src_package.__file__
    if src_package_file_str is None:
        msg = f"src_package.__file__ is None for {src_package}"
        raise ValueError(msg)

    project_path = Path(src_package_file_str).parent

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
        run_subprocess(["uv", "sync", "--no-dev"], env=env)

        # delete pyproject.toml and uv.lock and readme.md
        for config in configs:
            Path(config).unlink()
        # python -m video_vault.main

        # assert pytest is not installed
        dev_dep = "pytest"
        installed = run_subprocess(
            ["uv", "run", "pip", "show", dev_dep], check=False, env=env
        )
        stderr = installed.stderr.decode("utf-8")
        dev_dep_not_installed = f"not found: {dev_dep}" in stderr
        assert_with_msg(
            dev_dep_not_installed,
            f"Expected {dev_dep} not to be installed",
        )
        # check pytest is not importable
        installed = run_subprocess(
            ["uv", "run", "python", "-c", "import pytest"], check=False, env=env
        )
        stderr = installed.stderr.decode("utf-8")
        assert_with_msg(
            "ModuleNotFoundError" in stderr,
            f"Expected ModuleNotFoundError in stderr, got {stderr}",
        )

        # run walk_package with src and import all modules to catch dev dep imports
        cmd = [
            "uv",
            "run",
            "--no-dev",
            "python",
            "-c",
            (
                "from importlib import import_module; "
                "from pyrig import main; "
                "from pyrig import src; "
                "from pyrig.dev.configs.base.base import ConfigFile; "
                "from pyrig.src.modules.package import get_src_package, walk_package; "
                "from pyrig.src.testing.assertions import assert_with_msg; "
                "src_package=get_src_package(); "
                "src_module=import_module(ConfigFile.get_module_name_replacing_start_module(src, src_package.__name__)); "  # noqa: E501
                "pks=list(walk_package(src_module)); "
                "assert_with_msg(isinstance(pks, list), 'Expected pks to be a list'); "
                "assert_with_msg(len(pks) > 0, 'Expected pks to not be empty'); "
                # also test that main can be called
                "main_module=import_module(ConfigFile.get_module_name_replacing_start_module(main, src_package.__name__)); "  # noqa: E501
                # add a print statement to see the output
                "print('Success')"
            ),
        ]

        completed_process = run_subprocess(cmd, env=env, check=False)
        stdout = completed_process.stdout.decode("utf-8")
        stderr = completed_process.stderr.decode("utf-8")
        assert_with_msg(
            "Success" in stdout,
            f"Expected Success in stdout, got {stdout} and {stderr}",
        )

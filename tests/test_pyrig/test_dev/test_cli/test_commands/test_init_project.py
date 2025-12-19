"""Tests module."""

import logging
import os
import re
import shutil
from contextlib import chdir
from pathlib import Path

from pytest_mock import MockFixture

import pyrig
from pyrig.dev.cli.commands.init_project import (
    adding_dev_dependencies,
    committing_initial_changes,
    creating_priority_config_files,
    creating_project_root,
    creating_test_files,
    running_pre_commit_hooks,
    running_tests,
    syncing_venv,
)
from pyrig.dev.cli.subcommands import init
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.main import main
from pyrig.src.modules.module import make_obj_importpath
from pyrig.src.modules.path import ModulePath
from pyrig.src.project.mgt import DependencyManager, Pyrig, VersionControl
from pyrig.src.testing.assertions import assert_with_msg

logger = logging.getLogger(__name__)


def test_adding_dev_dependencies(mocker: MockFixture) -> None:
    """Test function."""
    mock = mocker.patch("subprocess.run")
    adding_dev_dependencies()
    mock.assert_called_once()


def test_running_tests(mocker: MockFixture) -> None:
    """Test function."""
    mock = mocker.patch("subprocess.run")
    running_tests()
    mock.assert_called_once()


def test_creating_priority_config_files(mocker: MockFixture) -> None:
    """Test func."""
    mock = mocker.patch(make_obj_importpath(ConfigFile.init_priority_config_files))
    creating_priority_config_files()
    mock.assert_called_once()


def test_creating_project_root(mocker: MockFixture) -> None:
    """Test func for run_create_root."""
    # mock the real underlying subprocess.run from subprocess pkg
    mock = mocker.patch("subprocess.run")
    creating_project_root()
    mock.assert_called_once()


def test_syncing_venv(mocker: MockFixture) -> None:
    """Test func for sync_venv."""
    # mock the real underlying subprocess.run from subprocess pkg
    mock_run = mocker.patch("subprocess.run")
    syncing_venv()
    mock_run.assert_called_once()


def test_creating_test_files(mocker: MockFixture) -> None:
    """Test func for run_create_tests."""
    # mock the real underlying subprocess.run from subprocess pkg
    mock_run = mocker.patch("subprocess.run")
    creating_test_files()
    mock_run.assert_called_once()


def test_committing_initial_changes(mocker: MockFixture) -> None:
    """Test func for commit_initial_changes."""
    # mock the real underlying subprocess.run from subprocess pkg
    mock_run = mocker.patch("subprocess.run")
    committing_initial_changes()
    mock_run.assert_called_once()


def test_running_pre_commit_hooks(mocker: MockFixture) -> None:
    """Test func for run_all_hooks."""
    # mock the real underlying subprocess.run from subprocess pkg
    mock_run = mocker.patch("subprocess.run")
    running_pre_commit_hooks()
    mock_run.assert_called()


def test_init_project(tmp_path: Path) -> None:
    """Test func for init."""
    # on Actions windows-latest temp path is on another drive so add path fails
    # so we use a tmp dir in the current dir
    # now test that in an empty folder with a pyproject.toml file
    # with a folder src that the setup works

    # copy the pyrig package to tmp_path/pyrig with shutil
    project_name = "src-project"

    pyrig_temp_path = tmp_path / PyprojectConfigFile.get_project_name()
    pyrig_path = ModulePath.pkg_type_to_dir_path(pyrig)
    shutil.copytree(
        pyrig_path.parent,
        pyrig_temp_path,
    )
    pyrig_temp_path = pyrig_temp_path.resolve()
    with chdir(pyrig_temp_path):
        # build the package
        args = DependencyManager.get_build_args()
        args.run()

    dist_files = list((pyrig_temp_path / "dist").glob("*.whl"))
    wheel_path = dist_files[-1].resolve().as_posix()

    src_project_dir = tmp_path / project_name
    src_project_dir.mkdir()

    # Get the current Python version in major.minor format
    python_version = str(PyprojectConfigFile.get_first_supported_python_version())

    # Initialize git repo in the test project directory
    with chdir(src_project_dir):
        VersionControl.get_init_args().run()
        VersionControl.get_config_local_user_email_args("test@example.com").run()
        VersionControl.get_config_local_user_name_args("Test User").run()

    with chdir(src_project_dir):
        # Create a clean environment dict without VIRTUAL_ENV to force
        # to create a new virtual environment instead of reusing the current one
        clean_env = os.environ.copy()
        clean_env.pop("VIRTUAL_ENV", None)

        args = DependencyManager.get_init_project_args("--python", python_version)
        args.run(env=clean_env)

        # Add pyrig wheel as a dependency
        DependencyManager.get_add_dependencies_args(wheel_path).run(env=clean_env)

        # uv add converts absolute paths to relative paths, which breaks when
        # the project is copied to a different location (e.g., in the
        # assert_src_runs_without_dev_deps fixture). We need to replace the
        # relative path with an absolute path.
        pyproject_toml = src_project_dir / "pyproject.toml"
        pyproject_content = pyproject_toml.read_text(encoding="utf-8")
        # Replace relative path with absolute path in tool.uv.sources
        # e.g., { path = "../pyrig/dist/..." } -> { path = "/tmp/.../pyrig/dist/..." }
        pyproject_content = re.sub(
            r'pyrig = \{ path = "[^"]*" \}',
            f'pyrig = {{ path = "{wheel_path}" }}',
            pyproject_content,
        )
        pyproject_toml.write_text(pyproject_content, encoding="utf-8")

        # Sync to update the lock file with the new absolute path
        args = DependencyManager.get_install_dependencies_args()
        args.run(env=clean_env)

        # Verify pyrig was installed correctly by running init also assert init passes
        args = Pyrig.get_venv_run_cmd_args(init)
        stdout = args.run(env=clean_env).stdout.decode("utf-8")

        # assert the pkgs own cli is available
        args = DependencyManager.get_run_args(project_name, "--help")
        res = args.run(env=clean_env)
        stdout = res.stdout.decode("utf-8")
        expected = project_name
        assert_with_msg(
            expected in stdout.lower(),
            f"Expected {expected} in stdout, got {stdout}",
        )
        #  assert running the main command works
        args = DependencyManager.get_run_args(project_name, main.__name__)
        res = args.run(env=clean_env)
        assert res.returncode == 0, f"Expected returncode 0, got {res.returncode}"

        # asert calling version works
        args = DependencyManager.get_run_args(project_name, "version")
        res = args.run(env=clean_env)
        stdout = res.stdout.decode("utf-8")
        expected = f"{project_name} version 0.1.0"
        assert expected in stdout, f"Expected {expected} in stdout, got {stdout}"

    pkg_dir = src_project_dir / "src_project"
    assert_with_msg(
        (pkg_dir / "__init__.py").exists(),
        f"Expected {pkg_dir / '__init__.py'} to be created",
    )

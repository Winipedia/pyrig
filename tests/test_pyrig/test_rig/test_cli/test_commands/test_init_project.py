"""Tests module."""

import logging
import os
import re
import shutil
from contextlib import chdir
from pathlib import Path

import tomlkit

import pyrig
from pyrig.main import main
from pyrig.rig.cli.commands.init_project import (
    adding_dev_dependencies,
    committing_initial_changes,
    creating_priority_config_files,
    creating_project_root,
    creating_test_files,
    get_setup_steps,
    initializing_version_control,
    running_pre_commit_hooks,
    running_tests,
    syncing_venv,
)
from pyrig.rig.cli.subcommands import init
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.version_controller import VersionController
from pyrig.src.modules.path import ModulePath
from pyrig.src.processes import Args

logger = logging.getLogger(__name__)


def test_get_setup_steps() -> None:
    """Test that get_setup_steps returns a non-empty list of callables."""
    steps = get_setup_steps()
    assert isinstance(steps, list), f"Expected list, got {type(steps)}"
    assert len(steps) > 0, "Expected non-empty list of setup steps"
    assert all(callable(step) for step in steps), "All steps should be callable"


def test_initializing_version_control() -> None:
    """Test function."""
    res = initializing_version_control()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_adding_dev_dependencies() -> None:
    """Test function."""
    res = adding_dev_dependencies()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_running_tests() -> None:
    """Test function."""
    res = running_tests()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_creating_priority_config_files() -> None:
    """Test func."""
    res = creating_priority_config_files()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_creating_project_root() -> None:
    """Test func for run_create_root."""
    # mock the real underlying subprocess.run from subprocess pkg
    res = creating_project_root()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_syncing_venv() -> None:
    """Test func for sync_venv."""
    res = syncing_venv()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_creating_test_files() -> None:
    """Test func for run_create_tests."""
    res = creating_test_files()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_committing_initial_changes() -> None:
    """Test func for commit_initial_changes."""
    res = committing_initial_changes()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_install_pre_commit_hooks() -> None:
    """Test function."""
    res = running_pre_commit_hooks()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_add_all_files_to_version_control() -> None:
    """Test function."""
    res = VersionController.L.get_add_all_args()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_running_pre_commit_hooks() -> None:
    """Test func for run_all_hooks."""
    res = running_pre_commit_hooks()
    assert isinstance(res, Args), f"Expected Args, got {type(res)}"


def test_init_project(tmp_path: Path) -> None:  # noqa: PLR0915
    """Test func for init."""
    # on Actions windows-latest temp path is on another drive so add path fails
    # so we use a tmp dir in the current dir
    # now test that in an empty folder with a pyproject.toml file
    # with a folder src that the setup works

    # copy the pyrig package to tmp_path/pyrig with shutil
    project_name = "src-project"

    pyrig_temp_path = tmp_path / PyprojectConfigFile.L.get_project_name()
    pyrig_path = ModulePath.pkg_type_to_dir_path(pyrig)
    shutil.copytree(
        pyrig_path.parent,
        pyrig_temp_path,
    )
    pyrig_temp_path = pyrig_temp_path.resolve()
    with chdir(pyrig_temp_path):
        # build the package
        args = PackageManager.L.get_build_args()
        args.run()

    dist_files = list((pyrig_temp_path / "dist").glob("*.whl"))
    wheel_path = dist_files[-1].resolve().as_posix()

    src_project_dir = tmp_path / project_name
    src_project_dir.mkdir()

    # Get the current Python version in major.minor format
    python_version = str(PyprojectConfigFile.L.get_first_supported_python_version())

    # Initialize git repo in the test project directory
    with chdir(src_project_dir):
        VersionController.L.get_init_args().run()
        VersionController.L.get_config_local_user_email_args(
            email="test@example.com"
        ).run()
        VersionController.L.get_config_local_user_name_args(name="Test User").run()

    with chdir(src_project_dir):
        # Create a clean environment dict without VIRTUAL_ENV to force
        # to create a new virtual environment instead of reusing the current one
        clean_env = os.environ.copy()
        clean_env.pop("VIRTUAL_ENV", None)

        args = PackageManager.L.get_init_project_args("--python", python_version)
        args.run(env=clean_env)

        # Add pyrig wheel as a dependency
        PackageManager.L.get_add_dependencies_args(wheel_path).run(env=clean_env)

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
        args = PackageManager.L.get_install_dependencies_args()
        args.run(env=clean_env)

        # Verify pyrig was installed correctly by running init also assert init passes
        args = PackageManager.L.get_run_args(*Pyrigger.L.get_cmd_args(cmd=init))
        res = args.run(env=clean_env)

        assert res.returncode == 0, f"Expected returncode 0, got {res.returncode}"

        # assert the pkgs own cli is available
        args = PackageManager.L.get_run_args(project_name, "--help")
        res = args.run(env=clean_env)
        stdout = res.stdout
        expected = project_name
        assert expected in stdout.lower(), (
            f"Expected {expected} in stdout, got {stdout}"
        )
        #  assert running the main command works
        args = PackageManager.L.get_run_args(project_name, main.__name__)
        res = args.run(env=clean_env)
        assert res.returncode == 0, f"Expected returncode 0, got {res.returncode}"

        # asert calling version works
        args = PackageManager.L.get_run_args(project_name, "version")
        res = args.run(env=clean_env)
        stdout = res.stdout
        expected = f"{project_name} version 0.1.0"
        assert expected in stdout, f"Expected {expected} in stdout, got {stdout}"

        # assert pyproject.toml contains not pyrig specific overrides
        pyproject_toml = tomlkit.parse((PyprojectConfigFile.L.get_path()).read_text())
        keywords = pyproject_toml.get("project", {}).get("keywords")
        assert keywords == []

    pkg_dir = src_project_dir / "src_project"
    assert pkg_dir.exists(), f"Expected {pkg_dir} to be created"
    assert (pkg_dir / "__init__.py").exists(), (
        f"Expected {pkg_dir / '__init__.py'} to be created"
    )

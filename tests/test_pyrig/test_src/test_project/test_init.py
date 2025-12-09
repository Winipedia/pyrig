"""Tests module."""

import logging
import os
import re
import shutil
from contextlib import chdir
from pathlib import Path

from pytest_mock import MockFixture

import pyrig
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.module import to_path
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.init import (
    commit_initial_changes,
    init,
    run_create_root,
    run_create_tests,
)
from pyrig.src.project.mgt import PROJECT_MGT, PROJECT_MGT_RUN_ARGS
from pyrig.src.testing.assertions import assert_with_msg

logger = logging.getLogger(__name__)


def test_run_create_root(mocker: MockFixture) -> None:
    """Test func for run_create_root."""
    # mock the real underlying subprocess.run from subprocess pkg
    mock_run = mocker.patch("subprocess.run")
    run_create_root()
    mock_run.assert_called_once()


def test_run_create_tests(mocker: MockFixture) -> None:
    """Test func for run_create_tests."""
    # mock the real underlying subprocess.run from subprocess pkg
    mock_run = mocker.patch("subprocess.run")
    run_create_tests()
    mock_run.assert_called_once()


def test_commit_initial_changes(mocker: MockFixture) -> None:
    """Test func for commit_initial_changes."""
    # mock the real underlying subprocess.run from subprocess pkg
    mock_run = mocker.patch("subprocess.run")
    commit_initial_changes()
    mock_run.assert_called_once()


def test_init(tmp_path: Path) -> None:
    """Test func for init."""
    # on Actions windows-latest temp path is on another drive so add path fails
    # so we use a tmp dir in the current dir
    # now test that in an empty folder with a pyproject.toml file
    # with a folder src that the setup works

    # copy the pyrig package to tmp_path/pyrig with shutil
    pyrig_temp_path = tmp_path / PyprojectConfigFile.get_project_name()
    shutil.copytree(
        to_path(pyrig.__name__, is_package=True).parent,
        pyrig_temp_path,
    )
    pyrig_temp_path = pyrig_temp_path.resolve()
    with chdir(pyrig_temp_path):
        # build the package
        run_subprocess([PROJECT_MGT, "build"])

    dist_files = list((pyrig_temp_path / "dist").glob("*.whl"))
    wheel_path = dist_files[-1].resolve().as_posix()

    src_project_dir = tmp_path / "src-project"
    src_project_dir.mkdir()

    # Get the current Python version in major.minor format
    python_version = str(PyprojectConfigFile.get_first_supported_python_version())

    # Initialize git repo in the test project directory
    with chdir(src_project_dir):
        run_subprocess(["git", "init"])
        run_subprocess(["git", "config", "user.email", "test@example.com"])
        run_subprocess(["git", "config", "user.name", "Test User"])

    with chdir(src_project_dir):
        # Create a clean environment dict without VIRTUAL_ENV to force
        # to create a new virtual environment instead of reusing the current one
        clean_env = os.environ.copy()
        clean_env.pop("VIRTUAL_ENV", None)

        run_subprocess(
            [PROJECT_MGT, "init", "--python", python_version],
            env=clean_env,
        )

        # Add pyrig wheel as a dependency
        run_subprocess(
            [
                "uv",
                "add",
                wheel_path,
            ],
            env=clean_env,
        )

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
        run_subprocess(["uv", "sync"], env=clean_env)

        # Verify pyrig was installed correctly
        project_name = PyprojectConfigFile.get_project_name_from_pkg_name(
            pyrig.__name__
        )

        run_subprocess(
            [*PROJECT_MGT_RUN_ARGS, project_name, init.__name__], env=clean_env
        )

        # test the cli can be called
        res = run_subprocess([*PROJECT_MGT_RUN_ARGS, project_name, "--help"])
        stdout = res.stdout.decode("utf-8")
        assert_with_msg(
            project_name in stdout,
            f"Expected {project_name} in stdout, got {stdout}",
        )
        # assert command is in stdout
        assert_with_msg(
            init.__name__ in stdout,
            f"Expected {init.__name__} in stdout, got {stdout}",
        )

        # assert the pkgs own cli is available
        res = run_subprocess(
            [*PROJECT_MGT_RUN_ARGS, "src-project", "--help"], check=False
        )
        stdout = res.stdout.decode("utf-8")
        expected = "src-project "
        assert_with_msg(
            expected in stdout.lower(),
            f"Expected {expected} in stdout, got {stdout}",
        )
        #  assert running the main command raises the NotImplementedError
        res = run_subprocess([*PROJECT_MGT_RUN_ARGS, "src-project"])

    pkg_dir = src_project_dir / "src_project"
    assert_with_msg(
        (pkg_dir / "__init__.py").exists(),
        f"Expected {pkg_dir / '__init__.py'} to be created",
    )

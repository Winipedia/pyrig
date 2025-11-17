"""Tests for py_dev.setup module."""

import os
import platform
import shutil
from contextlib import chdir
from pathlib import Path

import pytest

import py_dev
from py_dev import setup
from py_dev.dev.configs.pyproject import PyprojectConfigFile
from py_dev.utils.modules.module import to_path
from py_dev.utils.os.os import run_subprocess
from py_dev.utils.testing.assertions import assert_with_msg


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Test fails on Windows due to poetry add path fails",
)
def test_setup(tmp_path: Path) -> None:
    """Test func for _setup."""
    # on Actions windows-latest temp path is on another drive so poetry add path fails
    # so we use a tmp dir in the current dir
    # now test that in an empty folder with a pyproject.toml file
    # with a folder src that the setup works

    # copy the py_dev package to tmp_path/py_dev with shutil
    py_dev_temp_path = tmp_path / PyprojectConfigFile.get_project_name()
    shutil.copytree(
        to_path(py_dev.__name__, is_package=True).parent,
        py_dev_temp_path,
    )
    py_dev_temp_path = py_dev_temp_path.resolve()
    with chdir(py_dev_temp_path):
        # build the package
        run_subprocess(["poetry", "build"])

    dist_files = list((py_dev_temp_path / "dist").glob("*.whl"))
    wheel_path = dist_files[-1].as_posix()

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
        # Create a clean environment dict without VIRTUAL_ENV to force poetry
        # to create a new virtual environment instead of reusing the current one
        clean_env = os.environ.copy()
        clean_env.pop("VIRTUAL_ENV", None)

        run_subprocess(
            ["poetry", "init", "--no-interaction", f"--python=>={python_version}"],
            env=clean_env,
        )
        # Explicitly create a new virtual environment using the current Python
        run_subprocess(["poetry", "env", "use", python_version], env=clean_env)

        run_subprocess(
            [
                "poetry",
                "add",
                wheel_path,
            ],
            env=clean_env,
        )
        # Run setup via poetry run to ensure it uses the new virtual environment
        # with the editable install of the current state of py_dev
        setup.setup()

        # test the cli can be called
        res = run_subprocess(["poetry", "run", "py-dev", "--help"])
        stdout = res.stdout.decode("utf-8")
        assert_with_msg(
            "py-dev" in stdout,
            f"Expected py-dev in stdout, got {stdout}",
        )
        # assert setup command is in stdout
        assert_with_msg(
            "setup" in stdout,
            f"Expected setup in stdout, got {stdout}",
        )

    pkg_dir = src_project_dir / "src_project"
    assert_with_msg(
        (pkg_dir / "__init__.py").exists(),
        f"Expected {pkg_dir / '__init__.py'} to be created",
    )

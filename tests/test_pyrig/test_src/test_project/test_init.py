"""Tests module."""

import os
import platform
import shutil
from contextlib import chdir
from pathlib import Path

import pytest

import pyrig
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.module import to_path
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.init import init
from pyrig.src.testing.assertions import assert_with_msg


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Test fails on Windows due to poetry add path fails",
)
def test_init(tmp_path: Path) -> None:
    """Test func for init."""
    # on Actions windows-latest temp path is on another drive so poetry add path fails
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
        run_subprocess(["poetry", "build"])

    dist_files = list((pyrig_temp_path / "dist").glob("*.whl"))
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

        # Add pyrig wheel as a dependency
        run_subprocess(
            [
                "poetry",
                "add",
                wheel_path,
            ],
            env=clean_env,
        )

        # Verify pyrig was installed correctly
        project_name = PyprojectConfigFile.get_project_name_from_pkg_name(
            pyrig.__name__
        )

        run_subprocess(["poetry", "run", project_name, init.__name__], env=clean_env)

        # test the cli can be called
        res = run_subprocess(["poetry", "run", project_name, "--help"])
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
        res = run_subprocess(["poetry", "run", "src-project", "--help"], check=False)
        stdout = res.stdout.decode("utf-8")
        expected = "src-project "
        assert_with_msg(
            expected in stdout.lower(),
            f"Expected {expected} in stdout, got {stdout}",
        )
        #  assert running the main command raises the NotImplementedError
        res = run_subprocess(["poetry", "run", "src-project"], check=False)
        stderr = res.stderr.decode("utf-8")
        assert_with_msg(
            "NotImplementedError" in stderr,
            f"Expected NotImplementedError in stderr, got {stderr}",
        )

    pkg_dir = src_project_dir / "src_project"
    assert_with_msg(
        (pkg_dir / "__init__.py").exists(),
        f"Expected {pkg_dir / '__init__.py'} to be created",
    )

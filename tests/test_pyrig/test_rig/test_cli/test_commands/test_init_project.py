"""Tests module."""

import os
import re
import shutil
from contextlib import chdir
from pathlib import Path
from subprocess import CalledProcessError  # nosec: B404

import pytest
from pyrig_runtime.core.dependencies.discovery import dependency_ancestors
from pyrig_runtime.core.strings import snake_to_kebab_case
from pyrig_runtime.rig.cli.shared_subcommands import version
from pytest_mock import MockerFixture

import pyrig
from pyrig.rig.cli.commands.init_project import init_project
from pyrig.rig.cli.subcommands import init
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.testing.project import ProjectTester
from pyrig.rig.tools.version_control.controller import VersionController


def test_init_project_calls_pyrigger(mocker: MockerFixture) -> None:
    """This test exists only to get to 100% test coverage."""
    pyrigger_init_project_mock = mocker.patch.object(
        Pyrigger,
        Pyrigger.init_project.__name__,
    )
    init_project()
    pyrigger_init_project_mock.assert_called_once()


def test_init_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:  # noqa: PLR0915
    """Test function."""
    # on Actions windows-latest temp path is on another drive so add path fails
    # so we use a tmp dir in the current dir
    # now test that in an empty folder with a pyproject.toml file
    # with a folder src that the setup works

    # copy the pyrig package to tmp_path/pyrig with shutil
    project_name = "src-project"

    pyrig_tmp_path = tmp_path / PackageManager.I.project_name()
    shutil.copytree(
        Path(),
        pyrig_tmp_path,
    )
    with chdir(pyrig_tmp_path):
        # build the package
        args = PackageManager.I.build_args()
        args.run()

    dist_files = list((pyrig_tmp_path / "dist").glob("*.whl"))
    wheel_path = dist_files[-1].resolve().as_posix()

    src_project_dir = tmp_path / project_name
    src_project_dir.mkdir()

    # Get the current Python version in major.minor format
    python_version = str(PyprojectConfigFile.I.first_supported_python_version())

    with chdir(src_project_dir):
        # Strip VIRTUAL_ENV and the outer venv's bin dir from PATH so
        # subprocesses create a new virtual environment instead of reusing
        # the current one, and commands like `pyrig` from the dev environment
        # aren't found when testing that they're absent.
        venv = os.environ.get("VIRTUAL_ENV")
        monkeypatch.delenv("VIRTUAL_ENV", raising=False)
        if venv:
            path_entries = os.environ.get("PATH", "").split(os.pathsep)
            monkeypatch.setenv(
                "PATH",
                os.pathsep.join(
                    p for p in path_entries if not p.lower().startswith(venv.lower())
                ),
            )

        # Initialize git repo in the test project directory
        VersionController.I.init_args().run()
        VersionController.I.config_args(
            "--local",
            "user.email",
            "test@example.com",
        ).run()
        VersionController.I.config_args("--local", "user.name", "Test User").run()

        args = PackageManager.I.args("init", "--python", python_version)
        args.run()

        # Add pyrig wheel as a dev dependency and plugins
        plugins = tuple(
            snake_to_kebab_case(dep.__name__) for dep in dependency_ancestors(pyrig)
        )

        # add plugins
        PackageManager.I.add_dev_dependencies_args(wheel_path, *plugins).run()

        # uv add converts absolute paths to relative paths, which breaks when
        # the project is copied to a different location (e.g., in the
        # no_dev_deps_in_source_code fixture). We need to replace the
        # relative path with an absolute path.
        pyproject_toml = src_project_dir / "pyproject.toml"
        pyproject_content = pyproject_toml.read_text(encoding="utf-8")
        # Replace relative path with absolute path in tool.uv.sources
        # e.g., { path = "../pyrig/dist/..." }
        # -> { path = "/tmp/.../pyrig/dist/..." }
        pyproject_content = re.sub(
            r'pyrig = \{ path = "[^"]*" \}',
            f'pyrig = {{ path = "{wheel_path}" }}',
            pyproject_content,
        )
        pyproject_toml.write_text(pyproject_content, encoding="utf-8")

        # Sync to update the lock file with the new absolute path
        args = PackageManager.I.install_dependencies_args()
        args.run()

        # Verify pyrig was installed correctly
        # also checks if the init process works
        args = PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=init))
        res = args.run()
        assert res.returncode == 0

        # run tests with no cov
        args = PackageManager.I.run_args(*ProjectTester.I.test_args(), "--no-cov")
        res = args.run(check=False)
        assert res.returncode == pytest.ExitCode.NO_TESTS_COLLECTED

        # with cov
        args = PackageManager.I.run_args(*ProjectTester.I.test_args())
        res = args.run(check=False)
        assert res.returncode == pytest.ExitCode.TESTS_FAILED

        # assert the packages own cli is available
        args = PackageManager.I.run_args(project_name, "--help")
        res = args.run()
        stdout = res.stdout
        expected = project_name
        assert expected in stdout.lower(), (
            f"Expected {expected} in stdout, got {stdout}"
        )

        # assert calling version works
        args = PackageManager.I.run_args(project_name, version.__name__)
        res = args.run()
        assert res.returncode == 0
        stdout = res.stdout
        expected = f"{project_name} 0.1.0"
        assert expected in stdout

        package_dir = src_project_dir / "src" / "src_project"
        assert package_dir.exists()

        for cf in ConfigFile.concrete_subclasses():
            assert cf().path().exists()

        PackageManager.I.run_args(*Pyrigger.I.args("--help")).run()

        # rm all dev deps
        PackageManager.I.args(
            "remove",
            "--dev",
            *{*plugins, *Tool.subclasses_dev_dependencies()},
        ).run()
        PackageManager.I.args("sync").run()

        pyproject_content = pyproject_toml.read_text("utf-8")
        assert "pyrig-codecov" not in pyproject_content

        with pytest.raises(CalledProcessError):
            PackageManager.I.run_args(
                "--no-dev",
                "--no-sync",
                *Pyrigger.I.args("--help"),
            ).run()

        PackageManager.I.run_args(
            "--no-dev",
            "--no-sync",
            project_name,
            version.__name__,
        ).run()

"""Tests module."""

import os
import re
import shutil
from contextlib import chdir, suppress
from pathlib import Path

import pytest
from pyrig_runtime.core.strings import kebab_to_snake_case
from pyrig_runtime.rig.cli.shared_subcommands import version
from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.init_project import init_project
from pyrig.rig.cli.subcommands import init
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.packages.manager import PackageManager
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


def test_init_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run the steps behind `init_pyrig_project` and report success or failure.

    Extracted into a plain function, rather than inlined in the fixture, so
    tests can call it directly with mocked subprocess results to exercise
    each of its failure branches.
    """
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
        # remove a potential dist dir from a previous build
        dist_dir = pyrig_tmp_path / "dist"
        with suppress(FileNotFoundError):
            shutil.rmtree(dist_dir)
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

        # add plugins
        PackageManager.I.add_dev_dependencies_args(wheel_path).run()

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
        PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=init)).run()

        # with cov
        args = PackageManager.I.run_args(*ProjectTester.I.test_args())
        res = args.run(check=False)
        assert res.returncode == pytest.ExitCode.TESTS_FAILED

        # assert the packages own cli is available
        args = PackageManager.I.run_args(project_name, "--help")
        res = args.run()
        stdout = res.stdout
        expected = project_name
        assert expected in stdout.lower()

        # assert calling version works
        args = PackageManager.I.run_args(project_name, version.__name__)
        res = args.run()
        stdout = res.stdout
        expected = f"{project_name} 0.1.0"
        assert expected in stdout

        package_dir = src_project_dir / "src" / kebab_to_snake_case(project_name)
        assert package_dir.exists()

        PackageManager.I.run_args(*Pyrigger.I.args("--help")).run()

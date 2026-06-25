"""Tests module."""

import os
import re
import shutil
from contextlib import chdir
from pathlib import Path

import pytest
from pyrig_runtime.core.dependencies.graph import DependencyGraph
from pyrig_runtime.core.strings import snake_to_kebab_case
from pyrig_runtime.rig.cli.shared_subcommands import version
from pytest_mock import MockerFixture

import pyrig
from pyrig.rig.cli.commands.init_project import init_project
from pyrig.rig.cli.subcommands import init
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.testers.project import ProjectTester
from pyrig.rig.tools.version_control.version_controller import VersionController


def test_init_project_calls_pyrigger(mocker: MockerFixture) -> None:
    """This test exists only to get to 100% test coverage."""
    pyrigger_init_project_mock = mocker.patch.object(
        Pyrigger, Pyrigger.init_project.__name__
    )
    init_project()
    pyrigger_init_project_mock.assert_called_once()


def test_init_project(tmp_path: Path) -> None:  # noqa: PLR0915
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
        # Create a clean environment dict without VIRTUAL_ENV to force
        # to create a new virtual environment instead of reusing the current one
        clean_env = os.environ.copy()
        clean_env.pop("VIRTUAL_ENV", None)

        # Initialize git repo in the test project directory
        VersionController.I.init_args().run()
        VersionController.I.config_args(
            "--local", "user.email", "test@example.com"
        ).run()
        VersionController.I.config_args("--local", "user.name", "Test User").run()

        args = PackageManager.I.args("init", "--python", python_version)
        args.run(env=clean_env)

        # Add pyrig wheel as a dev dependency
        PackageManager.I.add_dev_dependencies_args(wheel_path).run(env=clean_env)

        # add plugins
        PackageManager.I.add_dev_dependencies_args(
            *(
                snake_to_kebab_case(dep)
                for dep in DependencyGraph(pyrig.__name__).sorted_ancestors(
                    pyrig.__name__
                )
            )
        ).run(env=clean_env)

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
        args.run(env=clean_env)

        # Verify pyrig was installed correctly
        # also checks if the init process works
        args = PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=init))
        res = args.run(env=clean_env)
        assert res.returncode == 0

        # run tests with no cov
        args = PackageManager.I.run_args(*ProjectTester.I.test_args(), "--no-cov")
        res = args.run(env=clean_env, check=False)
        assert res.returncode == pytest.ExitCode.NO_TESTS_COLLECTED

        # with cov
        args = PackageManager.I.run_args(*ProjectTester.I.test_args())
        res = args.run(env=clean_env, check=False)
        assert res.returncode == pytest.ExitCode.TESTS_FAILED

        # assert the packages own cli is available
        args = PackageManager.I.run_args(project_name, "--help")
        res = args.run(env=clean_env)
        stdout = res.stdout
        expected = project_name
        assert expected in stdout.lower(), (
            f"Expected {expected} in stdout, got {stdout}"
        )

        # assert calling version works
        args = PackageManager.I.run_args(project_name, version.__name__)
        res = args.run(env=clean_env)
        assert res.returncode == 0
        stdout = res.stdout
        expected = f"{project_name} 0.1.0"
        assert expected in stdout

        package_dir = src_project_dir / "src" / "src_project"
        assert package_dir.exists()

        for cf in ConfigFile.concrete_subclasses():
            assert cf().path().exists()

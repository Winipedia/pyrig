"""module."""

from contextlib import chdir
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args, run_subprocess_cached
from pyrig.rig.cli.subcommands import sync
from pyrig.rig.configs.docs.builder import DocsBuilderConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.version_control.controller import VersionController


class TestPyrigger:
    """Test class."""

    def test_runtime_dependency(self) -> None:
        """Test method."""
        assert Pyrigger.I.runtime_dependency() == "pyrig-runtime"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            Pyrigger.I.image_url()
            == "https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert Pyrigger.I.link_url() == "https://github.com/Winipedia/pyrig"

    def test_setup_steps(self) -> None:
        """Test that setup_steps returns a non-empty list of (Args, dict) pairs."""
        steps = Pyrigger.I.setup_steps()
        assert len(steps) > 0
        assert all(
            isinstance(step_args, Args) and isinstance(step_kwargs, dict)
            for step_args, step_kwargs in steps
        )

    def test_init_project(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test function."""
        run_subprocess_cached.cache_clear()
        with pytest.raises(
            RuntimeError,
            match="cannot initialize project that already has commits",
        ):
            Pyrigger.I.init_project()

        with chdir(tmp_path):
            run_mock = mocker.patch.object(Args, Args.run.__name__, return_value=None)
            has_commits_mock = mocker.patch.object(
                VersionController,
                VersionController.has_commits.__name__,
                return_value=False,
            )
            Pyrigger.I.init_project()
            has_commits_mock.assert_called_once()
            # assert was called as many times as there are steps in setup_steps
            assert run_mock.call_count == len(Pyrigger.I.setup_steps())

    def test_group(self) -> None:
        """Test method."""
        result = Pyrigger.I.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_name(self) -> None:
        """Test method."""
        result = Pyrigger.I.name()
        assert result == "pyrig"

    def test_cmd_args(self) -> None:
        """Test method."""

        def my_command() -> None:
            """Sample command."""

        result = Pyrigger.I.cmd_args("--help", cmd=my_command)
        assert result == ("pyrig", "my-command", "--help")

    def test_synchronize_project_hook(self) -> None:
        """Test method."""
        # syncing depends on dependencies already being installed
        hook = Pyrigger.I.synchronize_project_hook()
        install_hook = PackageManager.I.install_dependencies_hook()
        assert hook["priority"] > install_hook["priority"]
        audit_hook = PackageManager.I.audit_dependencies_hook()
        assert hook["priority"] > audit_hook["priority"]

    def test_synchronize_project(self) -> None:
        """Test method."""
        base_args = Pyrigger.I.cmd_args(cmd=sync)
        assert Pyrigger.I.synchronize_project() == PackageManager.I.run_args(*base_args)

    def test_hooks(self) -> None:
        """Test method."""
        assert Pyrigger.I.hooks() == (Pyrigger.I.synchronize_project_hook(),)

    def test_remove_config_files(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            PyprojectConfigFile.I.path().touch()
            assert PyprojectConfigFile.I.path().exists()
            Pyrigger.I.remove_config_files()
            assert PyprojectConfigFile.I.path().exists()

            DocsBuilderConfigFile.I.path().touch()
            assert DocsBuilderConfigFile.I.path().exists()
            Pyrigger.I.remove_config_files()
            assert not DocsBuilderConfigFile.I.path().exists()

    def test_runtime_dependencies(self) -> None:
        """Test method."""
        assert Pyrigger.I.runtime_dependencies() == [Pyrigger.I.runtime_dependency()]

    def test_setup_commit_msg(self) -> None:
        """Test method."""
        assert Pyrigger.I.setup_commit_msg() == "pyrig: Initialized project"

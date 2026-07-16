"""module."""

from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args
from pyrig.rig.cli.make import local
from pyrig.rig.cli.subcommands import sync
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger


class TestPyrigger:
    """Test class."""

    def test_runtime_dependency(self) -> None:
        """Test method."""
        assert Pyrigger.I.runtime_dependency() == "pyrig-runtime"

    def test_group_cmd_args(self) -> None:
        """Test method."""
        result = Pyrigger.I.group_cmd_args(group="mk", cmd=local)
        assert result == Args("pyrig", "mk", "local")

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
        assert isinstance(steps, list)
        assert len(steps) > 0
        assert all(
            isinstance(step_args, Args) and isinstance(step_kwargs, dict)
            for step_args, step_kwargs in steps
        )

    def test_init_project(self, mocker: MockerFixture) -> None:
        """Test function."""
        # mock the Args run method to prevent actual
        # execution of commands during testing
        run_mock = mocker.patch.object(Args, Args.run.__name__, return_value=None)
        Pyrigger.I.init_project()
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

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert Pyrigger.I.version_control_hooks() == (
            Pyrigger.I.synchronize_project_hook(),
        )

    def test_synchronize_project_hook(self) -> None:
        """Test method."""
        # syncing depends on dependencies already being installed
        hook = Pyrigger.I.synchronize_project_hook()
        install_hook = PackageManager.I.install_dependencies_hook()
        assert hook["priority"] > install_hook["priority"]
        assert hook["always_run"] is True
        assert hook["pass_filenames"] is False

    def test_synchronize_project(self) -> None:
        """Test method."""
        assert Pyrigger.I.synchronize_project() == Pyrigger.I.cmd_args(cmd=sync)

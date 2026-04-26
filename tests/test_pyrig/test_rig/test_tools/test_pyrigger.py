"""module."""

from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args
from pyrig.rig.tools import pyrigger
from pyrig.rig.tools.pyrigger import Pyrigger


class TestPyrigger:
    """Test class."""

    def test_setup_steps(self) -> None:
        """Test that setup_steps returns a non-empty list of callables."""
        steps = Pyrigger.I.setup_steps()
        assert isinstance(steps, tuple), f"Expected list, got {type(steps)}"
        assert len(steps) > 0, "Expected non-empty list of setup steps"
        assert all(callable(step) for step in steps), "All steps should be callable"

    def test_initializing_version_control(self) -> None:
        """Test function."""
        res = Pyrigger.I.initializing_version_control()
        assert isinstance(res, Args)

    def test_adding_dev_dependencies(self) -> None:
        """Test function."""
        res = Pyrigger.I.adding_dev_dependencies()
        assert isinstance(res, Args)

    def test_running_tests(self) -> None:
        """Test function."""
        res = Pyrigger.I.running_tests()
        assert isinstance(res, Args)

    def test_creating_project_root(self) -> None:
        """Test function."""
        # mock the real underlying subprocess.run from subprocess package
        res = Pyrigger.I.creating_project_root()
        assert isinstance(res, Args)

    def test_installing_dependencies(self) -> None:
        """Test function."""
        res = Pyrigger.I.installing_dependencies()
        assert isinstance(res, Args)

    def test_creating_test_files(self) -> None:
        """Test function."""
        res = Pyrigger.I.creating_test_files()
        assert isinstance(res, Args)

    def test_committing_initial_changes(self) -> None:
        """Test function."""
        res = Pyrigger.I.committing_initial_changes()
        assert isinstance(res, Args)

    def test_install_pre_commit_hooks(self) -> None:
        """Test function."""
        res = Pyrigger.I.install_pre_commit_hooks()
        assert isinstance(res, Args)

    def test_add_all_files_to_version_control(self) -> None:
        """Test function."""
        res = Pyrigger.I.add_all_files_to_version_control()
        assert isinstance(res, Args)

    def test_running_pre_commit_hooks(self) -> None:
        """Test function."""
        res = Pyrigger.I.running_pre_commit_hooks()
        assert isinstance(res, Args)

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

    def test_badge_urls(self) -> None:
        """Test method."""
        result = Pyrigger.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = Pyrigger.I.dev_dependencies()
        assert result == ("pyrig-dev",)

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


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        pyrigger.__doc__
        == """Wrapper around pyrig.

Provides a type-safe wrapper for pyrig commands and information.
"""
    )

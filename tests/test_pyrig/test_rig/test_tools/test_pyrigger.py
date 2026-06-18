"""module."""

from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args
from pyrig.rig.tools import pyrigger
from pyrig.rig.tools.pyrigger import Pyrigger


class TestPyrigger:
    """Test class."""

    def test_dev_dep_cmd_args(self) -> None:
        """Test method."""

        def some_cmd() -> None:
            """Does nothing."""

        assert Pyrigger.I.dev_dep_cmd_args(cmd=some_cmd) == Args(
            ("pyrig-dev", "some-cmd")
        )

    def test_dev_dep_args(self) -> None:
        """Test method."""
        assert Pyrigger.I.dev_dep_args("some", "args") == Args(
            ("pyrig-dev", "some", "args")
        )

    def test_dev_dep(self) -> None:
        """Test method."""
        assert Pyrigger.I.dev_dep() == "pyrig-dev"

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
        """Test that setup_steps returns a non-empty list of callables."""
        steps = Pyrigger.I.setup_steps()
        assert isinstance(steps, list)
        assert len(steps) > 0
        assert all(isinstance(step, Args) for step in steps)

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

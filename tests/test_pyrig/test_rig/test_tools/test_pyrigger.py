"""module."""

from pytest_mock import MockFixture

from pyrig.rig.tools import pyrigger
from pyrig.rig.tools.pyrigger import Pyrigger


class TestPyrigger:
    """Test class."""

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

    def test_cmd_args(self, mocker: MockFixture) -> None:
        """Test method."""
        # Mock the snake_to_kebab_case function
        mocker.patch(
            pyrigger.__name__ + ".snake_to_kebab_case",
            return_value="my-command",
        )

        def my_command() -> None:
            """Sample command."""

        result = Pyrigger.I.cmd_args("--help", cmd=my_command)
        assert result == ("pyrig", "my-command", "--help")

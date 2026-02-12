"""module."""

from pytest_mock import MockFixture

from pyrig.rig.tools import pyrigger
from pyrig.rig.tools.pyrigger import Pyrigger


class TestPyrigger:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = Pyrigger.L.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = Pyrigger.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = Pyrigger.L.dev_dependencies()
        assert isinstance(result, list), f"Expected list, got {type(result)}"

    def test_name(self) -> None:
        """Test method."""
        result = Pyrigger.L.name()
        assert result == "pyrig"

    def test_cmd_args(self, mocker: MockFixture) -> None:
        """Test method."""
        # Mock the project_name_from_pkg_name function
        mocker.patch(
            pyrigger.__name__ + ".project_name_from_pkg_name",
            return_value="my-command",
        )

        def my_command() -> None:
            """Sample command."""

        result = Pyrigger.L.cmd_args("--help", cmd=my_command)
        assert result == ("pyrig", "my-command", "--help")

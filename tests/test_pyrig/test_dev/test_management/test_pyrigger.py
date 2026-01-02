"""module."""

from pytest_mock import MockFixture

from pyrig.dev.management import pyrigger
from pyrig.dev.management.pyrigger import Pyrigger


class TestPyrigger:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = Pyrigger.name()
        assert result == "pyrig"

    def test_get_cmd_args(self, mocker: MockFixture) -> None:
        """Test method."""
        # Mock the get_project_name_from_pkg_name function
        mocker.patch(
            pyrigger.__name__ + ".get_project_name_from_pkg_name",
            return_value="my-command",
        )

        def my_command() -> None:
            """Sample command."""

        result = Pyrigger.get_cmd_args(my_command, "--help")
        assert result == ("pyrig", "my-command", "--help")

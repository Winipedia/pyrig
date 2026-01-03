"""module."""

from pytest_mock import MockFixture

from pyrig.dev.management import pyrigger
from pyrig.dev.management.pyrigger import Pyrigger


class TestPyrigger:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = Pyrigger.L.name()
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

        result = Pyrigger.L.get_cmd_args("--help", cmd=my_command)
        assert result == ("pyrig", "my-command", "--help")

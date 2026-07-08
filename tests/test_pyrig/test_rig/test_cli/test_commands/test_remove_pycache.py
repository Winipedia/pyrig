"""module."""

from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.remove_pycache import remove_pycache
from pyrig.rig.tools.programming_language import ProgrammingLanguage


def test_remove_pycache(mocker: MockerFixture) -> None:
    """Test function."""
    mock_remove_pycache = mocker.patch.object(
        ProgrammingLanguage, ProgrammingLanguage.remove_pycache.__name__
    )
    remove_pycache()
    mock_remove_pycache.assert_called_once()

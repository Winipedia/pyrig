"""Test module."""

from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.make.inits import make_project_init_files
from pyrig.rig.tools.programming_language import ProgrammingLanguage


def test_make_project_init_files(mocker: MockerFixture) -> None:
    """Test function."""
    mock_make_init_files = mocker.patch.object(
        ProgrammingLanguage,
        ProgrammingLanguage.make_init_files.__name__,
    )
    make_project_init_files()
    mock_make_init_files.assert_called_once_with()

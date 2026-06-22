"""Test module."""

from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.make.local import make_local_files
from pyrig.rig.configs.base.config_file import ConfigFile


def test_make_local_files(mocker: MockerFixture) -> None:
    """Test function."""
    config_file_mock = mocker.patch.object(
        ConfigFile,
        ConfigFile.version_control_ignored_subclasses.__name__,
        return_value=(),
    )

    make_local_files()

    config_file_mock.assert_called_once()

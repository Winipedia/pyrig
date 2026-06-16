"""test module."""

from pytest_mock import MockerFixture

from pyrig.rig.cli.commands import synchronize
from pyrig.rig.cli.commands.synchronize import synchronize_project


def test_synchronize_project(mocker: MockerFixture) -> None:
    """Test function."""
    make_init_files_mock = mocker.patch.object(synchronize, "make_init_files")
    config_file_mock = mocker.patch.object(synchronize, "ConfigFile")
    mirror_test_mock = mocker.patch.object(synchronize, "MirrorTestConfigFile")

    synchronize_project()

    make_init_files_mock.assert_called_once()
    config_file_mock.validate_all_subclasses.assert_called_once()
    mirror_test_mock.L.validate_all_subclasses.assert_called_once()

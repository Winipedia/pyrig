"""test module."""

from pytest_mock import MockerFixture

from pyrig.core.root import make_all_init_files
from pyrig.rig.cli.commands import synchronize
from pyrig.rig.cli.commands.synchronize import synchronize_project
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def test_synchronize_project(mocker: MockerFixture) -> None:
    """Test function."""
    make_init_files_mock = mocker.patch.object(
        synchronize, make_all_init_files.__name__
    )
    config_file_mock = mocker.patch.object(synchronize, ConfigFile.__name__)
    mirror_test_mock = mocker.patch.object(synchronize, MirrorTestConfigFile.__name__)

    synchronize_project()

    make_init_files_mock.assert_called_once()
    config_file_mock.validate_all_subclasses.assert_called_once()
    mirror_test_mock.L.validate_all_subclasses.assert_called_once()

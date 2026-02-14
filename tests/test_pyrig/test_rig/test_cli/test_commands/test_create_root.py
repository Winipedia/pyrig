"""Tests module."""

from pytest_mock import MockFixture

from pyrig.rig.cli.commands.create_root import (
    make_project_root,
)
from pyrig.rig.configs.base.base import ConfigFile


def test_make_project_root(mocker: MockFixture) -> None:
    """Test function."""
    num_config_file = ConfigFile.subclasses()
    mock = mocker.patch.object(
        ConfigFile, ConfigFile.validate.__name__, return_value=None
    )
    make_project_root()
    assert mock.call_count == len(num_config_file)

"""Tests for pyrig.src.projects.project module."""

from pytest_mock import MockFixture

from pyrig.dev.cli.commands.create_root import (
    make_project_root,
)
from pyrig.dev.configs.base.base import ConfigFile


def test_make_project_root(mocker: MockFixture) -> None:
    """Test func for _create_project_root."""
    num_config_file = ConfigFile.get_all_subclasses()
    mock = mocker.patch.object(ConfigFile, "__init__", return_value=None)
    make_project_root()
    assert mock.call_count == len(num_config_file)

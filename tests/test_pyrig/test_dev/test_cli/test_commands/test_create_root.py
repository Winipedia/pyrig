"""Tests for pyrig.src.projects.project module."""

from pytest_mock import MockFixture

from pyrig.dev.cli.commands.create_root import (
    get_ordered_config_files,
    get_priority_config_files,
    get_unordered_config_files,
    make_project_root,
)
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.src.modules.module import make_obj_importpath


def test_make_project_root() -> None:
    """Test func for _create_project_root."""
    make_project_root()


def test_init_all_config_files(mocker: MockFixture) -> None:
    """Test function."""
    mock = mocker.patch(make_obj_importpath(ConfigFile.__init__), return_value=None)
    make_project_root()
    mock.assert_called()


def test_init_config_files(mocker: MockFixture) -> None:
    """Test function."""
    mock = mocker.patch(make_obj_importpath(ConfigFile.__init__), return_value=None)
    make_project_root()
    mock.assert_called()


def test_get_priority_config_files() -> None:
    """Test function."""
    priority_config_files = get_priority_config_files()
    assert isinstance(priority_config_files, list)
    assert all(issubclass(cf, ConfigFile) for cf in priority_config_files)


def test_get_ordered_config_files() -> None:
    """Test function."""
    ordered_config_files = get_ordered_config_files()
    assert isinstance(ordered_config_files, list)
    assert all(issubclass(cf, ConfigFile) for cf in ordered_config_files)


def test_get_unordered_config_files() -> None:
    """Test function."""
    unordered_config_files = get_unordered_config_files()
    assert isinstance(unordered_config_files, list)
    assert all(issubclass(cf, ConfigFile) for cf in unordered_config_files)

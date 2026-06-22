"""test module."""

from pathlib import Path

import pytest
import typer
from pytest_mock import MockerFixture

from pyrig.core.root import make_all_init_files
from pyrig.rig.cli.commands import synchronize
from pyrig.rig.cli.commands.synchronize import synchronize_project
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def test_synchronize_project(mocker: MockerFixture) -> None:
    """Test function."""
    make_init_files_mock = mocker.patch.object(
        synchronize, make_all_init_files.__name__, return_value=()
    )
    config_file_mock = mocker.patch.object(
        ConfigFile, ConfigFile.validate_all_subclasses.__name__, return_value=()
    )

    synchronize_project()

    make_init_files_mock.assert_called_once()
    assert config_file_mock.call_count == len(
        (
            ConfigFile.validate_all_subclasses,
            MirrorTestConfigFile.validate_all_subclasses,
        )
    )

    make_init_files_mock.return_value = (Path(),)

    with pytest.raises(typer.Exit):
        synchronize_project()

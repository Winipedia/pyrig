"""test module."""

import pytest
import typer
from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.synchronize import (
    synchronize_project,
)
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def test_synchronize_project(mocker: MockerFixture) -> None:
    """Test function."""
    config_file_mock = mocker.patch.object(
        ConfigFile,
        ConfigFile.validate_concrete_subclasses.__name__,
        return_value=(),
    )

    synchronize_project([])

    assert config_file_mock.call_count == len(
        (
            ConfigFile.validate_concrete_subclasses,
            MirrorTestConfigFile.validate_concrete_subclasses,
        ),
    )

    config_file_mock.return_value = (PyprojectConfigFile,)

    with pytest.raises(typer.Exit):
        synchronize_project([])

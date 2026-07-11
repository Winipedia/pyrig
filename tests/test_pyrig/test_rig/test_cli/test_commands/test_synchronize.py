"""test module."""

from pathlib import Path

import pytest
import typer
from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.synchronize import (
    synchronize_project,
)
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.programming_language import ProgrammingLanguage


def test_synchronize_project(mocker: MockerFixture) -> None:
    """Test function."""
    make_init_files_mock = mocker.patch.object(
        ProgrammingLanguage,
        ProgrammingLanguage.make_init_files.__name__,
        return_value=(),
    )
    config_file_mock = mocker.patch.object(
        ConfigFile,
        ConfigFile.validate_concrete_subclasses.__name__,
        return_value=(),
    )

    synchronize_project()

    make_init_files_mock.assert_called_once()
    assert config_file_mock.call_count == len(
        (
            ConfigFile.validate_concrete_subclasses,
            MirrorTestConfigFile.validate_concrete_subclasses,
        ),
    )

    make_init_files_mock.return_value = (Path(),)

    with pytest.raises(typer.Exit):
        synchronize_project()

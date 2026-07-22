"""test module."""

from pathlib import Path

import pytest
import typer
from pytest_mock import MockerFixture

from pyrig.rig.cli.commands import synchronize
from pyrig.rig.cli.commands.synchronize import (
    synchronize_project,
    validate_config_files,
    validate_test_files,
)
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tests import mirror_test
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def test_synchronize_project(mocker: MockerFixture) -> None:
    """Test function."""
    config_file_mock = mocker.patch.object(
        synchronize,
        validate_config_files.__name__,
        return_value=(),
    )
    mirror_test_mock = mocker.patch.object(
        synchronize,
        validate_test_files.__name__,
        return_value=(),
    )

    synchronize_project([])

    config_file_mock.assert_called_once_with([])
    mirror_test_mock.assert_called_once_with([])

    config_file_mock.return_value = (PyprojectConfigFile,)

    with pytest.raises(typer.Exit):
        synchronize_project([])


def test_validate_config_files(mocker: MockerFixture) -> None:
    """Test function."""
    mocker.patch.object(
        ConfigFile,
        ConfigFile.validate_subclasses.__name__,
        side_effect=tuple,
    )

    all_subclasses = validate_config_files(None)
    assert set(all_subclasses) == set(ConfigFile.concrete_subclasses())

    target = PyprojectConfigFile.L
    one_subclass = validate_config_files([target().path()])
    assert set(one_subclass) == {target}

    assert validate_config_files([]) == ()


def test_validate_test_files(mocker: MockerFixture) -> None:
    """Test function."""
    mocker.patch.object(
        MirrorTestConfigFile,
        MirrorTestConfigFile.validate_subclasses.__name__,
        side_effect=tuple,
    )

    all_subclasses = validate_test_files(None)
    all_modules = {subclass().mirror_module() for subclass in all_subclasses}
    assert mirror_test in all_modules

    mirror_test_path = Path("src/pyrig/rig/tests/mirror_test.py")
    one_subclasses = validate_test_files([mirror_test_path])
    one_modules = {subclass().mirror_module() for subclass in one_subclasses}
    assert one_modules == {mirror_test}

    init_path = Path("src/pyrig/rig/tests/__init__.py")
    assert validate_test_files([init_path]) == ()

    outside_path = Path("pyproject.toml")
    assert validate_test_files([outside_path]) == ()

    non_python_path = Path("src/pyrig/py.typed")
    assert validate_test_files([non_python_path]) == ()

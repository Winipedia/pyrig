"""test module."""

from pathlib import Path

import pytest
import typer
from pytest_mock import MockerFixture

from pyrig.rig.cli.commands import synchronize
from pyrig.rig.cli.commands.synchronize import (
    synchronize_config_files,
    synchronize_project,
    synchronize_test_files,
    validate_config_files,
)
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tests import mirror_test


def test_synchronize_project(mocker: MockerFixture) -> None:
    """Test function."""
    config_file_mock = mocker.patch.object(
        synchronize,
        synchronize_config_files.__name__,
        return_value=(),
    )
    mirror_test_mock = mocker.patch.object(
        synchronize,
        synchronize_test_files.__name__,
        return_value=(),
    )

    synchronize_project([])

    config_file_mock.assert_called_once_with([])
    mirror_test_mock.assert_called_once_with([])

    config_file_mock.return_value = (PyprojectConfigFile,)

    with pytest.raises(typer.Exit):
        synchronize_project([])


def test_synchronize_config_files(mocker: MockerFixture) -> None:
    """Test function."""
    mocker.patch.object(
        synchronize,
        validate_config_files.__name__,
        side_effect=tuple,
    )

    all_subclasses = synchronize_config_files(None)
    all_subclasses_str_reprs = {str(cls.L) for cls in all_subclasses}
    concrete_leaves_str_reprs = {str(cls.L) for cls in ConfigFile.concrete_leaves()}
    assert all_subclasses_str_reprs == concrete_leaves_str_reprs

    target = PyprojectConfigFile.L
    one_subclass = synchronize_config_files([target().path()])
    assert set(one_subclass) == {target}

    assert synchronize_config_files([]) == ()


def test_synchronize_test_files(mocker: MockerFixture) -> None:
    """Test function."""
    mocker.patch.object(
        synchronize,
        validate_config_files.__name__,
        side_effect=tuple,
    )

    all_subclasses = synchronize_test_files(None)
    all_modules = {subclass().mirror_module() for subclass in all_subclasses}
    assert mirror_test in all_modules

    mirror_test_path = Path("src/pyrig/rig/tests/mirror_test.py")
    one_subclasses = synchronize_test_files([mirror_test_path])
    one_modules = {subclass().mirror_module() for subclass in one_subclasses}
    assert one_modules == {mirror_test}

    init_path = Path("src/pyrig/rig/tests/__init__.py")
    assert synchronize_test_files([init_path]) == ()

    outside_path = Path("pyproject.toml")
    assert synchronize_test_files([outside_path]) == ()

    non_python_path = Path("src/pyrig/py.typed")
    assert synchronize_test_files([non_python_path]) == ()

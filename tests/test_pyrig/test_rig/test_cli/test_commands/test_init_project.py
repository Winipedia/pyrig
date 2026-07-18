"""Tests module."""

from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.init_project import init_project
from pyrig.rig.tools.pyrigger import Pyrigger


def test_init_project_calls_pyrigger(mocker: MockerFixture) -> None:
    """This test exists only to get to 100% test coverage."""
    pyrigger_init_project_mock = mocker.patch.object(
        Pyrigger,
        Pyrigger.init_project.__name__,
    )
    init_project()
    pyrigger_init_project_mock.assert_called_once()


def test_init_project(init_pyrig_project: tuple[bool, str]) -> None:
    """Test function."""
    success, message = init_pyrig_project
    assert success, message

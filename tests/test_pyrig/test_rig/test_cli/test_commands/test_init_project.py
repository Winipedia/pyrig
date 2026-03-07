"""Tests module."""

from pytest_mock import MockFixture

from pyrig.rig.cli.commands.init_project import init_project
from pyrig.rig.tools.pyrigger import Pyrigger


def test_init_project(mocker: MockFixture) -> None:
    """Test function."""
    # patch the init_project method of Pyrigger to avoid side effects during testing
    init_mock = mocker.patch.object(
        Pyrigger, Pyrigger.init_project.__name__, return_value=None
    )
    init_project()
    init_mock.assert_called_once()

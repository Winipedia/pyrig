"""Tests module."""

from pytest_mock import MockerFixture

from pyrig.rig.cli.commands.make_tests import make_tests
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def test_make_tests(mocker: MockerFixture) -> None:
    """Test function."""
    mock_make_tests = mocker.patch.object(
        MirrorTestConfigFile, MirrorTestConfigFile.create_all_test_modules.__name__
    )
    make_tests()

    mock_make_tests.assert_called_once()

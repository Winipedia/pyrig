"""Tests module."""

from pytest_mock import MockFixture

from pyrig.rig.cli.commands.create_tests import create_tests
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile


def test_create_tests(mocker: MockFixture) -> None:
    """Test function."""
    mock_create_tests = mocker.patch.object(
        MirrorTestConfigFile, MirrorTestConfigFile.create_all_test_modules.__name__
    )
    create_tests()

    mock_create_tests.assert_called_once()

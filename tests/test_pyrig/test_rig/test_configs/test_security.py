"""module."""

from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.configs.security import SecurityConfigFile
from pyrig.rig.tools.version_control.controller import VersionController


class TestSecurityConfigFile:
    """Test class."""

    def test_is_correct(self) -> None:
        """Test method."""
        assert SecurityConfigFile.I.is_correct()

    def test_stem(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.stem()
        assert result == "SECURITY"

    def test_parent_path(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.parent_path()
        assert result == Path()

    def test_lines(self, mocker: MockerFixture) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="some.email@here.com",
        )
        result = SecurityConfigFile.I.lines()
        email_mock.assert_called_once()
        assert len(result) > 0
        assert any("some.email@here.com" in line for line in result)

    def test_template_with_contact_method(self, mocker: MockerFixture) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="some.email@here.com",
        )
        result = SecurityConfigFile.I.template_with_contact_method()
        email_mock.assert_called_once()
        assert len(result) > 0
        assert "<some.email@here.com>" in result

    def test_contact_method(self, mocker: MockerFixture) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="some.email@here.com",
        )
        result = SecurityConfigFile.I.contact_method()
        email_mock.assert_called_once()
        assert result == "<some.email@here.com>"

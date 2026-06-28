"""module."""

from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.configs.code_of_conduct import CodeOfConductConfigFile
from pyrig.rig.tools.version_control.version_controller import VersionController


class TestCodeOfConductConfigFile:
    """Test class."""

    def test_remote_code_of_conduct_template(
        self, *, on_linux_and_latest_python_version_or_not_in_ci: bool
    ) -> None:
        """Test method."""
        if not on_linux_and_latest_python_version_or_not_in_ci:
            return
        result = CodeOfConductConfigFile.I.remote_code_of_conduct_template()
        assert isinstance(result, str)
        assert "[INSERT CONTACT METHOD]" in result
        assert len(result) > 0
        assert (
            CodeOfConductConfigFile.I.local_code_of_conduct_template()
            == CodeOfConductConfigFile.I.remote_code_of_conduct_template()
        )

    def test_local_code_of_conduct_template(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.local_code_of_conduct_template()
        assert isinstance(result, str)
        assert len(result) > 0
        assert "[INSERT CONTACT METHOD]" in result

    def test_is_correct(self) -> None:
        """Test method."""
        assert CodeOfConductConfigFile.I.is_correct()

    def test_code_of_conduct(self, mocker: MockerFixture) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="some.email@here.com",
        )
        content = CodeOfConductConfigFile.I.code_of_conduct()
        email_mock.assert_called_once()
        assert "some.email@here.com" in content

    def test_contact_method(self, mocker: MockerFixture) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="some.email@here.com",
        )
        method = CodeOfConductConfigFile.I.contact_method()
        email_mock.assert_called_once()
        assert method == "<some.email@here.com>"

    def test_stem(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.stem()
        assert result == "CODE_OF_CONDUCT"

    def test_parent_path(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.parent_path()
        assert result == Path()

    def test_lines(self, mocker: MockerFixture) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="some.email@here.com",
        )
        lines = CodeOfConductConfigFile.I.lines()
        email_mock.assert_called_once()
        assert len(lines) > 1
        assert "<some.email@here.com>." in lines

    def test_code_of_conduct_template(self) -> None:
        """Test method."""
        result = CodeOfConductConfigFile.I.code_of_conduct_template()
        assert len(result) > 0

"""module."""

from pathlib import Path

import requests
from pytest_mock import MockerFixture

from pyrig.rig.configs.community.code_of_conduct import CodeOfConductConfigFile
from pyrig.rig.tools.version_control.controller import VersionController


class TestCodeOfConductConfigFile:
    """Test class."""

    def test_remote_code_of_conduct_template(
        self,
        *,
        on_linux_and_latest_python_version_or_not_in_ci: bool,
    ) -> None:
        """Test method."""
        if not on_linux_and_latest_python_version_or_not_in_ci:
            return
        code_of_conduct = requests.get(
            "https://raw.githubusercontent.com/github/MVG/main/org-docs/CODE-OF-CONDUCT.md",
            timeout=(3, 10),
        ).text
        assert isinstance(code_of_conduct, str)
        assert "[INSERT CONTACT METHOD]" in code_of_conduct
        assert len(code_of_conduct) > 0
        assert CodeOfConductConfigFile.I.code_of_conduct_template() == code_of_conduct

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

    def test_content(self, mocker: MockerFixture) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="some.email@here.com",
        )
        content = CodeOfConductConfigFile.I.content()
        email_mock.assert_called_once()
        assert len(content) > 1
        assert "<some.email@here.com>." in content

    def test_code_of_conduct_template(self) -> None:
        """Test method."""
        code_of_conduct = CodeOfConductConfigFile.I.code_of_conduct_template()
        assert isinstance(code_of_conduct, str)
        assert "[INSERT CONTACT METHOD]" in code_of_conduct
        assert len(code_of_conduct) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        assert CodeOfConductConfigFile.I.is_correct()

    def test_contact_method_placeholder(self) -> None:
        """Test method."""
        assert (
            CodeOfConductConfigFile.I.contact_method_placeholder()
            == "[INSERT CONTACT METHOD]"
        )

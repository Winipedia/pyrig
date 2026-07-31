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

        def normalized(text: str) -> str:
            return " ".join(text.split())

        repo = "EthicalSource/contributor_covenant"
        version_url = f"https://api.github.com/repos/{repo}/contents/content/version"
        majors = requests.get(f"{version_url}?ref=release", timeout=(3, 10)).json()
        latest_major = max(int(entry["name"]) for entry in majors)
        minors = requests.get(
            f"{version_url}/{latest_major}?ref=release",
            timeout=(3, 10),
        ).json()
        latest_minor = max(int(entry["name"]) for entry in minors)
        template_url = (
            f"https://raw.githubusercontent.com/{repo}/release/content/version/"
            f"{latest_major}/{latest_minor}/code_of_conduct.md"
        )
        remote_template = requests.get(template_url, timeout=(3, 10)).text
        _, _, remote_template = remote_template.split("+++", 2)

        local_template = CodeOfConductConfigFile.I.code_of_conduct_template()
        assert isinstance(local_template, str)
        assert len(local_template) > 0
        assert normalized(
            CodeOfConductConfigFile.I.reporting_placeholder(),
        ) in normalized(remote_template)
        assert normalized(
            CodeOfConductConfigFile.I.enforcement_placeholder(),
        ) in normalized(remote_template)
        assert normalized(remote_template) == normalized(local_template)

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

    def test_reporting_method(self, mocker: MockerFixture) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="some.email@here.com",
        )
        method = CodeOfConductConfigFile.I.reporting_method()
        email_mock.assert_called_once()
        assert method == "send an email to <some.email@here.com>."

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
        assert CodeOfConductConfigFile.I.reporting_placeholder() not in content
        assert CodeOfConductConfigFile.I.enforcement_placeholder() not in content

    def test_code_of_conduct_template(self) -> None:
        """Test method."""
        code_of_conduct = CodeOfConductConfigFile.I.code_of_conduct_template()
        assert isinstance(code_of_conduct, str)
        assert "[NOTE: describe your means of reporting here.]" in code_of_conduct
        assert len(code_of_conduct) > 0

    def test_is_correct(self) -> None:
        """Test method."""
        assert CodeOfConductConfigFile.I.is_correct()

    def test_reporting_placeholder(self) -> None:
        """Test method."""
        assert (
            CodeOfConductConfigFile.I.reporting_placeholder()
            == "[NOTE: describe your means of reporting here.]"
        )

    def test_enforcement_method(self) -> None:
        """Test method."""
        assert CodeOfConductConfigFile.I.enforcement_method() == ""

    def test_enforcement_placeholder(self) -> None:
        """Test method."""
        assert (
            CodeOfConductConfigFile.I.enforcement_placeholder()
            == """
**[NOTE: The remedies and repairs outlined below are suggestions based on best
practices in code of conduct enforcement. If your community has its own
established enforcement process, be sure to edit this section to describe your
own policies.]**
"""
        )

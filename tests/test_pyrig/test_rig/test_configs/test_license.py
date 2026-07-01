"""module."""

from pathlib import Path

import requests
from pytest_mock import MockerFixture

from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class TestLicenseConfigFile:
    """Test class."""

    def test_priority(self) -> None:
        """Test method."""
        assert LicenseConfigFile.I.priority() > PyprojectConfigFile.I.priority()

    def test_spdx_identifier(self, mocker: MockerFixture) -> None:
        """Test method."""
        assert LicenseConfigFile.I.spdx_identifier() == "MIT"

        read_content_mock = mocker.patch.object(
            LicenseConfigFile, "read_content", return_value="Not a valid license text."
        )
        assert LicenseConfigFile.I.spdx_identifier() == "LicenseRef-Custom"
        read_content_mock.assert_called_once()

    def test_remote_license_template(
        self, *, on_linux_and_latest_python_version_or_not_in_ci: bool
    ) -> None:
        """Test method."""
        if not on_linux_and_latest_python_version_or_not_in_ci:
            return
        mit_license = requests.get(
            "https://api.github.com/licenses/mit",
            timeout=(3, 10),
        ).json()["body"]
        assert "MIT License" in mit_license
        assert "[year]" in mit_license
        assert "[fullname]" in mit_license
        assert LicenseConfigFile.I.license_template() == mit_license

    def test_extension_separator(self) -> None:
        """Test method."""
        assert LicenseConfigFile.I.extension_separator() == ""

    def test_license_badge_url(self) -> None:
        """Test method."""
        result = LicenseConfigFile.I.license_badge_url()
        assert result == "https://img.shields.io/github/license/Winipedia/pyrig"

    def test_license_badge(self) -> None:
        """Test method."""
        result = LicenseConfigFile.I.license_badge()
        assert (
            result
            == "[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)"
        )

    def test_is_correct(self) -> None:
        """Test method."""
        assert LicenseConfigFile.I.is_correct()

    def test_license_template(self) -> None:
        """Test method."""
        mit_license = LicenseConfigFile.I.license_template()
        assert "MIT License" in mit_license
        assert "[year]" in mit_license
        assert "[fullname]" in mit_license

    def test_license(self) -> None:
        """Test method."""
        mit_license = LicenseConfigFile.I.license()
        assert "MIT License" in mit_license
        assert "Winipedia" in mit_license

        assert "[year]" not in mit_license
        assert "[fullname]" not in mit_license

    def test_stem(self) -> None:
        """Test method."""
        # Should return LICENSE
        assert LicenseConfigFile.I.stem() == "LICENSE", "Expected 'LICENSE'"

    def test_parent_path(self) -> None:
        """Test method."""
        # Should return Path()
        assert LicenseConfigFile.I.parent_path() == Path(), "Expected Path()"

    def test_extension(self) -> None:
        """Test method."""
        # Should return empty string
        assert LicenseConfigFile.I.extension() == "", "Expected ''"

    def test_lines(self) -> None:
        """Test method."""
        # Should return empty string
        assert isinstance(LicenseConfigFile.I.lines(), list)

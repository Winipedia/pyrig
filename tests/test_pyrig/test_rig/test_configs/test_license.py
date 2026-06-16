"""module."""

from pathlib import Path

from pyrig.rig.configs.license import LicenseConfigFile


class TestLicenseConfigFile:
    """Test class."""

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

    def test_mit_license(self) -> None:
        """Test method."""
        mit_license = LicenseConfigFile.I.mit_license()
        assert "MIT License" in mit_license

    def test_mit_license_with_year_and_owner(self) -> None:
        """Test method."""
        mit_license = LicenseConfigFile.I.mit_license_with_year_and_owner()
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

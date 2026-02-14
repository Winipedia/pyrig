"""module."""

from pathlib import Path

from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class TestLicenseConfigFile:
    """Test class."""

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

    def test_priority(self) -> None:
        """Test method."""
        # assert is bigger than PyprojectConfigFile
        assert LicenseConfigFile.priority() > PyprojectConfigFile.I.priority()

    def test_is_correct(self) -> None:
        """Test method."""
        assert LicenseConfigFile.is_correct()

    def test_mit_license(self) -> None:
        """Test method."""
        mit_license = LicenseConfigFile.mit_license()
        assert "MIT License" in mit_license

    def test_mit_license_with_year_and_owner(self) -> None:
        """Test method."""
        mit_license = LicenseConfigFile.mit_license_with_year_and_owner()
        assert "MIT License" in mit_license
        assert "Winipedia" in mit_license

        assert "[year]" not in mit_license
        assert "[fullname]" not in mit_license

    def test_filename(self) -> None:
        """Test method."""
        # Should return LICENSE
        assert LicenseConfigFile.filename() == "LICENSE", "Expected 'LICENSE'"

    def test_path(self) -> None:
        """Test method."""
        # Should return Path("LICENSE")
        assert LicenseConfigFile.path() == Path("LICENSE"), "Expected Path('LICENSE')"

    def test_parent_path(self) -> None:
        """Test method."""
        # Should return Path()
        assert LicenseConfigFile.parent_path() == Path(), "Expected Path()"

    def test_extension(self) -> None:
        """Test method."""
        # Should return empty string
        assert LicenseConfigFile.extension() == "", "Expected ''"

    def test_lines(self) -> None:
        """Test method."""
        # Should return empty string
        assert isinstance(LicenseConfigFile.lines(), list)

"""module."""

from pathlib import Path

from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class TestLicenseConfigFile:
    """Test class."""

    def test_get_license_badge_url(self) -> None:
        """Test method."""
        result = LicenseConfigFile.L.get_license_badge_url()
        assert result == "https://img.shields.io/github/license/Winipedia/pyrig"

    def test_get_license_badge(self) -> None:
        """Test method."""
        result = LicenseConfigFile.L.get_license_badge()
        assert (
            result
            == "[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)"
        )

    def test_get_priority(self) -> None:
        """Test method."""
        # assert is bigger than PyprojectConfigFile
        assert LicenseConfigFile.get_priority() > PyprojectConfigFile.L.get_priority()

    def test_is_correct(self) -> None:
        """Test method."""
        assert LicenseConfigFile().is_correct()

    def test_get_mit_license(self) -> None:
        """Test method."""
        mit_license = LicenseConfigFile.get_mit_license()
        assert "MIT License" in mit_license

    def test_get_mit_license_with_year_and_owner(self) -> None:
        """Test method."""
        mit_license = LicenseConfigFile.get_mit_license_with_year_and_owner()
        assert "MIT License" in mit_license
        assert "Winipedia" in mit_license

        assert "[year]" not in mit_license
        assert "[fullname]" not in mit_license

    def test_get_filename(self) -> None:
        """Test method for get_filename."""
        # Should return LICENSE
        assert LicenseConfigFile.get_filename() == "LICENSE", "Expected 'LICENSE'"

    def test_get_path(self) -> None:
        """Test method for get_path."""
        # Should return Path("LICENSE")
        assert LicenseConfigFile.get_path() == Path("LICENSE"), (
            "Expected Path('LICENSE')"
        )

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # Should return Path()
        assert LicenseConfigFile.get_parent_path() == Path(), "Expected Path()"

    def test_get_file_extension(self) -> None:
        """Test method for get_file_extension."""
        # Should return empty string
        assert LicenseConfigFile.get_file_extension() == "", "Expected ''"

    def test_get_lines(self) -> None:
        """Test method for get_content_str."""
        # Should return empty string
        assert isinstance(LicenseConfigFile.get_lines(), list)

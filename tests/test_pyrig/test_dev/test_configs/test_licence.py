"""module."""

from pathlib import Path

from pyrig.dev.configs.licence import LicenceConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class TestLicenceConfigFile:
    """Test class."""

    def test_get_priority(self) -> None:
        """Test method."""
        # assert is bigger than PyprojectConfigFile
        assert LicenceConfigFile.get_priority() > PyprojectConfigFile.L.get_priority()

    def test_is_correct(self) -> None:
        """Test method."""
        assert LicenceConfigFile().is_correct()

    def test_get_mit_license(self) -> None:
        """Test method."""
        mit_license = LicenceConfigFile.get_mit_license()
        assert "MIT License" in mit_license

    def test_get_mit_license_with_year_and_owner(self) -> None:
        """Test method."""
        mit_license = LicenceConfigFile.get_mit_license_with_year_and_owner()
        assert "MIT License" in mit_license
        assert "Winipedia" in mit_license

        assert "[year]" not in mit_license
        assert "[fullname]" not in mit_license

    def test_get_filename(self) -> None:
        """Test method for get_filename."""
        # Should return LICENSE
        assert LicenceConfigFile.get_filename() == "LICENSE", "Expected 'LICENSE'"

    def test_get_path(self) -> None:
        """Test method for get_path."""
        # Should return Path("LICENSE")
        assert LicenceConfigFile.get_path() == Path("LICENSE"), (
            "Expected Path('LICENSE')"
        )

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # Should return Path()
        assert LicenceConfigFile.get_parent_path() == Path(), "Expected Path()"

    def test_get_file_extension(self) -> None:
        """Test method for get_file_extension."""
        # Should return empty string
        assert LicenceConfigFile.get_file_extension() == "", "Expected ''"

    def test_get_lines(self) -> None:
        """Test method for get_content_str."""
        # Should return empty string
        assert isinstance(LicenceConfigFile.get_lines(), list)

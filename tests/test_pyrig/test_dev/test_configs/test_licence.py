"""module."""

from pathlib import Path

from pyrig.dev.configs.licence import LicenceConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestLicenceConfigFile:
    """Test class for LicenceConfigFile."""

    def test_get_filename(self) -> None:
        """Test method for get_filename."""
        # Should return LICENSE
        assert_with_msg(
            LicenceConfigFile.get_filename() == "LICENSE",
            "Expected 'LICENSE'",
        )

    def test_get_path(self) -> None:
        """Test method for get_path."""
        # Should return Path("LICENSE")
        assert_with_msg(
            LicenceConfigFile.get_path() == Path("LICENSE"),
            "Expected Path('LICENSE')",
        )

    def test_get_parent_path(self) -> None:
        """Test method for get_parent_path."""
        # Should return Path()
        assert_with_msg(
            LicenceConfigFile.get_parent_path() == Path(),
            "Expected Path()",
        )

    def test_get_file_extension(self) -> None:
        """Test method for get_file_extension."""
        # Should return empty string
        assert_with_msg(
            LicenceConfigFile.get_file_extension() == "",
            "Expected ''",
        )

    def test_get_content_str(self) -> None:
        """Test method for get_content_str."""
        # Should return empty string
        assert_with_msg(
            LicenceConfigFile.get_content_str() == "",
            "Expected ''",
        )

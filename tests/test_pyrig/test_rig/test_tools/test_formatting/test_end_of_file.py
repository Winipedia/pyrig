"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter


class TestEndOfFileFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = EndOfFileFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            EndOfFileFormatter.I.image_url()
            == "https://img.shields.io/badge/EOF-end--of--file--fixer-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            EndOfFileFormatter.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = EndOfFileFormatter.I.name()
        assert result == "end-of-file-fixer"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = EndOfFileFormatter.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_types(self) -> None:
        """Test method."""
        assert EndOfFileFormatter.I.types() == ["text"]

    def test_format_args(self) -> None:
        """Test method."""
        result = EndOfFileFormatter.I.format_args()
        assert result == ("end-of-file-fixer",)

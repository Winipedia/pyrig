"""module."""

from pyrig.rig.tools.formatting.trailing_whitespace import TrailingWhitespaceFormatter


class TestTrailingWhitespaceFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = TrailingWhitespaceFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            TrailingWhitespaceFormatter.I.image_url()
            == "https://img.shields.io/badge/whitespace-trailing--whitespace--fixer-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            TrailingWhitespaceFormatter.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = TrailingWhitespaceFormatter.I.name()
        assert result == "trailing-whitespace-fixer"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = TrailingWhitespaceFormatter.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_types(self) -> None:
        """Test method."""
        assert TrailingWhitespaceFormatter.I.types() == ["text"]

    def test_format_args(self) -> None:
        """Test method."""
        result = TrailingWhitespaceFormatter.I.format_args()
        assert result == ("trailing-whitespace-fixer",)

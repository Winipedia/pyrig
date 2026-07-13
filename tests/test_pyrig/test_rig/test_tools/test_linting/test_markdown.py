"""module."""

from pyrig.rig.tools.linting.markdown import MarkdownLinter


class TestMarkdownLinter:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            MarkdownLinter.I.image_url()
            == "https://img.shields.io/badge/markdown-rumdl-darkgreen"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.link_url() == "https://github.com/rvben/rumdl"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.version_control_ignore_paths() == (".rumdl_cache/",)

    def test_extension(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.extension() == "md"

    def test_regex(self) -> None:
        """Test method."""
        assert MarkdownLinter.I.regex() == r"\.md$"

    def test_group(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.name()
        assert result == "rumdl"

    def test_check_args(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.check_args()
        assert result == ("rumdl", "check")

    def test_check_fix_args(self) -> None:
        """Test method."""
        result = MarkdownLinter.I.check_fix_args()
        assert result == ("rumdl", "check", "--fix")

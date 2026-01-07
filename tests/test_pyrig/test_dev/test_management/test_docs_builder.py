"""module."""

from pyrig.dev.management.docs_builder import DocsBuilder


class TestDocsBuilder:
    """Test class."""

    def test_get_docs_dir(self) -> None:
        """Test method."""
        result = DocsBuilder.L.get_docs_dir()
        assert result == "docs"

    def test_name(self) -> None:
        """Test method."""
        result = DocsBuilder.L.name()
        assert result == "mkdocs"

    def test_get_build_args(self) -> None:
        """Test method."""
        result = DocsBuilder.L.get_build_args()
        assert result == ("mkdocs", "build")

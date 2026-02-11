"""module."""

from pathlib import Path

from pyrig.rig.tools.docs_builder import DocsBuilder


class TestDocsBuilder:
    """Test class."""

    def test_get_badge_group(self) -> None:
        """Test method."""
        result = DocsBuilder.L.get_badge_group()
        assert isinstance(result, str)
        assert result == "documentation"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = DocsBuilder.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_get_dev_dependencies(self) -> None:
        """Test method."""
        result = DocsBuilder.L.get_dev_dependencies()
        assert result == [
            "mkdocs",
            "mkdocs-material",
            "mkdocs-mermaid2-plugin",
            "mkdocstrings[python]",
        ]

    def test_get_docs_dir(self) -> None:
        """Test method."""
        result = DocsBuilder.L.get_docs_dir()
        assert result == Path("docs")

    def test_name(self) -> None:
        """Test method."""
        result = DocsBuilder.L.name()
        assert result == "mkdocs"

    def test_get_build_args(self) -> None:
        """Test method."""
        result = DocsBuilder.L.get_build_args()
        assert result == ("mkdocs", "build")

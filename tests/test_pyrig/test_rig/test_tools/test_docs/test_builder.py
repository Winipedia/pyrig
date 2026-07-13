"""module."""

from pathlib import Path

from pyrig.rig.tools.docs.builder import DocsBuilder


class TestDocsBuilder:
    """Test class."""

    def test_site_dir(self) -> None:
        """Test method."""
        result = DocsBuilder.I.site_dir()
        assert result == Path("site")

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            DocsBuilder.I.image_url()
            == "https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert DocsBuilder.I.link_url() == "https://Winipedia.github.io/pyrig"

    def test_version_control_ignore_paths(self) -> None:
        """Test method."""
        assert DocsBuilder.I.version_control_ignore_paths() == ("/site",)

    def test_documentation_url(self) -> None:
        """Test method."""
        result = DocsBuilder.I.documentation_url()
        assert isinstance(result, str)
        assert result.startswith("https://")
        assert "github.io" in result

    def test_group(self) -> None:
        """Test method."""
        result = DocsBuilder.I.group()
        assert isinstance(result, str)
        assert result == "project-info"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = DocsBuilder.I.dev_dependencies()
        assert result == (
            "mkdocs",
            "mkdocs-material",
            "mkdocs-mermaid2-plugin",
            "mkdocstrings[python]",
        )

    def test_docs_dir(self) -> None:
        """Test method."""
        result = DocsBuilder.I.docs_dir()
        assert result == Path("docs")

    def test_name(self) -> None:
        """Test method."""
        result = DocsBuilder.I.name()
        assert result == "mkdocs"

    def test_build_args(self) -> None:
        """Test method."""
        result = DocsBuilder.I.build_args()
        assert result == ("mkdocs", "build")

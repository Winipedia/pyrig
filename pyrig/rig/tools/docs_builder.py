"""MkDocs documentation builder wrapper.

Provides type-safe wrapper for MkDocs commands: build.
MkDocs is a static site generator for project documentation.

Example:
    >>> from pyrig.rig.tools.docs_builder import DocsBuilder
    >>> DocsBuilder.L.build_args().run()
"""

from pathlib import Path

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.rig.tools.version_controller import VersionController
from pyrig.src.processes import Args
from pyrig.src.string_ import make_linked_badge_markdown


class DocsBuilder(Tool):
    """MkDocs documentation builder wrapper.

    Constructs mkdocs command arguments for documentation building operations.

    Operations:
        - Building: Build static documentation site

    Example:
        >>> DocsBuilder.L.build_args().run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'mkdocs'
        """
        return "mkdocs"

    @classmethod
    def group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.DOCUMENTATION

    @classmethod
    def badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        return (
            "https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white",
            "https://www.mkdocs.org",
        )

    @classmethod
    def dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        return [
            *super().dev_dependencies(),
            "mkdocs-material",
            "mkdocs-mermaid2-plugin",
            "mkdocstrings[python]",
        ]

    @classmethod
    def docs_dir(cls) -> Path:
        """Get the documentation directory.

        Returns:
            Path to the documentation directory.
        """
        return Path("docs")

    @classmethod
    def build_args(cls, *args: str) -> Args:
        """Construct mkdocs build arguments.

        Args:
            *args: Build command arguments.

        Returns:
            Args for 'mkdocs build'.
        """
        return cls.args("build", *args)

    @classmethod
    def documentation_url(cls) -> str:
        """Construct GitHub Pages URL.

        Returns:
            URL in format: `https://{owner}.github.io/{repo}`

        Note:
            Site may not exist if GitHub Pages not enabled.
        """
        owner, repo = VersionController.L.repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://{owner}.github.io/{repo}"

    @classmethod
    def documentation_badge(cls) -> str:
        """Returns the badge for a markdown file.

        Shows github pages for github.
        """
        return make_linked_badge_markdown(
            badge_url="https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white",
            link_url=cls.documentation_url(),
            alt_text="Documentation",
        )

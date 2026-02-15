"""MkDocs documentation builder wrapper.

Provides type-safe wrapper for MkDocs commands: build.
MkDocs is a static site generator for project documentation.

Example:
    >>> from pyrig.rig.tools.docs_builder import DocsBuilder
    >>> DocsBuilder.I.build_args().run()
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
        >>> DocsBuilder.I.build_args().run()
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'mkdocs'
        """
        return "mkdocs"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.DOCUMENTATION`
        """
        return ToolGroup.DOCUMENTATION

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge and link URLs.

        Returns:
            Tuple containing badge image URL and tool homepage URL.
        """
        return (
            "https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white",
            "https://www.mkdocs.org",
        )

    def dev_dependencies(self) -> list[str]:
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

    def docs_dir(self) -> Path:
        """Get the documentation directory.

        Returns:
            Path to the documentation directory.
        """
        return Path("docs")

    def build_args(self, *args: str) -> Args:
        """Construct mkdocs build arguments.

        Args:
            *args: Build command arguments.

        Returns:
            Args for 'mkdocs build'.
        """
        return self.args("build", *args)

    def documentation_url(self) -> str:
        """Construct GitHub Pages URL.

        Returns:
            URL in format: `https://{owner}.github.io/{repo}`

        Note:
            Site may not exist if GitHub Pages not enabled.
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://{owner}.github.io/{repo}"

    def documentation_badge(self) -> str:
        """Construct a GitHub Pages documentation badge in Markdown.

        Returns:
            Markdown string with a linked badge pointing to the project's
            GitHub Pages URL (see `documentation_url`).
        """
        return make_linked_badge_markdown(
            badge_url="https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white",
            link_url=self.documentation_url(),
            alt_text="Documentation",
        )

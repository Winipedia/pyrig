"""Documentation builder tool wrapper.

Wraps DocsBuilder commands and information.
"""

from pathlib import Path

from pyrig.core.strings import make_linked_badge_markdown
from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup
from pyrig.rig.tools.version_controller import VersionController


class DocsBuilder(Tool):
    """MkDocs documentation builder tool wrapper.

    Provides methods for constructing mkdocs command arguments and
    generating documentation-related URLs and badges for GitHub Pages.

    Example:
        >>> DocsBuilder.I.build_args().run()
    """

    def name(self) -> str:
        """Get the tool command name.

        Returns:
            ``'mkdocs'``
        """
        return "mkdocs"

    def group(self) -> str:
        """Get the badge group for this tool.

        Returns:
            ``ToolGroup.DOCUMENTATION`` for grouping in generated badge lists.
        """
        return ToolGroup.DOCUMENTATION

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and target link URL for MkDocs.

        Returns:
            Tuple of ``(badge_image_url, link_url)`` where ``badge_image_url``
            is the shields.io badge and ``link_url`` points to mkdocs.org.
        """
        return (
            "https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white",
            "https://www.mkdocs.org",
        )

    def dev_dependencies(self) -> tuple[str, ...]:
        """Get the development dependencies required for MkDocs documentation.

        Extends the base ``Tool`` dependency (``'mkdocs'``) with additional
        packages for the Material theme, Mermaid diagram support, and
        Python API docstring rendering.

        Returns:
            Tuple of ``'mkdocs'``, ``'mkdocs-material'``,
            ``'mkdocs-mermaid2-plugin'``, and ``'mkdocstrings[python]'``.
        """
        return (
            *super().dev_dependencies(),
            "mkdocs-material",
            "mkdocs-mermaid2-plugin",
            "mkdocstrings[python]",
        )

    def docs_dir(self) -> Path:
        """Get the documentation source directory.

        Returns:
            ``Path('docs')`` — the standard MkDocs source directory,
            relative to the project root.
        """
        return Path("docs")

    def build_args(self, *args: str) -> Args:
        """Construct arguments for the ``mkdocs build`` command.

        Args:
            *args: Additional arguments appended after ``build``.

        Returns:
            Args representing ``['mkdocs', 'build', *args]``.
        """
        return self.args("build", *args)

    def documentation_badge(self) -> str:
        """Construct a GitHub Pages documentation badge in Markdown.

        Generates a shields.io badge labelled "Docs - GitHub Pages" that
        links to the project's GitHub Pages URL derived from the git remote.

        Returns:
            Markdown string in the form
            ``[![Documentation](badge_url)](documentation_url)``.
        """
        return make_linked_badge_markdown(
            badge_url="https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white",
            link_url=self.documentation_url(),
            alt_text="Documentation",
        )

    def documentation_url(self) -> str:
        """Construct the expected GitHub Pages URL for this project.

        Reads the repository owner and name from the git remote URL and
        composes the standard GitHub Pages URL. Both owner and name are
        URL-encoded for safe use in the URL. Does not verify that the remote
        is configured or that GitHub Pages is enabled.

        Returns:
            URL in the form ``https://{owner}.github.io/{repo}``.
        """
        owner, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False,
            url_encode=True,
        )
        return f"https://{owner}.github.io/{repo}"

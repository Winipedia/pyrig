"""MkDocs documentation builder wrapper.

Provides type-safe wrapper for MkDocs commands: build.
MkDocs is a static site generator for project documentation.

Example:
    >>> from pyrig.rig.tools.docs_builder import DocsBuilder
    >>> DocsBuilder.L.get_build_args().run()
"""

from pathlib import Path

from pyrig.rig.tools.base.base import Tool
from pyrig.src.processes import Args


class DocsBuilder(Tool):
    """MkDocs documentation builder wrapper.

    Constructs mkdocs command arguments for documentation building operations.

    Operations:
        - Building: Build static documentation site

    Example:
        >>> DocsBuilder.L.get_build_args().run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'mkdocs'
        """
        return "mkdocs"

    @classmethod
    def get_badge_group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return "documentation"

    @classmethod
    def get_badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        return (
            "https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white",
            "https://www.mkdocs.org",
        )

    @classmethod
    def get_dev_dependencies(cls) -> list[str]:
        """Get tool dependencies.

        Returns:
            List of tool dependencies.
        """
        return [
            *super().get_dev_dependencies(),
            "mkdocs-material",
            "mkdocs-mermaid2-plugin",
            "mkdocstrings[python]",
        ]

    @classmethod
    def get_docs_dir(cls) -> Path:
        """Get the documentation directory.

        Returns:
            Path to the documentation directory.
        """
        return Path("docs")

    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        """Construct mkdocs build arguments.

        Args:
            *args: Build command arguments.

        Returns:
            Args for 'mkdocs build'.
        """
        return cls.get_args("build", *args)

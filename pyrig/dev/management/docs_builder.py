"""MkDocs documentation builder wrapper.

Provides type-safe wrapper for MkDocs commands: build, serve, deploy.
MkDocs is a static site generator for project documentation.

Example:
    >>> from pyrig.dev.management.docs_builder import DocsBuilder
    >>> DocsBuilder.L.get_build_args().run()
    >>> DocsBuilder.L.get_serve_args().run()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class DocsBuilder(Tool):
    """MkDocs documentation builder wrapper.

    Constructs mkdocs command arguments for documentation building operations.

    Operations:
        - Building: Build static documentation site
        - Serving: Local development server
        - Deploying: Deploy to GitHub Pages

    Example:
        >>> DocsBuilder.L.get_build_args().run()
        >>> DocsBuilder.L.get_serve_args().run()
        >>> DocsBuilder.L.get_gh_deploy_args().run()
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'mkdocs'
        """
        return "mkdocs"

    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        """Construct mkdocs build arguments.

        Args:
            *args: Build command arguments.

        Returns:
            Args for 'mkdocs build'.
        """
        return cls.get_args("build", *args)

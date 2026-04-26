"""Ruff-based Python linter and formatter tool wrapper."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup


class Linter(Tool):
    """Type-safe wrapper for the Ruff Python linter and formatter.

    Ruff is a fast Python linter and formatter written in Rust.
    This class constructs command-line arguments for ruff's check,
    auto-fix, and format operations.

    Example:
        >>> Linter.I.check_fix_args().run()
        >>> Linter.I.format_args().run()
    """

    def name(self) -> str:
        """Return the tool command name.

        Returns:
            'ruff'
        """
        return "ruff"

    def group(self) -> str:
        """Return the badge group this tool belongs to.

        Returns:
            `ToolGroup.CODE_QUALITY`
        """
        return ToolGroup.CODE_QUALITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and project link URL for Ruff.

        Returns:
            A tuple of ``(badge_image_url, project_url)``.
        """
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json",
            "https://github.com/astral-sh/ruff",
        )

    def pydocstyle(self) -> str:
        """Return the docstring convention enforced by Ruff.

        The returned value is used in two places to keep both tools
        in sync with each other:

        - ``pyproject.toml`` — sets ``[tool.ruff.lint.pydocstyle] convention``
          so Ruff validates docstrings against this style.
        - ``mkdocs.yml`` — sets ``mkdocstrings`` ``docstring_style`` so the
          docs renderer parses docstrings with the same convention.

        Returns:
            The docstring convention name: ``'google'``.
        """
        return "google"

    def check_fix_args(self, *args: str) -> Args:
        """Construct ruff check arguments with auto-fix enabled.

        Args:
            *args: Additional arguments forwarded to the check command.

        Returns:
            Args for ``ruff check --fix``.
        """
        return self.check_args("--fix", *args)

    def check_args(self, *args: str) -> Args:
        """Construct ruff check arguments.

        Args:
            *args: Additional arguments forwarded to the check command.

        Returns:
            Args for ``ruff check``.
        """
        return self.args("check", *args)

    def format_args(self, *args: str) -> Args:
        """Construct ruff format arguments.

        Args:
            *args: Additional arguments forwarded to the format command.

        Returns:
            Args for ``ruff format``.
        """
        return self.args("format", *args)

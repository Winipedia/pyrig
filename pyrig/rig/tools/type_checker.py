"""Ty type checker wrapper.

Provides type-safe wrapper for ty commands: check.
Ty is Astral's extremely fast Python type checker.

Example:
    >>> from pyrig.rig.tools.type_checker import TypeChecker
    >>> TypeChecker.I.check_args().run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class TypeChecker(Tool):
    """Ty type checker wrapper.

    Constructs ty command arguments for type checking operations.

    Operations:
        - Type checking: Verify type annotations and correctness

    Example:
        >>> TypeChecker.I.check_args().run()
        >>> TypeChecker.I.check_args("src/").run()
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'ty'
        """
        return "ty"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.CODE_QUALITY`
        """
        return ToolGroup.CODE_QUALITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge and linked page URLs."""
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json",
            "https://github.com/astral-sh/ty",
        )

    def check_args(self, *args: str) -> Args:
        """Construct ty check arguments.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'ty check'.
        """
        return self.args("check", *args)

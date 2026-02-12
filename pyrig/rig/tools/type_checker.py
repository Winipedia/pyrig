"""Ty type checker wrapper.

Provides type-safe wrapper for ty commands: check.
Ty is Astral's extremely fast Python type checker.

Example:
    >>> from pyrig.rig.tools.type_checker import TypeChecker
    >>> TypeChecker.L.get_check_args().run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class TypeChecker(Tool):
    """Ty type checker wrapper.

    Constructs ty command arguments for type checking operations.

    Operations:
        - Type checking: Verify type annotations and correctness

    Example:
        >>> TypeChecker.L.get_check_args().run()
        >>> TypeChecker.L.get_check_args("src/").run()
    """

    @classmethod
    def get_name(cls) -> str:
        """Get tool name.

        Returns:
            'ty'
        """
        return "ty"

    @classmethod
    def get_group(cls) -> str:
        """Returns the group the tools belongs to.

        E.g. testing, tool, code-quality etc...
        """
        return ToolGroup.CODE_QUALITY

    @classmethod
    def get_badge_urls(cls) -> tuple[str, str]:
        """Returns the badge and connected page."""
        return (
            "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json",
            "https://github.com/astral-sh/ty",
        )

    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        """Construct ty check arguments.

        Args:
            *args: Check command arguments.

        Returns:
            Args for 'ty check'.
        """
        return cls.get_args("check", *args)

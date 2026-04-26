"""Type checker wrapper.

Wraps TypeChecker commands and information.
"""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup


class TypeChecker(Tool):
    """Type-safe wrapper for the ty type checker.

    Constructs ``ty check`` command arguments for running static type checks.

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
        """Return the group the tool belongs to.

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
            *args: Additional arguments appended after ``ty check``.

        Returns:
            Args for 'ty check [args]'.
        """
        return self.args("check", *args)

"""Type checker wrapper.

Wraps TypeChecker commands and information.
"""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class TypeChecker(Tool):
    """Type-safe wrapper for the ty type checker.

    Constructs ``ty check`` command arguments for running static type checks.
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
            `Group.CODE_QUALITY`
        """
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for ty.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json"

    def link_url(self) -> str:
        """Return the project link URL for ty.

        Returns:
            The URL of the ty project page as a string.
        """
        return "https://github.com/astral-sh/ty"

    def check_args(self, *args: str) -> Args:
        """Construct ty check arguments.

        Args:
            *args: Additional arguments appended after ``ty check``.

        Returns:
            Args for 'ty check [args]'.
        """
        return self.args("check", *args)

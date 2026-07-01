"""Static type checker command construction and badge metadata."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class TypeChecker(Tool):
    """Type-safe wrapper for the `ty` static type checker."""

    def name(self) -> str:
        """Return `'ty'`."""
        return "ty"

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the badge image URL for `ty`."""
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json"

    def link_url(self) -> str:
        """Return the URL of the `ty` project page."""
        return "https://github.com/astral-sh/ty"

    def check_args(self, *args: str) -> Args:
        """Build the command for running `ty check`.

        Args:
            *args: Additional arguments appended after `check`.

        Returns:
            Args for `ty check [args]`.
        """
        return self.args("check", *args)

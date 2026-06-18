"""Wrapper around the dependency checker tool."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class DependencyChecker(Tool):
    """Wrapper around the dependency checker tool."""

    def name(self) -> str:
        """Get the tool name."""
        return "deptry"

    def group(self) -> str:
        """Get the tool group."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Get the badges image url."""
        return "https://img.shields.io/badge/dependencies-deptry-blue"

    def link_url(self) -> str:
        """Get the badges link url."""
        return "https://github.com/osprey-oss/deptry"

    def check_args(self, *args: str) -> Args:
        """Get the args to check deps."""
        return self.args(*args)

"""Detection of unused, missing, and transitive Python dependencies."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class DependencyChecker(Tool):
    """`deptry` command wrapper."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `deptry`."""
        return "https://img.shields.io/badge/dependencies-deptry-blue"

    def link_url(self) -> str:
        """Return the URL of the `deptry` project page."""
        return "https://github.com/osprey-oss/deptry"

    def name(self) -> str:
        """Return `"deptry"`."""
        return "deptry"

    def check_args(self, *args: str) -> Args:
        """Build the `deptry` command.

        Args:
            *args: Additional CLI flags for `deptry`.

        Returns:
            Args for running `deptry` with the given flags.
        """
        return self.args(*args)

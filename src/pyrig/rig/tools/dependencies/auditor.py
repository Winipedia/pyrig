"""Vulnerability scanning for installed Python dependencies."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class DependencyAuditor(Tool):
    """`pip-audit` command wrapper.

    Intentionally minimal so that downstream projects can subclass and
    override `check_args` to apply project-specific flags such as custom
    ignore lists or output formats.
    """

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `pip-audit`."""
        return f"https://img.shields.io/badge/security-{self.shield_name()}-blue?logo=python"

    def link_url(self) -> str:
        """Return the URL of the `pip-audit` project page."""
        return "https://github.com/pypa/pip-audit"

    def name(self) -> str:
        """Return `"pip-audit"`."""
        return "pip-audit"

    def check_args(self, *args: str) -> Args:
        """Build the `pip-audit` command.

        Args:
            *args: Additional CLI flags for `pip-audit`.

        Returns:
            Args for running `pip-audit` with the given flags.
        """
        return self.args(*args)

"""Dependency vulnerability auditor for Python packages.

Wraps the dependency auditor commands and information.
"""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Tool, ToolGroup


class DependencyAuditor(Tool):
    """pip-audit command wrapper.

    Constructs pip-audit command arguments for dependency vulnerability
    scanning. Intentionally minimal so that downstream projects can subclass
    and override ``audit_args`` to apply project-specific flags such as
    custom ignore lists or output formats.
    """

    def audit_args(self, *args: str) -> Args:
        """Build pip-audit command arguments.

        Args:
            *args: Additional pip-audit CLI flags passed through verbatim
                (e.g. ``"--format"``, ``"json"``).

        Returns:
            Args for ``pip-audit`` with the given flags appended.
        """
        return self.args(*args)

    def name(self) -> str:
        """Return the pip-audit executable name.

        Returns:
            ``"pip-audit"``
        """
        return "pip-audit"

    def group(self) -> str:
        """Return the tool group used for badge organisation."""
        return ToolGroup.SECURITY

    def image_url(self) -> str:
        """Return the badge image URL for pip-audit.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/badge/security-pip--audit-blue?logo=python"

    def link_url(self) -> str:
        """Return the link URL for pip-audit.

        Returns:
            The URL of the pip-audit project page as a string.
        """
        return "https://github.com/pypa/pip-audit"

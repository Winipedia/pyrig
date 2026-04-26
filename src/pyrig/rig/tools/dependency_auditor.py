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
        """Return the tool group used for badge organisation.

        Returns:
            ``"security"``
        """
        return ToolGroup.SECURITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the pip-audit badge image URL and project link URL.

        Returns:
            A tuple of ``(badge_image_url, project_url)`` where
            ``badge_image_url`` is the shields.io badge and
            ``project_url`` is the pip-audit GitHub page.
        """
        return (
            "https://img.shields.io/badge/security-pip--audit-blue?logo=python",
            "https://github.com/pypa/pip-audit",
        )

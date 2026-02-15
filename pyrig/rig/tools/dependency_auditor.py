"""Dependency vulnerability auditor wrapper.

Provides a type-safe wrapper for `pip-audit`, which checks installed Python
dependencies for known vulnerabilities.

This complements Bandit:
    - Bandit: scans *your code* for insecure patterns.
    - pip-audit: scans *your dependencies* for known CVEs/advisories.

Example:
    >>> from pyrig.rig.tools.dependency_auditor import DependencyAuditor
    >>> DependencyAuditor.I.audit_args().run()
"""

from pyrig.rig.tools.base.base import Tool, ToolGroup
from pyrig.src.processes import Args


class DependencyAuditor(Tool):
    """pip-audit wrapper.

    Constructs pip-audit command arguments.

    Note:
        This wrapper intentionally stays small. Teams often need to customize
        pip-audit flags (e.g., ignores/formatting) based on their policy.
        Subclass this tool in your downstream package and override
        ``audit_args`` to add flags.
    """

    def name(self) -> str:
        """Get tool name.

        Returns:
            'pip-audit'
        """
        return "pip-audit"

    def group(self) -> str:
        """Returns the group the tool belongs to.

        Returns:
            `ToolGroup.SECURITY`
        """
        return ToolGroup.SECURITY

    def badge_urls(self) -> tuple[str, str]:
        """Return the badge image URL and project page URL.

        Returns:
            Tuple containing badge image URL and project page URL.
        """
        return (
            "https://img.shields.io/badge/security-pip--audit-blue?logo=python",
            "https://github.com/pypa/pip-audit",
        )

    def audit_args(self, *args: str) -> Args:
        """Construct pip-audit arguments.

        Args:
            *args: Additional pip-audit CLI arguments.

        Returns:
            Args for 'pip-audit'.
        """
        return self.args(*args)

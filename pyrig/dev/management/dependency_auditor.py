"""Dependency vulnerability auditor wrapper.

Provides a type-safe wrapper for `pip-audit`, which checks installed Python
dependencies for known vulnerabilities.

This complements Bandit:
    - Bandit: scans *your code* for insecure patterns.
    - pip-audit: scans *your dependencies* for known CVEs/advisories.

Example:
    >>> from pyrig.dev.management.dependency_auditor import DependencyAuditor
    >>> DependencyAuditor.L.get_run_args().run()
"""

from pyrig.dev.management.base.base import Tool
from pyrig.src.processes import Args


class DependencyAuditor(Tool):
    """pip-audit wrapper.

    Constructs pip-audit command arguments.

    Note:
        This wrapper intentionally stays small. Teams often need to customize
        pip-audit flags (e.g., ignores/formatting) based on their policy.
        Subclass this tool in your downstream package and override
        ``get_run_args`` to add flags.
    """

    @classmethod
    def name(cls) -> str:
        """Get tool name.

        Returns:
            'pip-audit'
        """
        return "pip-audit"

    @classmethod
    def get_audit_args(cls, *args: str) -> Args:
        """Construct pip-audit arguments.

        Args:
            *args: Additional pip-audit CLI arguments.

        Returns:
            Args for 'pip-audit'.
        """
        return cls.get_args(*args)

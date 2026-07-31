"""Configuration management for SECURITY.md files.

Manages SECURITY.md using a minimal best-practices template. The template
covers vulnerability reporting guidelines and response expectations.
"""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class SecurityConfigFile(MarkdownConfigFile):
    """Configuration manager for the project's SECURITY.md file.

    Generates SECURITY.md from a minimal best-practices template that covers
    vulnerability reporting guidelines, the information to include in reports,
    and response expectations. The contact method embedded in the template
    is the project's maintainer email, as configured in `pyproject.toml`.
    """

    def content(self) -> str:
        """Return the security policy text with the contact method filled in."""
        return f"""# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities publicly.**

Instead, please report them privately to {self.contact_method()}.

Include:

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Any potential impact

## Response

The vulnerability will be investigated, and a fix will be released as soon as
reasonably possible.
"""

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return the filename stem `"SECURITY"`."""
        return "SECURITY"

    def contact_method(self) -> str:
        """Return the contact email address for security reports.

        Returns:
            The project's maintainer email wrapped in angle brackets, e.g.
            `<user@example.com>`.
        """
        return f"<{PyprojectConfigFile.I.maintainer_email()}>"

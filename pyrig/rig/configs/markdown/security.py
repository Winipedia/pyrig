"""Configuration management for SECURITY.md files.

Manages SECURITY.md using a minimal best practices template. The template
covers vulnerability reporting, response timeline, and supported versions.

See Also:
    pyrig.rig.configs.base.markdown.MarkdownConfigFile
"""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.version_controller import VersionController

SECURITY_TEMPLATE = """# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public issues.**

Instead, please report them via email to
[INSERT CONTACT METHOD].

Include:

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Any potential impact

## Response

We will:

1. Acknowledge your report as soon as possible
2. Investigate and keep you informed of progress
3. Credit you when the issue is fixed (unless you prefer anonymity)
"""


class SecurityConfigFile(MarkdownConfigFile):
    """SECURITY.md configuration manager.

    Generates SECURITY.md using a minimal best practices template that
    covers vulnerability reporting guidelines. Works for both private and
    public repositories.

    The template includes:
        - How to report vulnerabilities (email, not public issues)
        - What information to include in reports
        - Response timeline expectations

    Examples:
        Generate SECURITY.md::

            SecurityConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.base.markdown.MarkdownConfigFile
        pyrig.rig.configs.markdown.code_of_conduct.CodeOfConductConfigFile
    """

    def filename(self) -> str:
        """Get the SECURITY filename.

        Returns:
            str: "SECURITY" (extension added by parent).
        """
        return "SECURITY"

    def parent_path(self) -> Path:
        """Get the parent directory for SECURITY.md.

        Returns:
            Path: Project root.
        """
        return Path()

    def lines(self) -> list[str]:
        """Return the security policy as individual lines.

        Returns:
            list[str]: Security template lines with contact method inserted.
        """
        return [*self.template_with_contact_method().splitlines()]

    def is_correct(self) -> bool:
        """Check if SECURITY.md exists and is non-empty.

        Returns:
            bool: True if file exists with content, False otherwise.
        """
        return self.path().exists() and bool(
            self.path().read_text(encoding="utf-8").strip()
        )

    def template_with_contact_method(self) -> str:
        """Get the security template content with email inserted.

        Returns:
            str: Security template content with user's email.
        """
        contact_method = self.contact_method()
        return SECURITY_TEMPLATE.replace("[INSERT CONTACT METHOD]", contact_method)

    def contact_method(self) -> str:
        """Get the contact method for security reports.

        Returns:
            str: Email address from version control config (e.g. git).
        """
        return f"<{VersionController.I.email()}>"

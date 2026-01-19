"""Configuration management for SECURITY.md files.

Manages SECURITY.md using a minimal best practices template. The template
covers vulnerability reporting, response timeline, and supported versions.

See Also:
    pyrig.dev.configs.base.markdown.MarkdownConfigFile
"""

from pathlib import Path

from pyrig.dev.configs.base.markdown import MarkdownConfigFile
from pyrig.dev.management.version_controller import VersionController

SECURITY_TEMPLATE = """
# Security Policy

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
        - Supported versions table

    Examples:
        Generate SECURITY.md::

            SecurityConfigFile()

    See Also:
        pyrig.dev.configs.base.markdown.MarkdownConfigFile
        pyrig.dev.configs.markdown.code_of_conduct.CodeOfConductConfigFile
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the SECURITY filename.

        Returns:
            str: "SECURITY" (extension added by parent).
        """
        return "SECURITY"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for SECURITY.md.

        Returns:
            Path: Project root.
        """
        return Path()

    @classmethod
    def get_lines(cls) -> list[str]:
        """Get the security template content with email inserted.

        Returns:
            list[str]: Security template lines.
        """
        return [*cls.get_security_template_with_contact_method().splitlines(), ""]

    @classmethod
    def is_correct(cls) -> bool:
        """Check if SECURITY.md exists and is non-empty.

        Returns:
            bool: True if file exists with content, False otherwise.
        """
        return cls.get_path().exists() and bool(
            cls.get_path().read_text(encoding="utf-8").strip()
        )

    @classmethod
    def get_security_template_with_contact_method(cls) -> str:
        """Get the security template content with email inserted.

        Returns:
            str: Security template content with user's email.
        """
        contact_method = cls.get_contact_method()
        return SECURITY_TEMPLATE.replace("[INSERT CONTACT METHOD]", contact_method)

    @classmethod
    def get_contact_method(cls) -> str:
        """Get the contact method for security reports.

        Returns:
            str: The email in the version control, e.g. the email in git config
        """
        return f"<{VersionController.L.get_email()}>"

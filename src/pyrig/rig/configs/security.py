"""Configuration management for SECURITY.md files.

Manages SECURITY.md using a minimal best-practices template. The template
covers vulnerability reporting guidelines and response expectations.
"""

from pathlib import Path

from pyrig.core.strings import file_has_content
from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.version_control.version_controller import VersionController

SECURITY_TEMPLATE = """# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities publicly.**

Instead, please report them privately via email to
[INSERT CONTACT METHOD].

Include:

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Any potential impact

## Response

The vulnerability will be investigated, and a fix will be released as soon as
reasonably possible.
"""


class SecurityConfigFile(MarkdownConfigFile):
    """Configuration manager for the project's SECURITY.md file.

    Generates SECURITY.md from a minimal best-practices template that covers
    vulnerability reporting guidelines, the information to include in reports,
    and response expectations. The contact method placeholder in the template
    is populated from the configured git user email.

    Any non-empty SECURITY.md is treated as valid, so users are free to
    replace or extend the generated template with their own policy.
    """

    def is_correct(self) -> bool:
        """Return whether SECURITY.md has non-empty content.

        Returns:
            `True` if the file is non-empty; `False` if it is empty.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return file_has_content(self.path())

    def lines(self) -> list[str]:
        """Return the security policy template as a list of lines.

        Returns:
            Lines of the security policy template, with the contact method
            placeholder filled in.
        """
        return self.split_lines(self.template_with_contact_method())

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return the filename stem `"SECURITY"`."""
        return "SECURITY"

    def template_with_contact_method(self) -> str:
        """Return the security template with the contact placeholder replaced.

        Returns:
            Complete security policy template with the contact method
            filled in.
        """
        contact_method = self.contact_method()
        return SECURITY_TEMPLATE.replace("[INSERT CONTACT METHOD]", contact_method)

    def contact_method(self) -> str:
        """Return the contact email address for security reports.

        Returns:
            The configured git user email wrapped in angle brackets, e.g.
            `<user@example.com>`.
        """
        return f"<{VersionController.I.email()}>"

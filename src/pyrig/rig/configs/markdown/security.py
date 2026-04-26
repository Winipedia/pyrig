"""Configuration management for SECURITY.md files.

Manages SECURITY.md using a minimal best-practices template. The template
covers vulnerability reporting, response timeline, and supported versions.
"""

from pathlib import Path

from pyrig.core.strings import read_text_utf8
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
    """Configuration manager for the project's SECURITY.md file.

    Generates SECURITY.md from a minimal best-practices template that covers
    vulnerability reporting guidelines, the information to include in reports,
    and response expectations. The contact method placeholder in the template
    is populated from the configured git user email.

    Any non-empty SECURITY.md is treated as valid, so users can replace or
    extend the generated template with their own policy without triggering
    validation failures.

    Example:
        Generate or update SECURITY.md::

            SecurityConfigFile.I.validate()
    """

    def stem(self) -> str:
        """Return the filename stem ``"SECURITY"``."""
        return "SECURITY"

    def parent_path(self) -> Path:
        """Return the project root directory as the location for SECURITY.md.

        Returns:
            Path: Current working directory (project root).
        """
        return Path()

    def is_correct(self) -> bool:
        """Return whether SECURITY.md exists and contains non-empty content.

        Overrides the parent's content-subset validation with a simpler check.
        Any non-empty SECURITY.md is accepted as correct, allowing users to
        replace or extend the generated template with their own policy without
        triggering validation failures.

        Returns:
            bool: True if the file exists and its content is not blank.
        """
        return self.path().exists() and bool(read_text_utf8(self.path()).strip())

    def lines(self) -> list[str]:
        """Return the security policy template as a list of lines.

        Delegates to ``template_with_contact_method()`` to build the full
        template string, then splits it into lines for the parent class.

        Returns:
            list[str]: Lines of the security policy template with the git
                user email substituted as the contact method.
        """
        return self.split_lines(self.template_with_contact_method())

    def template_with_contact_method(self) -> str:
        """Return the security template with the contact placeholder replaced.

        Substitutes the ``[INSERT CONTACT METHOD]`` placeholder in
        ``SECURITY_TEMPLATE`` with the value returned by ``contact_method()``.

        Returns:
            str: Complete security policy template with the contact method
                filled in.
        """
        contact_method = self.contact_method()
        return SECURITY_TEMPLATE.replace("[INSERT CONTACT METHOD]", contact_method)

    def contact_method(self) -> str:
        """Return the contact email address for security reports.

        Reads the git ``user.email`` configuration and wraps it in angle
        brackets to form a standard email reference (e.g. ``<user@example.com>``).

        Returns:
            str: Git user email wrapped in angle brackets.
        """
        return f"<{VersionController.I.email()}>"

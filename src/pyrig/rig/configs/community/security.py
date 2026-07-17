"""Configuration management for SECURITY.md files.

Manages SECURITY.md using a minimal best-practices template. The template
covers vulnerability reporting guidelines and response expectations.
"""

from pathlib import Path

from pyrig.core.strings import file_has_content
from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.version_control.controller import VersionController

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

    def content(self) -> str:
        """Return the security policy template content.

        Returns:
            The security policy template, with the contact method
            placeholder filled in.
        """
        return f"""# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities publicly.**

Instead, please report them privately to
{self.contact_method()}

Include:

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Any potential impact

## Response

The vulnerability will be investigated, and a fix will be released as soon as
reasonably possible.
"""

    def is_correct(self) -> bool:
        """Check whether SECURITY.md has non-empty content.

        Overrides the default content-comparison check with a simpler
        non-emptiness test.

        Returns:
            `True` if the file has non-empty content; `False` if the file
            is empty.
        """
        return file_has_content(self.path())

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return the filename stem `"SECURITY"`."""
        return "SECURITY"

    def contact_method(self) -> str:
        """Return the contact email address for security reports.

        Returns:
            The configured git user email wrapped in angle brackets, e.g.
            `<user@example.com>`.
        """
        return f"<{VersionController.I.email()}>"

"""Configuration management for SECURITY.md files.

Manages SECURITY.md, the project's vulnerability-reporting policy.
"""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class SecurityConfigFile(MarkdownConfigFile):
    """Configuration manager for the project's SECURITY.md file.

    Generates SECURITY.md from a general-purpose coordinated-disclosure
    template covering: which versions are supported, how to report a
    vulnerability (by emailing the configured maintainer), what information
    to include, a minimal acknowledgment expectation, and a safe-harbor
    statement for good-faith security research. The reporting address is
    derived from project configuration, so downstream users do not need to
    fill it in by hand.
    """

    def content(self) -> str:
        """Return the complete security policy text.

        Returns:
            The supported-versions, reporting, expectations, and
            safe-harbor sections joined into a single Markdown document.
        """
        return f"""# Security Policy

{self.supported_versions_section()}

{self.reporting_section()}

{self.expectations_section()}

{self.safe_harbor_section()}
"""

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return the filename stem `"SECURITY"`."""
        return "SECURITY"

    def supported_versions_section(self) -> str:
        """Return the section stating which versions receive security fixes.

        Framed as prose rather than a version table, since pyrig-based
        projects use continuous single-branch versioning with no
        maintained-branch/backport policy to tabulate.

        Returns:
            The `## Supported Versions` section.
        """
        return """## Supported Versions

Only the latest released version receives security fixes. Please upgrade
before reporting, or mention your version if you can't."""

    def reporting_section(self) -> str:
        """Return the section describing where and how to report a vulnerability.

        Uses the configured maintainer email as the reporting channel. The
        "please include" list asks for more than the bare minimum, since it
        only guides the reporter and commits the maintainer to nothing. Also
        clarifies scope, since a vulnerability in a dependency isn't this
        project's to fix.

        Returns:
            The `## Reporting a Vulnerability` section.
        """
        return f"""## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub
issues, discussions, or pull requests.**

Instead, report a vulnerability to:
{self.reporting_method()}

Please include:

- A description of the vulnerability and its impact
- Steps to reproduce it
- The affected version(s)
- Any special configuration required to reproduce it
- Full paths of any source files related to the issue, if known
- Any relevant logs, screenshots, or proof-of-concept code

This covers vulnerabilities in this project's own code. For a dependency,
please report to that project directly."""

    def reporting_method(self) -> str:
        """Return the method used for reporting a vulnerability.

        Returns:
            The reporting method as a string.
        """
        return f"<{PyprojectConfigFile.I.maintainer_email()}>"

    def expectations_section(self) -> str:
        """Return the section describing what happens after a report is filed.

        Deliberately minimal and free of any concrete commitment — no
        response time, fix-by date, disclosure-timing coordination, or
        credit policy — since a generated default can't know what's
        sustainable for whoever ends up maintaining a given downstream
        project. A project that wants firmer guarantees can subclass and
        override this method.

        Returns:
            The `## What to Expect` section.
        """
        return """## What to Expect

- We will acknowledge your report as soon as possible.
- We will investigate and work on a fix."""

    def safe_harbor_section(self) -> str:
        """Return the safe-harbor statement for good-faith security research.

        Returns:
            The `## Safe Harbor` section.
        """
        return """## Safe Harbor

Security research conducted in good faith, following this policy, and
without harming users, data, or service availability, is authorized. We
will not pursue legal action for reports that comply with this policy."""

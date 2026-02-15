"""Configuration management for pull request template.

Manages .github/pull_request_template.md using a minimal template inspired by
React's PR template. Contains Summary and Testing sections only.

See Also:
    pyrig.rig.configs.base.markdown.MarkdownConfigFile
    https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
"""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile

PULL_REQUEST_TEMPLATE = """<!--
Please consider the following:

- Does this pull request include a summary of the change? (See below.)
- Does this pull request include a descriptive title?
- Does this pull request include references to any relevant issues?
-->
# Change Overview

## Summary

<!-- What's the purpose of the change? What does it do, and why? -->

## Testing

<!-- How was it tested? -->
"""


class PullRequestTemplateConfigFile(MarkdownConfigFile):
    """Pull request template configuration manager.

    Generates .github/pull_request_template.md using a minimal template
    inspired by React's PR template. Contains only two sections:

    - Summary: What changed and why
    - Testing: How the change was verified

    Examples:
        Generate pull_request_template.md::

            PullRequestTemplateConfigFile.I.validate()

    See Also:
        pyrig.rig.configs.base.markdown.MarkdownConfigFile
        https://github.com/facebook/react/blob/main/.github/PULL_REQUEST_TEMPLATE.md
    """

    def parent_path(self) -> Path:
        """Return `.github` as parent directory."""
        return Path(".github")

    def lines(self) -> list[str]:
    def lines(self) -> list[str]:
        Returns:
            Parent directory path.
        """Return the pull request template content as lines."""
        return [*PULL_REQUEST_TEMPLATE.strip().splitlines()]

    def is_correct(self) -> bool:
        """Check if pull_request_template.md exists and is non-empty.

        Returns:
            True if file exists with content, False otherwise.
    def is_correct(self) -> bool:
        return self.path().exists() and bool(
            self.path().read_text(encoding="utf-8").strip()
        )

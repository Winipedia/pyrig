"""Configuration for the GitHub pull request template."""

from pathlib import Path

from pyrig.core.strings import file_has_content
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
    """Configuration manager for `.github/pull_request_template.md`.

    Validation is intentionally permissive: the file is considered correct
    as soon as it has any content, so contributors can freely customize the
    generated template without it being overwritten on later validation.
    """

    def parent_path(self) -> Path:
        """Return the `.github` directory."""
        return Path(".github")

    def stem(self) -> str:
        """Return `"pull_request_template"` as the filename stem."""
        return "pull_request_template"

    def lines(self) -> list[str]:
        """Return the required starter template content as a list of lines."""
        return self.split_lines(PULL_REQUEST_TEMPLATE)

    def is_correct(self) -> bool:
        """Return whether the file has non-empty content.

        Returns:
            `True` if the file has non-empty content; `False` if the file
            is empty.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return file_has_content(self.path())

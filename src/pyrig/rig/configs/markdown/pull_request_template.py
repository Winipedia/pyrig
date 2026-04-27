"""Configuration for the GitHub pull request template.

Manages ``.github/pull_request_template.md``, providing a minimal starter
template that prompts contributors to summarize their change and describe
how it was tested.
"""

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
    """Configuration manager for the GitHub pull request template.

    Generates ``.github/pull_request_template.md`` with a concise starter
    template containing a Change Overview section with Summary and Testing
    subsections.

    The ``is_correct`` validation is intentionally permissive: it only checks
    that the file exists and contains non-empty content. This lets
    contributors freely customize the template after initial generation
    without triggering unwanted regeneration on subsequent ``validate`` calls.

    Example:
        >>> PullRequestTemplateConfigFile.I.validate()
    """

    def parent_path(self) -> Path:
        """Return the ``.github`` directory as the file's parent path."""
        return Path(".github")

    def stem(self) -> str:
        """Return ``"pull_request_template"`` as the filename stem."""
        return "pull_request_template"

    def lines(self) -> list[str]:
        """Return the pull request template as a list of lines."""
        return self.split_lines(PULL_REQUEST_TEMPLATE)

    def is_correct(self) -> bool:
        """Return whether the pull request template file has content.

        Overrides the parent's content-matching validation with a permissive
        check: the file is considered correct as long as it has non-empty
        content. This avoids overwriting user-customized templates on
        subsequent ``validate`` calls.

        Returns:
            ``True`` if the file has non-empty content; ``False`` if the
            file is empty.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return file_has_content(self.path())

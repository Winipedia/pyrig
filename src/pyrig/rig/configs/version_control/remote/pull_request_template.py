"""Configuration for the GitHub pull request template."""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class PullRequestTemplateConfigFile(MarkdownConfigFile):
    """Configuration manager for `.github/pull_request_template.md`.

    Seeds the file with a starter template that prompts contributors for a
    change summary and testing notes, alongside a pre-submission checklist.
    """

    def content(self) -> str:
        """Return the required starter template content."""
        return """<!--
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

    def parent_path(self) -> Path:
        """Return the `RemoteVersionController`'s config directory."""
        return RemoteVersionController.I.config_dir()

    def stem(self) -> str:
        """Return `"pull_request_template"` as the filename stem."""
        return "pull_request_template"

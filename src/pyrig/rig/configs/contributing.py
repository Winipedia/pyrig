"""Configuration management for CONTRIBUTING.md files.

Manages CONTRIBUTING.md using a minimal best-practices template covering
issue reporting and the pull request workflow.
"""

from pathlib import Path

from pyrig.core.strings import file_has_content
from pyrig.rig.configs.base.markdown import MarkdownConfigFile

CONTRIBUTING_TEMPLATE = """# Contributing

Contributions are welcome!

## Issues

Before opening an issue, please search existing ones to avoid duplicates.

Use issues for:

- **Ideas** — Suggest new features or improvements
- **Problems** — Report bugs with steps to reproduce
- **Questions** — Ask if something is unclear

## Pull Requests

1. Clone the repository
2. Create a branch (`git switch -c your-feature`)
3. Make your changes
4. Commit your changes with clear messages
5. Push your branch and open a pull request

### Guidelines

- Reference related issues in the PR description
- Keep changes focused and atomic
- Update documentation when behavior changes
- Match the existing code style
- All checks must pass before merge
"""


class ContributingConfigFile(MarkdownConfigFile):
    """Configuration manager for the project's CONTRIBUTING.md file.

    Generates CONTRIBUTING.md from a minimal best-practices template covering
    issue reporting and the pull request workflow. Users are free to
    customize the file after initial generation.
    """

    def is_correct(self) -> bool:
        """Return whether CONTRIBUTING.md has non-empty content.

        Any non-empty file at the expected path is considered correct, even
        if its content no longer matches the template, since the template is
        a starting point that users are expected to customize.

        Returns:
            `True` if the file has non-empty content; `False` if the file is
            empty.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return file_has_content(self.path())

    def content(self) -> str:
        """Return the contributing template content."""
        return CONTRIBUTING_TEMPLATE

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"CONTRIBUTING"` as the filename stem."""
        return "CONTRIBUTING"

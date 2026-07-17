"""Configuration management for CONTRIBUTING.md files.

Manages CONTRIBUTING.md using a minimal best-practices template covering
issue reporting and the pull request workflow.
"""

from pathlib import Path

from pyrig.rig.configs.base.markdown import MarkdownConfigFile


class ContributingConfigFile(MarkdownConfigFile):
    """Configuration manager for the project's CONTRIBUTING.md file.

    Generates CONTRIBUTING.md from a minimal best-practices template covering
    issue reporting and the pull request workflow. Users are free to
    customize the file after initial generation.
    """

    def content(self) -> str:
        """Return the contributing template content."""
        return """# Contributing

Contributions are welcome!

## Issues

Before opening an issue, please search existing ones to avoid duplicates.

Use issues for:

- **Ideas** — Suggest new features or improvements
- **Problems** — Report bugs with steps to reproduce
- **Questions** — Ask if something is unclear

## Pull Requests

1. Clone the repository
2. Create a branch
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

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `"CONTRIBUTING"` as the filename stem."""
        return "CONTRIBUTING"

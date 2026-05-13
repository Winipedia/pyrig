"""Configuration management for CONTRIBUTING.md files.

Provides a configuration file class for generating and managing CONTRIBUTING.md
with a minimal best practices contribution guide template.
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
2. Create a branch (`git checkout -b your-feature`)
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
    """Manages the CONTRIBUTING.md file for the project.

    Generates a standard contribution guide covering issue reporting and the
    pull request workflow. Suitable for both private and public repositories.
    Users may customize the file content after initial generation.

    Examples:
        Generate or validate CONTRIBUTING.md::

            ContributingConfigFile.I.validate()
    """

    def stem(self) -> str:
        """Return "CONTRIBUTING" as the filename stem."""
        return "CONTRIBUTING"

    def parent_path(self) -> Path:
        """Return project root as parent directory."""
        return Path()

    def lines(self) -> list[str]:
        """Return the contributing template content as lines."""
        return self.split_lines(CONTRIBUTING_TEMPLATE)

    def is_correct(self) -> bool:
        """Return whether CONTRIBUTING.md has non-empty content.

        Overrides the inherited line-matching validation so that user-modified
        content is still considered correct. Any non-empty file at the expected
        path passes, because the template is a starting point that projects are
        expected to customise.

        Returns:
            ``True`` if the file has non-empty content; ``False`` if the
            file is empty.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        return file_has_content(self.path())

"""Configuration management for CONTRIBUTING.md files.

Provides a configuration file class for generating and managing CONTRIBUTING.md
with a minimal best practices contribution guide template.
"""

from pathlib import Path

from pyrig.core.strings import read_text_utf8
from pyrig.rig.configs.base.markdown import MarkdownConfigFile

CONTRIBUTING_TEMPLATE = """# Contributing

Contributions are welcome! This document explains how to contribute.

## Issues

Issues help improve this project.

- **Ideas** - Suggest new features or improvements
- **Problems** - Report bugs with steps to reproduce
- **Questions** - Ask if something is unclear

Before opening an issue, please search existing ones to avoid duplicates.

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes with clear messages
4. Push to your fork
5. Open a pull request

### Guidelines

- Reference related issues in your PR
- Keep changes focused and atomic
- Update documentation if needed
- Follow existing code style
- Ensure tests pass

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.
"""


class ContributingConfigFile(MarkdownConfigFile):
    """Manages the CONTRIBUTING.md file for the project.

    Generates a standard contribution guide covering issue reporting, pull
    request workflow, and code of conduct reference. Suitable for both private
    and public repositories. Users may customize the file content after initial
    generation.

    Examples:
        Generate or validate CONTRIBUTING.md::

            ContributingConfigFile.I.validate()
    """

    def stem(self) -> str:
        """Return "CONTRIBUTING" as the filename."""
        return "CONTRIBUTING"

    def parent_path(self) -> Path:
        """Return project root as parent directory."""
        return Path()

    def lines(self) -> list[str]:
        """Return the contributing template content as lines."""
        return self.split_lines(CONTRIBUTING_TEMPLATE)

    def is_correct(self) -> bool:
        """Check whether CONTRIBUTING.md exists and contains non-empty content.

        Overrides the inherited line-matching validation so that user-modified
        content is still considered correct. Any non-empty file at the expected
        path passes, because the template is a starting point that projects are
        expected to customise.

        Returns:
            True if the file exists and contains non-empty content, False otherwise.
        """
        return self.path().exists() and bool(read_text_utf8(self.path()).strip())

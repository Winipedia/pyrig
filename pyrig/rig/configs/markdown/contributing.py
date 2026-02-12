"""Configuration management for CONTRIBUTING.md files.

Manages CONTRIBUTING.md using a minimal best practices template. The template
covers essential contribution guidelines: issues, pull requests, and code of
conduct reference.

See Also:
    pyrig.rig.configs.base.markdown.MarkdownConfigFile
"""

from pathlib import Path

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
    """CONTRIBUTING.md configuration manager.

    Generates CONTRIBUTING.md using a minimal best practices template that
    covers essential contribution guidelines. Works for both private and
    public repositories.

    The template includes:
        - How to open issues (ideas, problems, questions)
        - Pull request workflow (fork, branch, commit, PR)
        - PR guidelines (reference issues, atomic changes, tests)
        - Code of Conduct reference

    Examples:
        Generate CONTRIBUTING.md::

            ContributingConfigFile()

    See Also:
        pyrig.rig.configs.base.markdown.MarkdownConfigFile
        pyrig.rig.configs.markdown.code_of_conduct.CodeOfConductConfigFile
    """

    @classmethod
    def filename(cls) -> str:
        """Get the CONTRIBUTING filename.

        Returns:
            str: "CONTRIBUTING" (extension added by parent).
        """
        return "CONTRIBUTING"

    @classmethod
    def parent_path(cls) -> Path:
        """Get the parent directory for CONTRIBUTING.md.

        Returns:
            Path: Project root.
        """
        return Path()

    @classmethod
    def get_lines(cls) -> list[str]:
        """Get the contributing template content.

        Returns:
            list[str]: Contributing template lines.
        """
        return [*CONTRIBUTING_TEMPLATE.splitlines()]

    @classmethod
    def is_correct(cls) -> bool:
        """Check if CONTRIBUTING.md exists and is non-empty.

        Returns:
            bool: True if file exists with content, False otherwise.
        """
        return cls.path().exists() and bool(
            cls.path().read_text(encoding="utf-8").strip()
        )

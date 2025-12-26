"""Configuration management for pre-commit hooks.

This module provides the PreCommitConfigConfigFile class for managing the
.pre-commit-config.yaml file, which configures Git pre-commit hooks to run
automated code quality checks before each commit.

The generated configuration uses local hooks (not remote repositories) to run:
    - **ruff**: Fast Python linter and formatter (check + format)
    - **ty**: Type checker for Python code
    - **bandit**: Security vulnerability scanner
    - **rumdl**: Markdown linter for documentation

All hooks run on every commit (always_run=True) and use the system-installed
versions of the tools, ensuring consistency with the project's development
environment.

See Also:
    pre-commit framework: https://pre-commit.com/
    ruff: https://docs.astral.sh/ruff/
    bandit: https://bandit.readthedocs.io/
"""

import logging
from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.yaml import YamlConfigFile
from pyrig.src.management.base.base import (
    Args,
)

logger = logging.getLogger(__name__)


class PreCommitConfigConfigFile(YamlConfigFile):
    """Configuration file manager for .pre-commit-config.yaml.

    Generates a .pre-commit-config.yaml file that configures local Git hooks
    to run code quality checks before each commit. The hooks use system-installed
    tools rather than remote repositories, ensuring they match the project's
    development environment.

    Configured Hooks:
        - **lint-code**: Runs `ruff check --fix` to lint and auto-fix issues
        - **format-code**: Runs `ruff format` to format code
        - **check-types**: Runs `ty check` for type checking
        - **check-security**: Runs `bandit` to scan for security issues
        - **check-markdown**: Runs `rumdl check` to lint markdown files

    All hooks are configured with:
        - language: system (uses installed tools)
        - always_run: true (runs on every commit)
        - pass_filenames: false (tools handle file discovery)

    Examples:
        Generate .pre-commit-config.yaml::

            from pyrig.dev.configs.git.pre_commit import PreCommitConfigConfigFile

            # Creates .pre-commit-config.yaml in project root
            PreCommitConfigConfigFile()

        Install the hooks::

            # Run this command after generating the config
            pre-commit install

    Note:
        After generating the config file, you must run `pre-commit install`
        to activate the hooks in your Git repository.

    See Also:
        pyrig.src.management.base.base.Args
            Used to format hook entry commands
        pre-commit documentation: https://pre-commit.com/
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the pre-commit config filename.

        Transforms the class name to the standard .pre-commit-config filename
        by converting underscores to hyphens and adding a leading dot.

        Returns:
            str: The string ".pre-commit-config" (without extension, which is
                added by the parent class).
        """
        filename = super().get_filename()
        return f".{filename.replace('_', '-')}"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .pre-commit-config.yaml.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_hook(
        cls,
        name: str,
        args: list[str],
        *,
        language: str = "system",
        pass_filenames: bool = False,
        always_run: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a pre-commit hook configuration dictionary.

        Builds a hook configuration dict with standard settings for local
        system hooks. The hook will use system-installed tools and run on
        every commit by default.

        Args:
            name (str): Hook identifier and display name. Used for both the
                'id' and 'name' fields in the hook configuration.
            args (list[str]): Command and arguments for the hook. Will be
                formatted as a shell command string using Args.
            language (str, optional): Hook language/runtime. Defaults to
                "system" for system-installed tools.
            pass_filenames (bool, optional): Whether to pass staged filenames
                to the hook command. Defaults to False (tools handle file
                discovery themselves).
            always_run (bool, optional): Whether to run the hook on every
                commit, even if no files match. Defaults to True.
            **kwargs (Any): Additional hook configuration options to merge
                into the hook dict (e.g., 'files', 'exclude', 'stages').

        Returns:
            dict[str, Any]: Hook configuration dictionary ready for inclusion
                in .pre-commit-config.yaml.

        Examples:
            Create a simple linting hook::

                hook = PreCommitConfigConfigFile.get_hook(
                    "lint-code",
                    ["ruff", "check", "--fix"]
                )
                # Returns: {
                #     "id": "lint-code",
                #     "name": "lint-code",
                #     "entry": "ruff check --fix",
                #     "language": "system",
                #     "always_run": True,
                #     "pass_filenames": False
                # }
        """
        hook: dict[str, Any] = {
            "id": name,
            "name": name,
            "entry": str(Args(args)),
            "language": language,
            "always_run": always_run,
            "pass_filenames": pass_filenames,
            **kwargs,
        }
        return hook

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the complete pre-commit configuration.

        Generates a full .pre-commit-config.yaml configuration with local hooks
        for code quality checks. All hooks use system-installed tools and run
        on every commit.

        The configuration includes:
            1. **lint-code**: Runs `ruff check --fix` to lint and auto-fix issues
            2. **format-code**: Runs `ruff format` to format code
            3. **check-types**: Runs `ty check` for type checking
            4. **check-security**: Runs `bandit` to scan for security vulnerabilities
            5. **check-markdown**: Runs `rumdl check` to lint markdown files

        Returns:
            dict[str, Any]: Complete pre-commit configuration with structure::

                {
                    "repos": [
                        {
                            "repo": "local",
                            "hooks": [
                                {"id": "lint-code", "name": "lint-code", ...},
                                {"id": "format-code", "name": "format-code", ...},
                                ...
                            ]
                        }
                    ]
                }

        Note:
            All hooks are configured as local hooks using system-installed tools.
            This ensures they match the project's development environment and
            don't require downloading remote repositories.

        Examples:
            The returned configuration creates a YAML file like::

                repos:
                  - repo: local
                    hooks:
                      - id: lint-code
                        name: lint-code
                        entry: ruff check --fix
                        language: system
                        always_run: true
                        pass_filenames: false
                      - id: format-code
                        name: format-code
                        entry: ruff format
                        language: system
                        always_run: true
                        pass_filenames: false
                      ...
        """
        hooks: list[dict[str, Any]] = [
            cls.get_hook(
                "lint-code",
                ["ruff", "check", "--fix"],
            ),
            cls.get_hook(
                "format-code",
                ["ruff", "format"],
            ),
            cls.get_hook(
                "check-types",
                ["ty", "check"],
            ),
            cls.get_hook(
                "check-security",
                ["bandit", "-c", "pyproject.toml", "-r", "."],
            ),
            cls.get_hook(
                "check-markdown",
                ["rumdl", "check"],
            ),
        ]
        return {
            "repos": [
                {
                    "repo": "local",
                    "hooks": hooks,
                },
            ]
        }

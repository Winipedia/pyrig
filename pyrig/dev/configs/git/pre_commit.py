"""Configuration management for pre-commit hooks.

This module provides the PreCommitConfigConfigFile class for managing
the .pre-commit-config.yaml file. It configures local hooks for linting,
formatting, type checking, and security scanning.
"""

import logging
from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.base import YamlConfigFile
from pyrig.src.project.mgt import (
    Args,
)

logger = logging.getLogger(__name__)


class PreCommitConfigConfigFile(YamlConfigFile):
    """Configuration file manager for .pre-commit-config.yaml.

    Configures local pre-commit hooks for:
        - ruff linting and formatting
        - mypy type checking
        - bandit security scanning
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the pre-commit config filename.

        Returns:
            The string ".pre-commit-config".
        """
        filename = super().get_filename()
        return f".{filename.replace('_', '-')}"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
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
        """Create a pre-commit hook configuration.

        Args:
            name: Hook identifier and display name.
            args: Command arguments for the hook.
            language: Hook language (default: "system").
            pass_filenames: Whether to pass filenames to the hook.
            always_run: Whether to run on every commit.
            **kwargs: Additional hook configuration options.

        Returns:
            Hook configuration dict.
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
        """Get the expected pre-commit configuration.

        Returns:
            Configuration dict with local hooks for linting,
            formatting, type checking, and security scanning.
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
                "check-static-types",
                ["mypy", "--exclude-gitignore"],
            ),
            cls.get_hook(
                "check-security",
                ["bandit", "-c", "pyproject.toml", "-r", "."],
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

    def __init__(self) -> None:
        """Initialize the pre-commit config file manager."""
        super().__init__()

"""Configuration management for pre-commit hooks.

This module provides the PreCommitConfigConfigFile class for managing
the .pre-commit-config.yaml file. It configures local hooks for linting,
formatting, type checking, and security scanning.
"""

import logging
from pathlib import Path
from subprocess import CompletedProcess  # nosec: B404
from typing import Any

from pyrig.dev.configs.base.base import YamlConfigFile
from pyrig.src.git.git import git_add_file
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.mgt import (
    PROJECT_MGT_RUN_ARGS,
    get_script_from_args,
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
            "entry": get_script_from_args(args),
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

    @classmethod
    def install(cls) -> CompletedProcess[bytes]:
        """Install pre-commit hooks into the git repository.

        Returns:
            The completed process result.
        """
        logger.info("Running pre-commit install")
        return run_subprocess([*PROJECT_MGT_RUN_ARGS, "pre-commit", "install"])

    @classmethod
    def run_hooks(
        cls,
        *,
        with_install: bool = True,
        all_files: bool = True,
        add_before_commit: bool = False,
        verbose: bool = True,
        check: bool = True,
    ) -> None:
        """Run all pre-commit hooks.

        Args:
            with_install: Whether to install hooks first.
            all_files: Whether to run on all files.
            add_before_commit: Whether to git add files first.
            verbose: Whether to show verbose output.
            check: Whether to raise on hook failure.
        """
        if add_before_commit:
            logger.info("Adding all files to git")
            git_add_file(Path())
        if with_install:
            cls.install()
        logger.info("Running pre-commit run")
        args = ["pre-commit", "run"]
        if all_files:
            args.append("--all-files")
        if verbose:
            args.append("--verbose")
        run_subprocess([*args], check=check)

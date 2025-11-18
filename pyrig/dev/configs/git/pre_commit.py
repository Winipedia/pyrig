"""Has config utilities for pre-commit."""

import logging
from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.base import YamlConfigFile
from pyrig.src.os.os import run_subprocess
from pyrig.src.project.poetry.poetry import (
    POETRY_ARG,
    POETRY_RUN_ARGS,
    get_script_from_args,
)

logger = logging.getLogger(__name__)


class PreCommitConfigConfigFile(YamlConfigFile):
    """Config file for pre-commit."""

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        filename = super().get_filename()
        return f".{filename.replace('_', '-')}"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_hook(
        cls,
        name: str,
        args: list[str],
        *,
        language: str = "system",
        always_run: bool = True,
        pass_filenames: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get a hook."""
        if args[0] != POETRY_ARG:
            args = POETRY_RUN_ARGS + args
        return {
            "id": name,
            "name": name,
            "entry": get_script_from_args(args),
            "language": language,
            "always_run": always_run,
            "pass_filenames": pass_filenames,
            **kwargs,
        }

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        hooks: list[dict[str, Any]] = [
            cls.get_hook(
                "update-package-manager",
                ["poetry", "self", "update"],
            ),
            cls.get_hook(
                "check-package-manager-config",
                ["poetry", "check", "--strict"],
            ),
            cls.get_hook(
                "install-dependencies",
                ["poetry", "install", "--with", "dev"],
            ),
            cls.get_hook(
                "create-root",
                ["pyrig", "create-root"],
            ),
            cls.get_hook(
                "lint-code",
                ["ruff", "check", "--fix"],
            ),
            cls.get_hook(
                "format-code",
                ["ruff", "format"],
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
        """Init the file."""
        super().__init__()

    @classmethod
    def install(cls) -> None:
        """Installs the pre commits in the config."""
        logger.info("Running pre-commit install")
        run_subprocess(["pre-commit", "install"])

    @classmethod
    def run_hooks(
        cls,
        *,
        with_install: bool = True,
        all_files: bool = True,
        add_before_commit: bool = True,
        verbose: bool = True,
        check: bool = True,
    ) -> None:
        """Runs the pre-commit hooks."""
        if add_before_commit:
            logger.info("Adding all files to git")
            run_subprocess(["git", "add", "."])
        if with_install:
            cls.install()
        logger.info("Running pre-commit run")
        args = ["pre-commit", "run"]
        if all_files:
            args.append("--all-files")
        if verbose:
            args.append("--verbose")
        run_subprocess([*args], check=check)

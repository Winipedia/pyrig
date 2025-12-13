"""Configuration management for .gitignore files.

This module provides the GitIgnoreConfigFile class for managing the
project's .gitignore file. It fetches GitHub's standard Python gitignore
and adds pyrig-specific patterns.
"""

import os
from pathlib import Path
from typing import Any

import pathspec
import requests

import pyrig
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.dot_env import DotEnvConfigFile
from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile
from pyrig.dev.utils.resources import return_resource_content_on_fetch_error


class GitIgnoreConfigFile(ConfigFile):
    """Configuration file manager for .gitignore.

    Creates a comprehensive .gitignore file by combining:
        - GitHub's standard Python.gitignore
        - VS Code workspace files
        - pyrig-specific patterns
        - Common cache directories
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get an empty filename to produce ".gitignore".

        Returns:
            Empty string so the path becomes ".gitignore".
        """
        return ""  # so it builds the path .gitignore and not gitignore.gitignore

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the gitignore file extension.

        Returns:
            The string "gitignore".
        """
        return "gitignore"

    @classmethod
    def load(cls) -> list[str]:
        """Load the .gitignore file as a list of patterns.

        Returns:
            List of gitignore patterns, one per line.
        """
        return cls.get_path().read_text(encoding="utf-8").splitlines()

    @classmethod
    def dump(cls, config: list[str] | dict[str, Any]) -> None:
        """Write patterns to the .gitignore file.

        Args:
            config: List of gitignore patterns.

        Raises:
            TypeError: If config is not a list.
        """
        if not isinstance(config, list):
            msg = f"Cannot dump {config} to .gitignore file."
            raise TypeError(msg)
        cls.get_path().write_text("\n".join(config), encoding="utf-8")

    @classmethod
    def get_configs(cls) -> list[str]:
        """Get the expected .gitignore patterns.

        Combines GitHub's Python gitignore with pyrig-specific patterns.

        Returns:
            List of gitignore patterns.
        """
        # fetch the standard github gitignore via https://github.com/github/gitignore/blob/main/Python.gitignore
        needed = [
            *cls.get_github_python_gitignore_as_list(),
            "# vscode stuff",
            ".vscode/",
            "",
            f"# {pyrig.__name__} stuff",
            ".git/",
            DotExperimentConfigFile.get_path().as_posix(),
            "# others",
            DotEnvConfigFile.get_path().as_posix(),
            ".coverage",
            "coverage.xml",
            ".mypy_cache/",
            ".pytest_cache/",
            ".ruff_cache/",
            ".venv/",
            "dist/",
        ]

        dotenv_path = DotEnvConfigFile.get_path().as_posix()
        if dotenv_path not in needed:
            needed.extend(["# for secrets used locally", dotenv_path])

        existing = cls.load()
        needed = [p for p in needed if p not in set(existing)]
        return existing + needed

    @classmethod
    @return_resource_content_on_fetch_error(resource_name="GITIGNORE")
    def get_github_python_gitignore_as_str(cls) -> str:
        """Fetch GitHub's standard Python gitignore patterns.

        Returns:
            String of patterns from GitHub's Python.gitignore.

        Raises:
            RuntimeError: If fetch fails and no .gitignore exists.
        """
        url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.text

    @classmethod
    def get_github_python_gitignore_as_list(cls) -> list[str]:
        """Fetch GitHub's standard Python gitignore patterns.

        Returns:
            List of patterns from GitHub's Python.gitignore.

        Raises:
            RuntimeError: If fetch fails and no .gitignore exists.
        """
        gitignore_str = cls.get_github_python_gitignore_as_str()
        return gitignore_str.splitlines()

    @classmethod
    def path_is_in_gitignore(cls, relative_path: str | Path) -> bool:
        """Check if a path matches any pattern in .gitignore.

        Args:
            relative_path: Path to check, relative to repository root.

        Returns:
            True if the path matches any gitignore pattern.
        """
        gitignore_path = cls.get_path()
        if not gitignore_path.exists():
            return False
        as_path = Path(relative_path)
        if as_path.is_absolute():
            as_path = as_path.relative_to(Path.cwd())
        is_dir = (
            bool(as_path.suffix == "")
            or as_path.is_dir()
            or str(as_path).endswith(os.sep)
        )
        is_dir = is_dir and not as_path.is_file()

        as_posix = as_path.as_posix()
        if is_dir and not as_posix.endswith("/"):
            as_posix += "/"

        spec = pathspec.PathSpec.from_lines(
            "gitwildmatch",
            cls.load(),
        )

        return spec.match_file(as_posix)

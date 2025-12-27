"""Configuration management for .gitignore files.

Manages .gitignore by combining GitHub's standard Python patterns with
pyrig-specific patterns (.experiment, .env, tool caches, build artifacts).
Intelligently merges with existing patterns, avoiding duplicates.

See Also:
    GitHub gitignore templates: https://github.com/github/gitignore
    Git documentation: https://git-scm.com/docs/gitignore
"""

from pathlib import Path
from typing import Any

import requests

import pyrig
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.dot_env import DotEnvConfigFile
from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile
from pyrig.dev.utils.git import load_gitignore
from pyrig.dev.utils.resources import return_resource_content_on_fetch_error


class GitIgnoreConfigFile(ConfigFile):
    """Gitignore configuration manager.

    Combines GitHub's standard Python patterns with pyrig-specific patterns
    (.vscode/, .experiment, .env, tool caches, build artifacts). Preserves
    existing patterns and only adds missing ones.

    Examples:
        Initialize .gitignore::

            GitIgnoreConfigFile()

        Load patterns::

            patterns = GitIgnoreConfigFile.load()

    Note:
        Makes HTTP request to GitHub for Python.gitignore. Uses fallback on failure.

    See Also:
        pyrig.dev.utils.git.load_gitignore
        pyrig.dev.configs.dot_env.DotEnvConfigFile
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get an empty filename to produce ".gitignore".

        Returns:
            str: Empty string (produces ".gitignore" not "gitignore.gitignore").
        """
        return ""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .gitignore.

        Returns:
            Path: Project root.
        """
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for .gitignore.

        Returns:
            str: "gitignore" (combined with empty filename produces ".gitignore").
        """
        return "gitignore"

    @classmethod
    def load(cls) -> list[str]:
        """Load the .gitignore file as a list of patterns.

        Returns:
            list[str]: Gitignore patterns (one per line, preserves comments).

        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        return load_gitignore(path=cls.get_path())

    @classmethod
    def dump(cls, config: list[str] | dict[str, Any]) -> None:
        """Write patterns to the .gitignore file.

        Args:
            config (list[str]): Gitignore patterns (one per line).

        Raises:
            TypeError: If config is not a list.

        Note:
            Overwrites entire file. Use get_configs() to merge with existing.
        """
        if not isinstance(config, list):
            msg = f"Cannot dump {config} to .gitignore file."
            raise TypeError(msg)
        cls.get_path().write_text("\n".join(config), encoding="utf-8")

    @classmethod
    def get_configs(cls) -> list[str]:
        """Get complete .gitignore patterns with intelligent merging.

        Combines GitHub's Python patterns with pyrig-specific patterns (.vscode/,
        .experiment, .env, tool caches, build artifacts). Preserves existing
        patterns and avoids duplicates.

        Returns:
            list[str]: Complete gitignore patterns (existing + missing standard).

        Note:
            Makes HTTP request to GitHub. Uses fallback on failure.
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
            ".coverage",  # bc of pytest-cov
            "coverage.xml",  # bc of pytest-cov
            ".pytest_cache/",  # bc of pytest cache
            ".ruff_cache/",  # bc of ruff cache
            ".rumdl_cache/",  # bc of rumdl cache
            ".venv/",  # bc of uv venv
            "dist/",  # bc of uv publish
            "/site/",  # bc of mkdocs
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
            str: Python.gitignore content from GitHub.

        Raises:
            requests.HTTPError: If HTTP request fails (caught by decorator).
            RuntimeError: If fetch fails and no fallback exists.

        Note:
            Makes HTTP request with 10s timeout. Decorator provides fallback.
        """
        url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.text

    @classmethod
    def get_github_python_gitignore_as_list(cls) -> list[str]:
        """Fetch GitHub's standard Python gitignore patterns as a list.

        Returns:
            list[str]: Python.gitignore patterns (one per line).

        Raises:
            requests.HTTPError: If HTTP request fails.
            RuntimeError: If fetch fails and no fallback exists.
        """
        gitignore_str = cls.get_github_python_gitignore_as_str()
        return gitignore_str.splitlines()

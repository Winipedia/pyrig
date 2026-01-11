"""Configuration management for .gitignore files.

Manages .gitignore by combining GitHub's standard Python patterns with
pyrig-specific patterns (.experiment, .env, tool caches, build artifacts).
Intelligently merges with existing patterns, avoiding duplicates.

See Also:
    GitHub gitignore templates: https://github.com/github/gitignore
    Git documentation: https://git-scm.com/docs/gitignore
"""

from functools import cache
from pathlib import Path

import requests

import pyrig
from pyrig.dev.configs.base.string_ import StringConfigFile
from pyrig.dev.configs.dot_env import DotEnvConfigFile
from pyrig.dev.configs.python.dot_experiment import DotExperimentConfigFile
from pyrig.dev.utils.resources import return_resource_content_on_fetch_error


class GitIgnoreConfigFile(StringConfigFile):
    """Gitignore configuration manager.

    Combines GitHub's standard Python patterns with pyrig-specific patterns
    (.experiment, .env, tool caches, build artifacts). Preserves existing
    patterns and only adds missing ones.

    Examples:
        Initialize .gitignore::

            GitIgnoreConfigFile()

        Load patterns::

            patterns = GitIgnoreConfigFile.load()

    Note:
        Makes HTTP request to GitHub for Python.gitignore. Uses fallback on failure.

    See Also:
        pyrig.dev.management.version_controller.VersionController.get_loaded_ignore
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
    def get_lines(cls) -> list[str]:
        """Get complete .gitignore patterns with intelligent merging.

        Combines GitHub's Python patterns with pyrig-specific patterns
        (.experiment, .env, tool caches, build artifacts). Preserves existing
        patterns and avoids duplicates.

        Returns:
            list[str]: Complete gitignore patterns (existing + missing standard).

        Note:
            Makes HTTP request to GitHub. Uses fallback on failure.
        """
        # fetch the standard github gitignore via https://github.com/github/gitignore/blob/main/Python.gitignore
        needed = [
            *cls.get_github_python_gitignore_as_list(),
            "",
            f"# {pyrig.__name__} stuff",
            DotExperimentConfigFile.L.get_path().as_posix(),
            DotEnvConfigFile.L.get_path().as_posix(),
            ".coverage",  # bc of pytest-cov
            "coverage.xml",  # bc of pytest-cov
            ".pytest_cache/",  # bc of pytest cache
            ".ruff_cache/",  # bc of ruff cache
            ".rumdl_cache/",  # bc of rumdl cache
            ".venv/",  # bc of uv venv
            "dist/",  # bc of uv publish
            "/site/",  # bc of mkdocs
        ]

        existing = cls.load()
        needed = [p for p in needed if p not in set(existing)]
        return existing + needed

    @classmethod
    @return_resource_content_on_fetch_error(resource_name="GITIGNORE")
    @cache
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

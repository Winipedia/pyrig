"""Configuration management for .gitignore files.

This module provides the GitIgnoreConfigFile class for managing the project's
.gitignore file, which specifies intentionally untracked files that Git should
ignore.

The generated .gitignore file combines:
    - **GitHub's Standard Python Patterns**: Fetched from the official GitHub
      gitignore repository, covering common Python build artifacts, bytecode,
      virtual environments, and IDE files
    - **VS Code Patterns**: Excludes .vscode/ workspace settings
    - **pyrig-Specific Patterns**: Excludes .experiment, .env, and pyrig caches
    - **Tool-Specific Caches**: Excludes .ruff_cache, .rumdl_cache, .pytest_cache
    - **Build Artifacts**: Excludes dist/, site/, .coverage files

The class intelligently merges existing patterns with new ones, avoiding
duplicates and preserving user customizations.

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
    """Configuration file manager for .gitignore files.

    Creates and maintains a comprehensive .gitignore file by combining GitHub's
    standard Python gitignore patterns with pyrig-specific patterns. The class
    fetches the latest Python.gitignore from GitHub and adds patterns for:
        - VS Code workspace files (.vscode/)
        - pyrig-specific files (.experiment, .env)
        - Tool caches (.ruff_cache, .rumdl_cache, .pytest_cache)
        - Build artifacts (dist/, site/, coverage files)
        - Virtual environments (.venv/)

    The class preserves existing patterns and only adds missing ones, ensuring
    user customizations are not lost.

    Examples:
        Initialize the .gitignore file::

            from pyrig.dev.configs.git.gitignore import GitIgnoreConfigFile

            # Creates or updates .gitignore
            GitIgnoreConfigFile()

        Load and inspect patterns::

            patterns = GitIgnoreConfigFile.load()
            print(f"Ignoring {len(patterns)} patterns")

    Note:
        This class makes an external HTTP request to GitHub to fetch the
        standard Python.gitignore template. On failure, it uses a fallback
        template from resources.

    See Also:
        pyrig.dev.utils.git.load_gitignore
            Utility function for loading gitignore files
        pyrig.dev.configs.dot_env.DotEnvConfigFile
            .env file is automatically added to .gitignore
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get an empty filename to produce ".gitignore".

        Returns:
            str: Empty string so the final path becomes ".gitignore" instead
                of "gitignore.gitignore".
        """
        return ""  # so it builds the path .gitignore and not gitignore.gitignore

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .gitignore.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for .gitignore.

        Returns:
            str: The string "gitignore" (combined with empty filename to
                produce ".gitignore").
        """
        return "gitignore"

    @classmethod
    def load(cls) -> list[str]:
        """Load the .gitignore file as a list of patterns.

        Reads the .gitignore file from disk and returns each line as a
        separate pattern in a list.

        Returns:
            list[str]: List of gitignore patterns, one per line. Empty lines
                and comments are preserved.

        Note:
            This method reads from disk. If the file doesn't exist, it will
            raise a FileNotFoundError.
        """
        return load_gitignore(path=cls.get_path())

    @classmethod
    def dump(cls, config: list[str] | dict[str, Any]) -> None:
        """Write patterns to the .gitignore file.

        Writes a list of gitignore patterns to the .gitignore file, joining
        them with newlines.

        Args:
            config (list[str]): List of gitignore patterns to write. Each
                element becomes a line in the file.

        Raises:
            TypeError: If config is not a list.

        Note:
            This method overwrites the entire .gitignore file. Use get_configs()
            to merge with existing patterns.
        """
        if not isinstance(config, list):
            msg = f"Cannot dump {config} to .gitignore file."
            raise TypeError(msg)
        cls.get_path().write_text("\n".join(config), encoding="utf-8")

    @classmethod
    def get_configs(cls) -> list[str]:
        """Get the complete .gitignore patterns with intelligent merging.

        Combines GitHub's standard Python gitignore patterns with pyrig-specific
        patterns, while preserving existing patterns and avoiding duplicates.

        The method:
            1. Fetches GitHub's Python.gitignore (or uses fallback)
            2. Adds VS Code patterns (.vscode/)
            3. Adds pyrig-specific patterns (.experiment, .git/)
            4. Adds tool caches (.ruff_cache, .rumdl_cache, .pytest_cache)
            5. Adds build artifacts (dist/, site/, coverage files)
            6. Adds .env file for secrets
            7. Loads existing patterns from disk
            8. Merges new patterns with existing ones (no duplicates)

        Returns:
            list[str]: Complete list of gitignore patterns, combining existing
                patterns with any missing standard patterns.

        Note:
            This method makes an external HTTP request to GitHub. On failure,
            it uses a fallback template from resources.

        Examples:
            Returns a list like::

                [
                    "# Byte-compiled / optimized / DLL files",
                    "__pycache__/",
                    "*.py[cod]",
                    ...
                    "# vscode stuff",
                    ".vscode/",
                    "# pyrig stuff",
                    ".experiment",
                    ".env",
                    ...
                ]
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
        """Fetch GitHub's standard Python gitignore patterns as a string.

        Makes an HTTP GET request to GitHub's gitignore repository to fetch
        the latest Python.gitignore template. On failure, the decorator
        provides a fallback template from resources.

        Returns:
            str: Complete Python.gitignore content from GitHub, including
                comments and all standard Python patterns.

        Raises:
            requests.HTTPError: If the HTTP request fails (caught by decorator).
            RuntimeError: If fetch fails and no fallback resource exists.

        Note:
            This method makes an external HTTP request with a 10-second timeout.
            The @return_resource_content_on_fetch_error decorator provides
            automatic fallback to a bundled template on network errors.

        See Also:
            GitHub Python.gitignore: https://github.com/github/gitignore/blob/main/Python.gitignore
        """
        url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.text

    @classmethod
    def get_github_python_gitignore_as_list(cls) -> list[str]:
        """Fetch GitHub's standard Python gitignore patterns as a list.

        Fetches the Python.gitignore template from GitHub and splits it into
        individual lines for easier processing.

        Returns:
            list[str]: List of gitignore patterns from GitHub's Python.gitignore,
                one pattern per line. Includes comments and empty lines.

        Raises:
            requests.HTTPError: If the HTTP request fails (caught by decorator).
            RuntimeError: If fetch fails and no fallback resource exists.

        Note:
            This method makes an external HTTP request. Use the result to build
            a comprehensive .gitignore file with additional custom patterns.
        """
        gitignore_str = cls.get_github_python_gitignore_as_str()
        return gitignore_str.splitlines()

"""Configuration management for .gitignore files.

Manages .gitignore by combining GitHub's standard Python patterns with
pyrig-specific patterns (.scratch.py, .env, tool caches, build artifacts).
Intelligently merges with existing patterns, avoiding duplicates.

See Also:
    GitHub gitignore templates: https://github.com/github/gitignore
    Git documentation: https://git-scm.com/docs/gitignore
"""

from pathlib import Path

import pyrig
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.configs.dot_env import DotEnvConfigFile
from pyrig.rig.configs.python.dot_scratch import DotScratchConfigFile
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.resources import (
    requests_get_text_cached,
    return_resource_content_on_fetch_error,
)


class GitignoreConfigFile(StringConfigFile):
    """Gitignore configuration manager.

    Combines GitHub's standard Python patterns with pyrig-specific patterns
    (.scratch.py, .env, tool caches, build artifacts). Preserves existing
    patterns and only adds missing ones.

    Examples:
        validate .gitignore::

            GitignoreConfigFile.I.validate()

        Load patterns::

            patterns = GitignoreConfigFile.I.load()

    Note:
        Makes HTTP request to GitHub for Python.gitignore. Uses fallback on failure.

    See Also:
        pyrig.rig.tools.version_controller.VersionController.loaded_ignore
        pyrig.rig.configs.dot_env.DotEnvConfigFile
    """

    def filename(self) -> str:
        """Get the filename for .gitignore."""
        return VersionController.I.ignore_filename()

    def parent_path(self) -> Path:
        """Get parent directory (project root)."""
        return Path()

    def extension_separator(self) -> str:
        """Get extension separator (empty; .gitignore has no extension)."""
        return ""

    def extension(self) -> str:
        """Get file extension (empty; .gitignore has no extension)."""
        return ""

    def lines(self) -> list[str]:
        """Get complete .gitignore patterns with intelligent merging.

        Combines GitHub's Python patterns with pyrig-specific patterns
        (.scratch.py, .env, tool caches, build artifacts). Preserves existing
        patterns and avoids duplicates.

        Returns:
            list[str]: Complete gitignore patterns (existing + missing standard).

        Note:
            Makes HTTP request to GitHub. Uses fallback on failure.
        """
        # fetch the standard github gitignore via https://github.com/github/gitignore/blob/main/Python.gitignore
        needed = [
            *self.github_python_gitignore_lines(),
            "",
            f"# {pyrig.__name__} stuff",
            DotScratchConfigFile.I.path().as_posix(),
            DotEnvConfigFile.I.path().as_posix(),
            ".coverage",  # bc of pytest-cov
            "coverage.xml",  # bc of pytest-cov
            ".pytest_cache/",  # bc of pytest cache
            ".ruff_cache/",  # bc of ruff cache
            ".rumdl_cache/",  # bc of rumdl cache
            ".venv/",  # bc of uv venv
            "dist/",  # bc of uv publish
            "/site/",  # bc of mkdocs
        ]

        existing = self.load()
        needed = [p for p in needed if p not in set(existing)]
        return existing + needed

    @return_resource_content_on_fetch_error(resource_name="GITIGNORE")
    def github_python_gitignore(self) -> str:
        """Fetch GitHub's standard Python gitignore patterns.

        Returns:
            str: Python.gitignore content from GitHub.

        Note:
            Makes HTTP request with 10s timeout. Decorator provides fallback.
        """
        url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
        return requests_get_text_cached(url)

    def github_python_gitignore_lines(self) -> list[str]:
        """Fetch GitHub's standard Python gitignore patterns as a list.

        Returns:
            list[str]: Python.gitignore patterns (one per line).
        """
        gitignore_str = self.github_python_gitignore()
        return gitignore_str.splitlines()

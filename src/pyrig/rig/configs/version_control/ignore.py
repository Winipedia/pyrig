"""Configuration management for .gitignore files.

Manages .gitignore by combining GitHub's standard Python patterns with
pyrig-specific patterns (.scratch.py, .env, tool caches, build artifacts).
Intelligently merges with existing patterns, avoiding duplicates.

See Also:
    GitHub gitignore templates: https://github.com/github/gitignore
    Git documentation: https://git-scm.com/docs/gitignore
"""

from pathlib import Path

from pyrig.core.resources import resource_content
from pyrig.core.strings import pyrig_project_name
from pyrig.rig import resources
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.version_controller import VersionController


class VersionControllerIgnoreConfigFile(StringConfigFile):
    """Gitignore configuration manager.

    Combines GitHub's standard Python patterns with pyrig-specific patterns
    (.scratch.py, .env, tool caches, build artifacts). Preserves existing
    patterns and only adds missing ones.

    Examples:
        validate .gitignore::

            VersionControllerIgnoreConfigFile.I.validate()

        Load patterns::

            patterns = VersionControllerIgnoreConfigFile.I.load()

    Note:
        Makes HTTP request to GitHub for Python.gitignore. Uses fallback on failure.

    See Also:
        pyrig.rig.tools.version_controller.VersionController.loaded_ignore
        pyrig.rig.configs.dot_env.DotEnvConfigFile
    """

    def stem(self) -> str:
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
        ignored_paths = {
            cf().path().as_posix()
            for cf in ConfigFile.version_control_ignored_subclasses()
        }

        needed = [
            f"# {pyrig_project_name()} stuff",
            "__pycache__/",  # bc of python bytecode cache
            ".coverage",  # bc of pytest-cov
            "coverage.xml",  # bc of pytest-cov
            ".pytest_cache/",  # bc of pytest cache
            ".ruff_cache/",  # bc of ruff cache
            ".rumdl_cache/",  # bc of rumdl cache
            ".venv/",  # bc of uv venv
            "dist/",  # bc of uv publish
            "/site/",  # bc of mkdocs
            *ignored_paths,  # ignored config files (e.g. .scratch.py, .env)
        ]
        standard = self.standard_ignore_lines()
        standard_set = set(standard)
        needed = [line for line in needed if line not in standard_set]

        return [*standard, *needed, ""]

    def standard_ignore_lines(self) -> list[str]:
        """Fetch GitHub's standard Python gitignore patterns as a list.

        Returns:
            list[str]: Python.gitignore patterns (one per line).
        """
        return self.split_lines(resource_content("GITIGNORE", resources))

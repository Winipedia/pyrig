"""Configuration management for .gitignore files."""

from pathlib import Path

from pyrig.core.resources import resource_content
from pyrig.rig import resources
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.pyrigger import Pyrigger


class VersionControllerIgnoreConfigFile(StringConfigFile):
    """Manages the ``.gitignore`` file for a pyrig project.

    Produces the final ``.gitignore`` content by merging a bundled Python gitignore
    baseline with pyrig-specific additions such as tool caches, build artifacts, and
    the paths of config files that are excluded from version control (e.g. ``.env``,
    ``.scratch.py``). Entries already present in the baseline are never duplicated.
    """

    def stem(self) -> str:
        """Return the stem of the ``.gitignore`` filename.

        Returns:
            ``'.gitignore'``
        """
        return ".gitignore"

    def parent_path(self) -> Path:
        """Return the directory where ``.gitignore`` is written.

        Returns:
            ``Path()`` — the current working directory, representing the project root.
        """
        return Path()

    def extension_separator(self) -> str:
        """Return the separator between the stem and the extension.

        Returns:
            An empty string, because ``.gitignore`` has no extension.
        """
        return ""

    def extension(self) -> str:
        """Return the file extension.

        Returns:
            An empty string, because ``.gitignore`` has no extension.
        """
        return ""

    def lines(self) -> list[str]:
        """Build the complete list of lines for ``.gitignore``.

        Assembles the final pattern list by merging the standard Python gitignore
        baseline with pyrig-specific additions.

        Returns:
            Complete list of ``.gitignore`` lines with the baseline first,
            followed by any pyrig-specific additions not already present in
            the baseline, and a trailing empty string.
        """
        standard = self.standard_ignore_lines()
        standard_set = set(standard)
        additional = [
            line for line in self.additional_ignore_lines() if line not in standard_set
        ]
        return [*standard, *additional, ""]

    def standard_ignore_lines(self) -> list[str]:
        """Return the bundled Python gitignore baseline as a list of lines.

        Reads the ``GITIGNORE`` resource file packaged with
        ``pyrig.rig.resources`` — a snapshot of GitHub's ``Python.gitignore``
        template — and splits it into individual lines.

        Returns:
            Lines from the bundled Python gitignore baseline.
        """
        return self.split_lines(resource_content("GITIGNORE", resources))

    def additional_ignore_lines(self) -> list[str]:
        """Additional lines to be ignored.

        Builds a list of pyrig-specific patterns to be added to the gitignore.
        They are only added if not already present in the standard baseline
        to avoid duplication.
        This will always include at least the line ``# Pyrigger stuff`` as a header for
        the pyrig-specific entries.
        Some enries here are already covered by the standard Python gitignore, but are
        included here to be sure as they are almost garantueed to occur in a
        pyrig project.
        """
        ignored_paths = (
            cf().path().as_posix()
            for cf in ConfigFile.version_control_ignored_subclasses()
        )
        return [
            f"# {Pyrigger.I.name()} stuff",
            "__pycache__/",  # bc of python bytecode cache
            ".coverage",  # bc of pytest-cov
            ".pytest_cache/",  # bc of pytest cache
            ".ruff_cache/",  # bc of ruff cache
            ".rumdl_cache/",  # bc of rumdl cache
            ".venv",  # bc of uv venv
            "dist/",  # bc of uv publish
            "/site",  # bc of mkdocs
            *ignored_paths,  # ignored config files (e.g. .scratch.py, .env)
        ]

"""Configuration management for .gitignore files."""

from pathlib import Path

from pyrig.core.resources import resource_content
from pyrig.rig import resources
from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.pyrigger import Pyrigger


class VersionControllerIgnoreConfigFile(StringConfigFile):
    """Manages the ``.gitignore`` file for a pyrig project.

    Produces the final ``.gitignore`` content by merging a bundled Python gitignore
    baseline with pyrig-specific additions such as tool caches, build artifacts, and
    the paths of config files that are excluded from version control (e.g. ``.env``,
    ``.scratch.py``). Entries already present in the baseline are never duplicated.

    Examples:
        Validate the ``.gitignore`` file::

            VersionControllerIgnoreConfigFile.I.validate()

        Load the current patterns::

            patterns = VersionControllerIgnoreConfigFile.I.load()
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

        Assembles the final pattern list by:

        1. Collecting the file paths of all ``ConfigFile`` subclasses whose
           ``version_control_ignored()`` returns ``True`` (e.g. ``.env``,
           ``.scratch.py``).
        2. Building a list of pyrig-specific patterns covering tool caches
           (pytest, ruff, rumdl), build artifacts, the virtual environment,
           the docs output directory, and those collected paths.
        3. Reading the bundled Python gitignore baseline via
           ``standard_ignore_lines()``.
        4. Removing any pyrig-specific entry that already appears in the
           baseline to avoid duplication.
        5. Returning the baseline lines, then the remaining pyrig-specific
           additions, followed by a trailing empty string for a final newline.

        Returns:
            Complete list of ``.gitignore`` lines with the baseline first,
            followed by any pyrig-specific additions not already present in
            the baseline, and a trailing empty string.
        """
        # fetch the standard github gitignore via https://github.com/github/gitignore/blob/main/Python.gitignore
        ignored_subclasses = self.version_control_ignored_subclasses()
        ignored_paths = {cf().path().as_posix() for cf in ignored_subclasses}

        needed = [
            f"# {Pyrigger.I.name()} stuff",
            "__pycache__/",  # bc of python bytecode cache
            ".coverage",  # bc of pytest-cov
            "coverage.xml",  # bc of pytest-cov
            ".pytest_cache/",  # bc of pytest cache
            ".ruff_cache/",  # bc of ruff cache
            ".rumdl_cache/",  # bc of rumdl cache
            ".venv",  # bc of uv venv
            "dist/",  # bc of uv publish
            "/site",  # bc of mkdocs
            *ignored_paths,  # ignored config files (e.g. .scratch.py, .env)
        ]
        standard = self.standard_ignore_lines()
        standard_set = set(standard)
        needed = [line for line in needed if line not in standard_set]

        return [*standard, *needed, ""]

    def standard_ignore_lines(self) -> list[str]:
        """Return the bundled Python gitignore baseline as a list of lines.

        Reads the ``GITIGNORE`` resource file packaged with
        ``pyrig.rig.resources`` — a snapshot of GitHub's ``Python.gitignore``
        template — and splits it into individual lines.

        Returns:
            Lines from the bundled Python gitignore baseline.
        """
        return self.split_lines(resource_content("GITIGNORE", resources))

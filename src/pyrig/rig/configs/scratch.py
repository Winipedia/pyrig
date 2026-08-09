"""Management of the project-root scratch file used for ad-hoc experimentation."""

from pathlib import Path

from pyrig.rig.configs.base.python import PythonConfigFile


class ScratchConfigFile(PythonConfigFile):
    """Config file manager for `.scratch.py`.

    `.scratch.py` is excluded from version control and never committed.
    Its required content is a single module docstring line, so any other
    code the user adds to the file is preserved across validation runs.
    """

    def content(self) -> str:
        """Return a one-line module docstring followed by a trailing newline."""
        return (
            '"""This file is for scratch work and is ignored by version control."""\n'
        )

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `".scratch"`."""
        return ".scratch"

    def version_control_ignored(self) -> bool:
        """Return `True`; `.scratch.py` is always excluded from version control."""
        return True

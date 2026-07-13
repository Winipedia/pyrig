"""Management of the project-root scratch file used for ad-hoc experimentation."""

from pathlib import Path

from pyrig.rig.configs.base.python import PythonConfigFile


class ScratchConfigFile(PythonConfigFile):
    """Config file manager for `.scratch.py`.

    `.scratch.py` is excluded from version control and never committed.
    Because its content is meant to be edited freely by the user, validation
    checks only that the file exists, not what it contains.
    """

    def content(self) -> str:
        """Return a one-line module docstring followed by a trailing newline."""
        return (
            '"""This file is for scratch work and is ignored by version control."""\n'
        )

    def create_file(self) -> None:
        """Create `.scratch.py` and remove the root `main.py`, if present."""
        super().create_file()
        self.delete_root_main()

    def parent_path(self) -> Path:
        """Return the project root as the parent directory."""
        return Path()

    def stem(self) -> str:
        """Return `".scratch"`."""
        return ".scratch"

    def version_control_ignored(self) -> bool:
        """Return `True`; `.scratch.py` is always excluded from version control."""
        return True

    def delete_root_main(self) -> None:
        """Delete `main.py` at the project root, if present.

        `uv init` places a starter `main.py` at the project root; pyrig-managed
        projects do not use it.
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            root_main_path.unlink()

"""Configuration for the .scratch.py scratch file at the project root."""

from pathlib import Path

from pyrig.rig.configs.base.python import PythonConfigFile


class DotScratchConfigFile(PythonConfigFile):
    """Manages the .scratch.py file at the project root.

    .scratch.py is a local scratch file intended for ad-hoc experimentation.
    It is automatically excluded from version control via .gitignore and is
    never committed to the repository. Validation only checks that the file
    exists; content is intentionally left free for the user to modify.

    When the scratch file is first created, the root-level ``main.py`` that
    ``uv init`` leaves behind is removed, since pyrig-managed projects do not
    use it.
    """

    def create_file(self) -> None:
        """Generate ``.scratch.py`` and remove the root ``main.py``.

        Delegates file creation to the parent implementation, then removes
        ``main.py`` from the project root if it exists.
        """
        super().create_file()
        self.delete_root_main()

    def is_correct(self) -> bool:
        """Return whether .scratch.py exists at the project root.

        Overrides the default validation from the base class, which verifies
        required content. Because .scratch.py is a
        free-form scratch file that users are expected to edit freely,
        content is not validated — only existence matters.

        Returns:
            bool: True if .scratch.py exists at the project root.
        """
        return self.path().exists()

    def version_control_ignored(self) -> bool:
        """Return True to indicate .scratch.py is excluded from version control.

        Returns:
            bool: Always True.
        """
        return True

    def stem(self) -> str:
        """Return the stem of the scratch filename.

        Combined with the ".py" extension provided by the parent class,
        this produces the filename ".scratch.py".

        Returns:
            str: ".scratch"
        """
        return ".scratch"

    def parent_path(self) -> Path:
        """Return the directory that will contain .scratch.py.

        Returns:
            Path: An empty Path, representing the project root.
        """
        return Path()

    def lines(self) -> list[str]:
        """Return the initial content lines written to .scratch.py.

        The generated file contains only a module docstring stating its
        purpose. Users are free to replace or extend this content.

        Returns:
            list[str]: Initial content lines for the scratch file.
        """
        return ['"""This file is for scratch work and is ignored by git."""', ""]

    def delete_root_main(self) -> None:
        """Remove ``main.py`` from the project root if it exists.

        ``uv init`` places a ``main.py`` in the project root as a starter
        script. Pyrig-managed projects do not use it, so this cleanup step
        removes it after the scratch file is generated.
        """
        root_main_path = Path("main.py")
        if root_main_path.exists():
            root_main_path.unlink()

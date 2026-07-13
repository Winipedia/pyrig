"""Command-line wrapper for the Python linter and formatter."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group


class PythonLinter(FileTool):
    """`ruff` command wrapper for linting, auto-fixing, and formatting."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `ruff`."""
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"

    def link_url(self) -> str:
        """Return the URL of the `ruff` project page."""
        return "https://github.com/astral-sh/ruff"

    def name(self) -> str:
        """Return `"ruff"`."""
        return "ruff"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return `ruff`'s cache directory as the only path to ignore."""
        return (".ruff_cache/",)

    def types(self) -> list[str]:
        """Return the list of file types that `ruff` can lint and format.

        Deliberately excludes `pyi`: `identify` tags a `.pyi` stub file as
        `pyi`, not `python` - a separate, non-overlapping tag - but a
        pyrig-scaffolded project is a pure-Python, inline-typed project by
        default (see the generated `py.typed` marker), with no native
        build backend for the one case that actually justifies a `.pyi`
        file (a C/Rust extension with no `.py` source to annotate). A
        project that adds one is already customizing well past pyrig's
        defaults and can add `pyi` back here too.
        """
        return ["python"]

    def check_fix_args(self, *args: str) -> Args:
        """Build a `ruff check` command with auto-fix enabled.

        Args:
            *args: Additional arguments appended after `--fix`.

        Returns:
            Args for `ruff check --fix`.
        """
        return self.check_args("--fix", *args)

    def check_args(self, *args: str) -> Args:
        """Build a `ruff check` command.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `ruff check`.
        """
        return self.args("check", *args)

    def format_args(self, *args: str) -> Args:
        """Build a `ruff format` command.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `ruff format`.
        """
        return self.args("format", *args)

    def pydocstyle(self) -> str:
        """Return `google` as the docstring standard."""
        return "google"

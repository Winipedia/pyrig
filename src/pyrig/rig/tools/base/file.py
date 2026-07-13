"""Shared contract for tools a prek hook invokes with a scoped subset of files."""

from abc import abstractmethod

from pyrig.rig.tools.base.tool import Tool


class FileTool(Tool):
    """Abstract base for a `Tool` that a prek hook invokes with specific files.

    Distinguishes tools that operate on a scoped subset of files (e.g. a
    linter or formatter) from ones that scan the whole project instead
    (e.g. a type checker or dependency auditor) - see
    `pyrig.rig.configs.version_control.hook_manager`. A plain `Tool` used
    that second way (like `PackageManager`, invoked for whole-project
    hooks such as updating the lockfile) has no need for `regex` and
    is not a `FileTool`.
    """

    @abstractmethod
    def extension(self) -> str:
        """Return the file extension this tool's files end in, without the dot."""

    def regex(self) -> str:
        r"""Return the regex identifying which files this tool operates on.

        Built from `extension()` by default (e.g. `"sh"` becomes `r"\.sh$"`),
        matching that one extension exactly. Override directly instead when a
        tool's files can't be identified by a single extension (e.g. `.py`
        and `.pyi` both, or a path prefix restriction) - `extension()` still
        must return something even then, since it stays required for every
        `FileTool`; return whichever extension is the primary/most common one.

        Returns:
            A regex matching `extension()` at the end of a path.
        """
        return rf"\.{self.extension()}$"

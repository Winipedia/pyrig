"""Detection of unused, missing, and transitive Python dependencies."""

from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.file import FileTool
from pyrig.rig.tools.base.tool import Group
from pyrig.rig.tools.linting.python import PythonLinter


class DependencyChecker(FileTool):
    """`deptry` command wrapper."""

    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    def image_url(self) -> str:
        """Return the Shields.io badge URL advertising `deptry`."""
        return f"https://img.shields.io/badge/dependencies-{self.shield_name()}-blue"

    def link_url(self) -> str:
        """Return the URL of the `deptry` project page."""
        return "https://github.com/osprey-oss/deptry"

    def name(self) -> str:
        """Return `"deptry"`."""
        return "deptry"

    def types(self) -> list[str]:
        """Return the file types that affect `deptry`'s dependency check.

        Python source plus `pyproject.toml` itself, since `deptry`
        reconciles imports found in the former against dependencies
        declared in the latter - a commit that only changes one of the
        two is still a case it needs to check. Deliberately excludes
        `pyi`, unlike `PythonLinter`'s own type list: confirmed by testing
        that `deptry` never scans `.pyi` stub files for imports at all
        (a stub-only change can't affect its dependency analysis), so
        delegating to `PythonLinter.types()` wholesale would be wrong
        here, not just imprecise. Only used to gate whether this hook
        runs at all - `deptry` always analyzes the whole project once
        triggered, since it needs the full import graph.
        """
        return [*PythonLinter.I.types(), "pyproject"]

    def check_args(self, *args: str) -> Args:
        """Build the `deptry` command.

        Args:
            *args: Additional CLI flags for `deptry`.

        Returns:
            Args for running `deptry` with the given flags.
        """
        return self.args(*args)

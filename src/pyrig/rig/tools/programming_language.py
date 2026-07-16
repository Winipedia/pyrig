"""Metadata and constants for the project's programming language."""

import shutil
from collections.abc import Iterator
from itertools import chain
from pathlib import Path

import typer

from pyrig.core.introspection.packages import make_init_files
from pyrig.rig.tools.base.tool import Group, Tool
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.testing.project import ProjectTester


class ProgrammingLanguage(Tool):
    """Tool wrapper for the Python programming language.

    Python is the only supported language; this wrapper gives a single,
    consistent access point for language-level details so callers never
    hard-code language-specific strings.
    """

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `()`, since Python is the runtime and not a dev dependency."""
        return ()

    def group(self) -> str:
        """Return `Group.PROJECT_INFO`."""
        return Group.PROJECT_INFO

    def image_url(self) -> str:
        """Return the Shields.io badge image URL for Python."""
        return f"https://img.shields.io/badge/Language-Python-3776AB?logo={self.name()}&logoColor=white"

    def link_url(self) -> str:
        """Return the URL of the official Python website."""
        return "https://www.python.org"

    def name(self) -> str:
        """Return `"python"`."""
        return "python"

    def version_control_ignore_patterns(self) -> tuple[str, ...]:
        """Return `("__pycache__/",)`."""
        return ("__pycache__/",)

    def make_init_files(self) -> tuple[Path, ...]:
        """Create all missing `__init__.py` files in the project.

        Echoes each directory where a file was created to standard output.

        Returns:
            Directories where `__init__.py` files were created. Empty if all
            already existed.
        """
        return make_init_files(
            self.namespace_package_paths(),
            content=self.standard_init_content(),
        )

    def namespace_package_paths(self) -> Iterator[Path]:
        """Yield project directories that lack an `__init__.py` file.

        Searches the source package root and tests package root, including each
        root itself and all subdirectories at any depth, skipping `__pycache__`
        directories.

        Yields:
            Each directory under the source or tests package root that has no
            `__init__.py`.
        """
        package_root, tests_package_root = (
            PackageManager.I.package_root(),
            ProjectTester.I.package_root(),
        )
        for p in chain(
            (package_root, tests_package_root),
            package_root.rglob("*"),
            tests_package_root.rglob("*"),
        ):
            if not p.is_dir():
                continue
            if p.name == "__pycache__":
                continue
            init = p / "__init__.py"
            if init.exists():
                continue
            yield p

    def no_bytecode_env_var(self) -> str:
        """Return the name of the env var that disables `.pyc` bytecode writing."""
        return "PYTHONDONTWRITEBYTECODE"

    def remove_pycache(self) -> None:
        """Remove all `__pycache__` directories in the project.

        Covers the package root and tests package root at all depths, echoing
        each removed path to standard output.
        """
        roots = (ProjectTester.I.package_root(), PackageManager.I.package_root())
        for root in roots:
            for pycache in root.rglob("__pycache__"):
                if pycache.is_dir():
                    shutil.rmtree(pycache)
                    typer.echo(f"Removed {pycache}")

    def standard_init_content(self) -> str:
        """Return the minimal source text for a generated `__init__.py` file."""
        return '"""Package initialization."""\n'

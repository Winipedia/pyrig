"""Metadata and constants for the project's programming language."""

from pyrig.rig.tools.base.tool import Group, Tool


class ProgrammingLanguage(Tool):
    """Tool wrapper for the Python programming language.

    Python is the only supported language; this wrapper gives a single,
    consistent access point for language-level details so callers never
    hard-code language-specific strings.
    """

    def name(self) -> str:
        """Return `"python"`."""
        return "python"

    def group(self) -> str:
        """Return `Group.PROJECT_INFO`."""
        return Group.PROJECT_INFO

    def image_url(self) -> str:
        """Return the Shields.io badge image URL for Python."""
        return "https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white"

    def link_url(self) -> str:
        """Return the URL of the official Python website."""
        return "https://www.python.org"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return `("__pycache__/",)`."""
        return ("__pycache__/",)

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `()`, since Python is the runtime and not a dev dependency."""
        return ()

    def no_bytecode_env_var(self) -> str:
        """Return the name of the env var that disables `.pyc` bytecode writing."""
        return "PYTHONDONTWRITEBYTECODE"

    def standard_init_content(self) -> str:
        """Return the minimal source text for a generated `__init__.py` file."""
        return '"""Package initialization."""\n'

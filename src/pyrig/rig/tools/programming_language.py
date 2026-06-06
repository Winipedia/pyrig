"""Programming language tool wrapper.

Wraps ProgrammingLanguage commands and information.
"""

from pyrig.rig.tools.base.tool import Tool, ToolGroup


class ProgrammingLanguage(Tool):
    """Tool wrapper for the Python programming language.

    Provides Python-specific metadata and constants used across the project,
    such as the language badge, the bytecode suppression environment variable,
    and the standard ``__init__.py`` content written to namespace packages.

    Python is the only supported language; this wrapper exists to give a
    single, consistent access point for language-level details so callers
    never hard-code language-specific strings.
    """

    def name(self) -> str:
        """Return the canonical name of the programming language.

        Returns:
            ``"python"``.
        """
        return "python"

    def group(self) -> str:
        """Return the tool group for the programming language.

        Returns:
            ``ToolGroup.PROJECT_INFO``.
        """
        return ToolGroup.PROJECT_INFO

    def image_url(self) -> str:
        """Return the badge image URL for Python.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white"

    def link_url(self) -> str:
        """Return the link URL for Python.

        Returns:
            The URL of the official Python website as a string.
        """
        return "https://www.python.org"

    def version_control_ignore_paths(self) -> tuple[str, ...]:
        """Return a tuple of file paths to ignore for version control."""
        return ("__pycache__/",)

    def dev_dependencies(self) -> tuple[str, ...]:
        """Return an empty tuple — Python is the runtime, not a dev dependency.

        Overrides the base implementation, which would otherwise include the
        tool name (``"python"``) in the aggregated dev-dependency list.

        Returns:
            An empty tuple.
        """
        return ()

    def no_bytecode_env_var(self) -> str:
        """Return the environment variable that disables ``.pyc`` bytecode generation.

        Set this variable to a truthy value (e.g. ``1``) to instruct Python not
        to write compiled bytecode files. Used in CI workflow environment blocks
        to keep the workspace clean.

        Returns:
            ``"PYTHONDONTWRITEBYTECODE"``.
        """
        return "PYTHONDONTWRITEBYTECODE"

    def standard_init_content(self) -> str:
        """Return the minimal content written to generated ``__init__.py`` files.

        Used when creating ``__init__.py`` files for namespace packages so that
        every package has a consistent, minimal docstring.

        Returns:
            A single-line module docstring followed by a newline.
        """
        return '"""Package initialization."""\n'

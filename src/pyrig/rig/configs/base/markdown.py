"""Abstract base for Markdown (`.md`) configuration file management."""

from pyrig.rig.configs.base.string_ import StringConfigFile


class MarkdownConfigFile(StringConfigFile):
    r"""Abstract base for Markdown (`.md`) configuration files.

    Fixes the file extension to `"md"`.

    Subclasses must implement:
        - `parent_path`: Directory containing the `.md` file.
        - `stem`: Filename without its extension.
        - `content`: Required Markdown content.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.markdown import MarkdownConfigFile
        >>>
        >>> class ReadmeFile(MarkdownConfigFile):
        ...     def parent_path(self) -> Path:
        ...         return Path()
        ...
        ...     def stem(self) -> str:
        ...         return "README"
        ...
        ...     def content(self) -> str:
        ...         return "# My Project\n\nDescription here."
    """

    def extension(self) -> str:
        """Return the file extension `"md"`."""
        return "md"

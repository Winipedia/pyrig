"""Abstract base for shell script (`.sh`) configuration file management."""

from pyrig.rig.configs.base.string_ import StringConfigFile


class ShellConfigFile(StringConfigFile):
    r"""Abstract base for shell script (`.sh`) configuration files.

    Fixes the file extension to `"sh"`.

    Subclasses must implement:
        - `parent_path`: Directory containing the `.sh` file.
        - `stem`: Filename without its extension.
        - `content`: Required shell script content.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.shell import ShellConfigFile
        >>>
        >>> class GreetScriptFile(ShellConfigFile):
        ...     def parent_path(self) -> Path:
        ...         return Path(".github/scripts")
        ...
        ...     def stem(self) -> str:
        ...         return "greet"
        ...
        ...     def content(self) -> str:
        ...         return 'greet() {\n  echo "Hello, $1"\n}'
    """

    def extension(self) -> str:
        """Return the file extension `"sh"`."""
        return "sh"

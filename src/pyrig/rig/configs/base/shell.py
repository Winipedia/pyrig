"""Abstract base for shell script (`.sh`) configuration file management."""

from pyrig.rig.configs.base.string_ import StringConfigFile


class ShellConfigFile(StringConfigFile):
    """Abstract base for shell script (`.sh`) configuration files.

    Fixes the file extension to `"sh"`.

    Subclasses must implement:
        - `parent_path`: Directory containing the `.sh` file.
        - `stem`: Filename without its extension.
        - `lines`: Required shell script content as a list of lines.

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
        ...     def lines(self) -> list[str]:
        ...         return ["greet() {", '  echo "Hello, $1"', "}"]
    """

    def extension(self) -> str:
        """Return the file extension `"sh"`."""
        return "sh"

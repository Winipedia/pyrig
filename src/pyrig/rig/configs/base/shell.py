"""Abstract base for shell script (`.sh`) configuration file management."""

from abc import abstractmethod

from pyrig.rig.configs.base.string_ import StringConfigFile


class ShellConfigFile(StringConfigFile):
    r"""Abstract base for shell script (`.sh`) configuration files.

    Fixes the file extension to `"sh"` and prepends a shebang and strict
    mode line to every script. The shebang pins the interpreter to `bash`,
    required because the strict mode line's `pipefail` option is a bash
    extension that a plain POSIX `sh` does not support. Strict mode
    (`set -euo pipefail`) makes a failed command anywhere in a pipeline
    abort the script instead of silently masking the failure.

    Subclasses must implement:
        - `parent_path`: Directory containing the `.sh` file.
        - `stem`: Filename without its extension.
        - `script_content`: Required shell script content, below the header.

    Example:
        >>> from pathlib import Path
        >>> from pyrig.rig.configs.base.shell import ShellConfigFile
        >>>
        >>> class GreetScriptFile(ShellConfigFile):
        ...     def parent_path(self) -> Path:
        ...         return Path(".github/")
        ...
        ...     def stem(self) -> str:
        ...         return "greet"
        ...
        ...     def script_content(self) -> str:
        ...         return 'greet() {\n  echo "Hello, $1"\n}'
    """

    @abstractmethod
    def script_content(self) -> str:
        """Return the script's required content, below the shared header.

        Returns:
            Shell script content, excluding the shebang and strict mode
            line, which `content()` prepends automatically.
        """

    def content(self) -> str:
        """Prepend the shebang and strict mode line to `script_content()`.

        Returns:
            The shebang line, the strict mode line, a blank line, and
            `script_content()`.
        """
        return f"""{self.shebang_line()}
{self.strict_mode_line()}

{self.script_content()}"""

    def extension(self) -> str:
        """Return the file extension `"sh"`."""
        return "sh"

    def shebang_line(self) -> str:
        """Return `"#!/usr/bin/env bash"`."""
        return "#!/usr/bin/env bash"

    def strict_mode_line(self) -> str:
        """Return `"set -euo pipefail"`."""
        return "set -euo pipefail"

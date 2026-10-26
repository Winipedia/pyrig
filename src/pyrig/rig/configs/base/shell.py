"""Abstract base for shell script (`.sh`) configuration file management."""

from abc import abstractmethod

from pyrig.rig.configs.base.string_ import StringConfigFile
from pyrig.rig.tools.formatting.shell import ShellFormatter


class ShellConfigFile(StringConfigFile):
    r"""Abstract base for shell script (`.sh`) configuration files.

    Adds a Bash shebang and strict-mode header to each script, followed by
    checks for any required environment variables.

    Subclasses must implement:
        - `parent_path`: Directory containing the `.sh` file.
        - `stem`: Filename without its extension.
        - `script`: Required shell script content, below the header.

    Override `required_env_vars` when a script needs nonempty environment
    variables before it runs. By default, no variables are required.
    """

    @abstractmethod
    def script(self) -> str:
        """Return shell content to place after the shared header.

        Returns:
            Shell content without the shared header or required-variable checks.
        """

    def required_env_vars(self) -> tuple[str, ...]:
        """Return names of environment variables the script requires.

        Each name must be valid as a shell variable reference, and each
        variable must be nonempty when the script runs. Defaults to an empty
        tuple.
        """
        return ()

    def content(self) -> str:
        """Return the script with the shared header prepended.

        Returns:
            The header, a blank line, and the shell content returned by `script()`.
        """
        return f"""{self.global_content()}

{self.script()}"""

    def extension(self) -> str:
        """Return the file extension `"sh"`."""
        return "sh"

    def global_content(self) -> str:
        """Return the shebang, strict mode, and any required variable checks."""
        content = f"""{self.shebang_line()}
{self.strict_mode_line()}"""
        if self.required_env_vars():
            content = f"""{content}

{self.required_env_var_checks()}"""
        return content

    def required_env_var_checks(self) -> str:
        """Return an assertion for each required environment variable.

        The shell exits if a variable is unset or empty. Return an empty string
        when no variables are required.
        """
        return "\n".join(
            f': "${{{var}:?}}"' for var in sorted(self.required_env_vars())
        )

    def shebang_line(self) -> str:
        """Return the shebang pinning the interpreter to the shell dialect."""
        return f"#!/usr/bin/env {ShellFormatter.I.dialect()}"

    def strict_mode_line(self) -> str:
        """Return `"set -euo pipefail"`."""
        return "set -euo pipefail"

"""Manage .env files for local environment variables and secrets.

Creates an empty .env file in the project root if one does not exist.
Pyrig does not manage the file's content; users populate and maintain it
manually. The file is automatically added to .gitignore so secrets are
never committed to version control.
"""

from pathlib import Path

from dotenv import dotenv_values

from pyrig.rig.configs.base.config_file import ConfigDict, DictConfigFile


class DotEnvConfigFile(DictConfigFile):
    """Config file manager for .env.

    Ensures a .env file exists at the project root for storing local
    environment variables and secrets. Pyrig only creates the file when
    missing; all content is managed by the user directly.

    Writing is intentionally blocked: dump() raises PermissionError when
    called with a non-empty config to prevent accidental overwriting of
    user secrets. The file is gitignored by default.
    """

    def _load(self) -> dict[str, str | None]:
        """Load all key-value pairs from the .env file.

        Parses the file according to dotenv format rules. Keys declared
        without a value (e.g. ``KEY=``) are returned as empty strings.

        Returns:
            Mapping of variable names to their string values, or None for
            keys that are present without an assignment.
        """
        return dotenv_values(self.path())

    def _dump(self, config: ConfigDict) -> None:
        """Block all non-empty writes to the .env file.

        Pyrig never overwrites .env content because the file holds user
        secrets that must not be lost. Passing an empty dict is allowed so
        the base class can create an empty placeholder file without
        triggering this guard.

        Args:
            config: Configuration to write. Must be empty.

        Raises:
            PermissionError: When config is non-empty.
        """
        if config:
            msg = f"""Dumping to {self} is forbidden.
For security reasons this file is managed manually by the user.
Please edit it directly."""
            raise PermissionError(msg)

    def _configs(self) -> ConfigDict:
        """Return an empty dict; pyrig manages no .env content.

        Returns:
            An empty dict.
        """
        return {}

    def version_control_ignored(self) -> bool:
        """Indicate that .env is excluded from version control.

        Returns:
            Always True.
        """
        return True

    def parent_path(self) -> Path:
        """Return the project root as the parent directory for .env.

        Returns:
            Path(), which resolves to the current working directory
            (the project root at runtime).
        """
        return Path()

    def stem(self) -> str:
        """Return the filename stem for the .env file.

        Together with the empty extension and empty separator returned by
        extension() and extension_separator(), this produces the final
        filename .env.

        Returns:
            ``".env"``
        """
        return ".env"

    def extension(self) -> str:
        """Return an empty string because .env has no extension.

        Returns:
            ``""``
        """
        return ""

    def extension_separator(self) -> str:
        """Return an empty separator between stem and extension.

        Overrides the default ``"."`` separator so that the stem ``".env"``
        is not followed by a trailing dot when combined with the empty
        extension.

        Returns:
            ``""``
        """
        return ""

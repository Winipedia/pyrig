"""Config utilities for .gitignore."""

import os
from pathlib import Path
from typing import Any

import pathspec
import requests

import pyrig
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.dot_env import DotEnvConfigFile
from pyrig.dev.configs.python.experiment import ExperimentConfigFile


class GitIgnoreConfigFile(ConfigFile):
    """Config file for .gitignore."""

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return ""  # so it builds the path .gitignore and not gitignore.gitignore

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "gitignore"

    @classmethod
    def load(cls) -> list[str]:
        """Load the config file."""
        return cls.get_path().read_text(encoding="utf-8").splitlines()

    @classmethod
    def dump(cls, config: list[str] | dict[str, Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, list):
            msg = f"Cannot dump {config} to .gitignore file."
            raise TypeError(msg)
        cls.get_path().write_text("\n".join(config), encoding="utf-8")

    @classmethod
    def get_configs(cls) -> list[str]:
        """Get the config."""
        # fetch the standard github gitignore via https://github.com/github/gitignore/blob/main/Python.gitignore
        needed = [
            *cls.get_github_python_gitignore(),
            "# vscode stuff",
            ".vscode/",
            "",
            f"# {pyrig.__name__} stuff",
            "# for walk_os_skipping_gitignore_patterns func",
            ".git/",
            "# for executing experimental code",
            "/" + ExperimentConfigFile.get_path().as_posix(),
        ]

        dotenv_path = DotEnvConfigFile.get_path().as_posix()
        if dotenv_path not in needed:
            needed.extend(["# for secrets used locally", dotenv_path])

        existing = cls.load()
        needed = [p for p in needed if p not in set(existing)]
        return existing + needed

    @classmethod
    def get_github_python_gitignore(cls) -> list[str]:
        """Get the standard github python gitignore."""
        url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
        res = requests.get(url, timeout=10)
        if not res.ok:
            if not Path(".gitignore").exists():
                msg = f"Failed to fetch {url}. Cannot create .gitignore."
                raise RuntimeError(msg)
            return []
        return res.text.splitlines()

    @classmethod
    def path_is_in_gitignore(cls, relative_path: str | Path) -> bool:
        """Check if a path matches any pattern in the .gitignore file.

        Args:
            relative_path: The path to check, relative to the repository root

        Returns:
            True if the path matches any pattern in .gitignore, False otherwise

        """
        gitignore_path = cls.get_path()
        if not gitignore_path.exists():
            return False
        as_path = Path(relative_path)
        if as_path.is_absolute():
            as_path = as_path.relative_to(Path.cwd())
        is_dir = (
            bool(as_path.suffix == "")
            or as_path.is_dir()
            or str(as_path).endswith(os.sep)
        )
        is_dir = is_dir and not as_path.is_file()

        as_posix = as_path.as_posix()
        if is_dir and not as_posix.endswith("/"):
            as_posix += "/"

        spec = pathspec.PathSpec.from_lines(
            "gitwildmatch",
            cls.load(),
        )

        return spec.match_file(as_posix)

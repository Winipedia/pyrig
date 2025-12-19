"""Configuration management for Containerfile files.

This module provides the ContainerfileConfigFile class for managing the
project's Containerfile file. It fetches GitHub's standard Python gitignore
and adds pyrig-specific patterns.
"""

import json
from pathlib import Path

from pyrig.dev.configs.base.base import TextConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.main import main
from pyrig.src.project.mgt import DependencyManager


class ContainerfileConfigFile(TextConfigFile):
    """Configuration file manager for Containerfile.

    Creates a Containerfile file in the project root. It is based on the
    GitHub Containerfile template.
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the Containerfile filename.

        Returns:
            The string "Containerfile".
        """
        return "Containerfile"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the project root directory.

        Returns:
            Path to the project root.
        """
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the Containerfile file extension.

        Returns:
            The string "Containerfile".
        """
        return ""

    @classmethod
    def get_extension_sep(cls) -> str:
        """Get the Containerfile extension separator.

        Returns:
            The string "".
        """
        return ""

    @classmethod
    def get_content_str(cls) -> str:
        """Get the Containerfile content.

        Builds a standard working Containerfile from scratch.

        Returns:
            The Containerfile content.
        """
        return "\n\n".join(cls.get_layers())

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the Containerfile is valid.

        Returns:
            True if each step in the Containerfile is present.
        """
        all_layers_in_file = all(
            layer in cls.get_file_content() for layer in cls.get_layers()
        )
        return super().is_correct() or all_layers_in_file

    @classmethod
    def get_layers(cls) -> list[str]:
        """Get the layers of the Containerfile.

        Returns:
            List of strings with each layer.
        """
        latest_python_version = PyprojectConfigFile.get_latest_possible_python_version()
        project_name = PyprojectConfigFile.get_project_name()
        package_name = PyprojectConfigFile.get_package_name()
        app_user_name = "appuser"
        entrypoint_args = list(DependencyManager.get_run_args(project_name))
        default_cmd_args = [main.__name__]
        return [
            f"FROM python:{latest_python_version}-slim",
            f"WORKDIR /{project_name}",
            "COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv",
            "COPY README.md LICENSE pyproject.toml uv.lock ./",
            f"RUN useradd -m -u 1000 {app_user_name}",
            f"RUN chown -R {app_user_name}:{app_user_name} .",
            f"USER {app_user_name}",
            f"COPY --chown=appuser:appuser {package_name} {package_name}",
            "RUN uv sync --no-group dev",
            "RUN rm README.md LICENSE pyproject.toml uv.lock",
            f"ENTRYPOINT {json.dumps(entrypoint_args)}",
            # if the image is provided a different command, it will run that instead
            # so adding a default is convenient without restricting usage
            f"CMD {json.dumps(default_cmd_args)}",
        ]

"""Configuration management for Containerfile files.

This module provides the ContainerfileConfigFile class for managing the project's
Containerfile, which is a Docker-compatible container build file used to create
production-ready container images.

The generated Containerfile follows best practices:
    - Uses Python slim base image for smaller image size
    - Installs uv package manager for fast dependency installation
    - Creates non-root user (appuser) for security
    - Optimizes layer caching by copying dependencies first
    - Sets proper file permissions
    - Configures entrypoint and default command
    - Removes unnecessary files after installation

The Containerfile is compatible with Docker, Podman, and other OCI-compliant
container runtimes.

Example Containerfile structure:
    FROM python:3.13-slim
    WORKDIR /myproject
    COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
    COPY README.md LICENSE pyproject.toml uv.lock ./
    RUN useradd -m -u 1000 appuser
    RUN chown -R appuser:appuser .
    USER appuser
    COPY --chown=appuser:appuser mypackage mypackage
    RUN uv sync --no-group dev
    RUN rm README.md LICENSE pyproject.toml uv.lock
    ENTRYPOINT ["uv", "run", "myproject"]
    CMD ["pyrig.main:main"]

See Also:
    Containerfile specification: https://github.com/containers/common/blob/main/docs/Containerfile.5.md
    Docker documentation: https://docs.docker.com/engine/reference/builder/
"""

import json
from pathlib import Path

from pyrig.dev.configs.base.text import TextConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.main import main
from pyrig.src.management.package_manager import PackageManager


class ContainerfileConfigFile(TextConfigFile):
    """Configuration file manager for Containerfile.

    Generates a production-ready Containerfile in the project root that builds
    optimized container images for Python applications. The Containerfile uses
    multi-stage builds, layer caching, and security best practices.

    Key Features:
        - **Slim Base Image**: Uses python:X.Y-slim for smaller image size
        - **Fast Dependencies**: Integrates uv package manager
        - **Security**: Runs as non-root user (appuser, UID 1000)
        - **Layer Optimization**: Copies dependencies before source code
        - **Clean Images**: Removes build artifacts after installation
        - **Flexible Execution**: Configurable entrypoint and command

    The generated Containerfile is compatible with Docker, Podman, buildah, and
    other OCI-compliant container runtimes.

    Examples:
        Generate a Containerfile::

            from pyrig.dev.configs.containers.container_file import (
                ContainerfileConfigFile,
            )

            # Creates Containerfile in project root
            ContainerfileConfigFile()

        Build and run the container::

            # Using Docker
            docker build -t myproject .
            docker run myproject

            # Using Podman
            podman build -t myproject .
            podman run myproject

    See Also:
        pyrig.dev.configs.pyproject.PyprojectConfigFile
            Used to determine Python version and project metadata
        pyrig.src.management.package_manager.PackageManager
            Provides the run command for the entrypoint
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the Containerfile filename.

        Returns:
            str: The string "Containerfile" (capitalized, no extension).
        """
        return "Containerfile"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for Containerfile.

        Returns:
            Path: Empty Path() representing the project root directory.
        """
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension for Containerfile.

        Returns:
            str: Empty string (Containerfile has no file extension).
        """
        return ""

    @classmethod
    def get_extension_sep(cls) -> str:
        """Get the extension separator for Containerfile.

        Returns:
            str: Empty string (no separator needed since there's no extension).
        """
        return ""

    @classmethod
    def get_content_str(cls) -> str:
        """Get the complete Containerfile content.

        Builds a production-ready Containerfile by joining all layers with
        double newlines for readability.

        Returns:
            str: Complete Containerfile content with all build instructions.

        Note:
            This method calls get_layers() which reads from pyproject.toml
            and may make external API calls to determine the Python version.
        """
        return "\n\n".join(cls.get_layers())

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the Containerfile is valid and complete.

        Validates that all expected layers are present in the Containerfile.
        This ensures the file hasn't been corrupted or manually edited to
        remove critical build steps.

        Returns:
            bool: True if all layers from get_layers() are present in the file,
                False otherwise.

        Note:
            This method reads the Containerfile from disk and compares it
            against the expected layers.
        """
        all_layers_in_file = all(
            layer in cls.get_file_content() for layer in cls.get_layers()
        )
        return super().is_correct() or all_layers_in_file

    @classmethod
    def get_layers(cls) -> list[str]:
        r"""Get the individual layers (instructions) of the Containerfile.

        Generates a list of Containerfile instructions that build an optimized
        container image. The layers are ordered to maximize Docker layer caching:
            1. Base image selection
            2. Working directory setup
            3. uv package manager installation
            4. Dependency files copy (for caching)
            5. User creation and permissions
            6. Source code copy
            7. Dependency installation
            8. Cleanup
            9. Entrypoint and command configuration

        Returns:
            list[str]: List of Containerfile instructions, each as a string.
                Instructions include FROM, WORKDIR, COPY, RUN, USER, ENTRYPOINT,
                and CMD directives.

        Note:
            This method reads from pyproject.toml and may make external API calls
            to determine the latest supported Python version.

        Examples:
            Returns a list like::

                [
                    "FROM python:3.13-slim",
                    "WORKDIR /myproject",
                    "COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv",
                    "COPY README.md LICENSE pyproject.toml uv.lock ./",
                    "RUN useradd -m -u 1000 appuser",
                    "RUN chown -R appuser:appuser .",
                    "USER appuser",
                    "COPY --chown=appuser:appuser mypackage mypackage",
                    "RUN uv sync --no-group dev",
                    "RUN rm README.md LICENSE pyproject.toml uv.lock",
                    "ENTRYPOINT ["uv", "run", "myproject"]",
                    "CMD ["pyrig.main:main"]"
                ]
        """
        latest_python_version = PyprojectConfigFile.get_latest_possible_python_version()
        project_name = PyprojectConfigFile.get_project_name()
        package_name = PyprojectConfigFile.get_package_name()
        app_user_name = "appuser"
        entrypoint_args = list(PackageManager.get_run_args(project_name))
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

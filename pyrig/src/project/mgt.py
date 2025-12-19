"""Project management utilities for Python projects.

This module provides utilities for managing Python projects using various tools
including uv (package manager), git (version control), pre-commit (code quality),
and podman (containerization). It centralizes command construction for common
project management tasks.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from subprocess import CompletedProcess  # nosec: B404
from typing import Any

from pyrig.src.modules.package import get_project_name_from_pkg_name
from pyrig.src.os.os import run_subprocess

logger = logging.getLogger(__name__)


class Args(tuple[str, ...]):
    """Command-line arguments container with execution capabilities.

    A tuple subclass that represents command-line arguments and provides
    convenient methods for string representation and subprocess execution.
    """

    __slots__ = ()

    def __str__(self) -> str:
        """Convert arguments to a space-separated string.

        Returns:
            str: Space-separated string of all arguments.
        """
        return " ".join(self)

    def run(self, *args: str, **kwargs: Any) -> CompletedProcess[Any]:
        """Execute the command represented by these arguments.

        Args:
            *args: Additional positional arguments to pass to run_subprocess.
            **kwargs: Additional keyword arguments to pass to run_subprocess.

        Returns:
            CompletedProcess[Any]: The completed process result containing
                return code, stdout, and stderr.
        """
        return run_subprocess(self, *args, **kwargs)


class Tool(ABC):
    """Abstract base class for tool command argument construction.

    Subclasses must implement the ``name`` method to provide the tool name.
    They can then use the ``get_args`` method to construct command arguments
    starting with the tool name.
    """

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Get the name of the tool.

        Returns:
            str: The name of the tool.
        """

    @classmethod
    def get_args(cls, *args: str) -> Args:
        """Construct base command arguments.

        Args:
            *args: Additional arguments to append to the command.

        Returns:
            Args: Command arguments starting with the tool name.
        """
        return Args((cls.name(), *args))


class DependencyManager(Tool):
    """UV package manager tool for Python projects.

    Provides methods for constructing uv command arguments for package
    management, project initialization, building, and publishing.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'uv'.
        """
        return "uv"

    @classmethod
    def get_init_project_args(cls, *args: str) -> Args:
        """Construct uv init command arguments for project initialization.

        Args:
            *args: Additional arguments to append to the init command.

        Returns:
            Args: Command arguments for 'uv init'.
        """
        return cls.get_args("init", *args)

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct uv run command arguments.

        Args:
            *args: Additional arguments to append to the run command.

        Returns:
            Args: Command arguments for 'uv run'.
        """
        return cls.get_args("run", *args)

    @classmethod
    def get_add_dependencies_args(cls, *args: str) -> Args:
        """Construct uv add command arguments for dependencies.

        Args:
            *args: Package names or additional arguments for the add command.

        Returns:
            Args: Command arguments for 'uv add'.
        """
        return cls.get_args("add", *args)

    @classmethod
    def get_add_dev_dependencies_args(cls, *args: str) -> Args:
        """Construct uv add command arguments for dev dependencies.

        Args:
            *args: Package names or additional arguments for the add command.

        Returns:
            Args: Command arguments for 'uv add --group dev'.
        """
        return cls.get_args("add", "--group", "dev", *args)

    @classmethod
    def get_install_dependencies_args(cls, *args: str) -> Args:
        """Construct uv sync command arguments for installing dependencies.

        Args:
            *args: Additional arguments to append to the sync command.

        Returns:
            Args: Command arguments for 'uv sync'.
        """
        return cls.get_args("sync", *args)

    @classmethod
    def get_update_dependencies_args(cls, *args: str) -> Args:
        """Construct uv lock command arguments for updating dependencies.

        Args:
            *args: Additional arguments to append to the lock command.

        Returns:
            Args: Command arguments for 'uv lock --upgrade'.
        """
        return cls.get_args("lock", "--upgrade", *args)

    @classmethod
    def get_update_self_args(cls, *args: str) -> Args:
        """Construct uv self update command arguments.

        Args:
            *args: Additional arguments to append to the self update command.

        Returns:
            Args: Command arguments for 'uv self update'.
        """
        return cls.get_args("self", "update", *args)

    @classmethod
    def get_patch_version_args(cls, *args: str) -> Args:
        """Construct uv version command arguments for patch version bump.

        Args:
            *args: Additional arguments to append to the version command.

        Returns:
            Args: Command arguments for 'uv version --bump patch'.
        """
        return cls.get_args("version", "--bump", "patch", *args)

    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        """Construct uv build command arguments.

        Args:
            *args: Additional arguments to append to the build command.

        Returns:
            Args: Command arguments for 'uv build'.
        """
        return cls.get_args("build", *args)

    @classmethod
    def get_publish_args(cls, token: str, *args: str) -> Args:
        """Construct uv publish command arguments with authentication token.

        Args:
            token: Authentication token for publishing.
            *args: Additional arguments to append to the publish command.

        Returns:
            Args: Command arguments for 'uv publish --token <token>'.
        """
        return cls.get_args("publish", "--token", token, *args)

    @classmethod
    def get_version_args(cls, *args: str) -> Args:
        """Construct uv version command arguments.

        Args:
            *args: Additional arguments to append to the version command.

        Returns:
            Args: Command arguments for 'uv version'.
        """
        return cls.get_args("version", *args)

    @classmethod
    def get_version_short_args(cls, *args: str) -> Args:
        """Construct uv version command arguments with short output format.

        Args:
            *args: Additional arguments to append to the version command.

        Returns:
            Args: Command arguments for 'uv version --short'.
        """
        return cls.get_version_args("--short", *args)


class Pyrig(Tool):
    """Pyrig command-line tool.

    Provides methods for constructing pyrig command arguments and
    running pyrig commands through uv.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'pyrig'.
        """
        return "pyrig"

    @classmethod
    def get_cmd_args(cls, cmd: Callable[..., Any], *args: str) -> Args:
        """Construct pyrig command arguments from a callable.

        Args:
            cmd: Callable whose name will be converted to a command name.
            *args: Additional arguments to append to the command.

        Returns:
            Args: Command arguments for 'pyrig <cmd_name>'.
        """
        cmd_name = get_project_name_from_pkg_name(cmd.__name__)  # ty:ignore[unresolved-attribute]
        return cls.get_args(cmd_name, *args)

    @classmethod
    def get_venv_run_args(cls, *args: str) -> Args:
        """Construct uv run pyrig command arguments.

        Args:
            *args: Additional arguments to append to the pyrig command.

        Returns:
            Args: Command arguments for 'uv run pyrig'.
        """
        return DependencyManager.get_run_args(*cls.get_args(*args))

    @classmethod
    def get_venv_run_cmd_args(cls, cmd: Callable[..., Any], *args: str) -> Args:
        """Construct uv run pyrig command arguments from a callable.

        Args:
            cmd: Callable whose name will be converted to a command name.
            *args: Additional arguments to append to the command.

        Returns:
            Args: Command arguments for 'uv run pyrig <cmd_name>'.
        """
        return DependencyManager.get_run_args(*cls.get_cmd_args(cmd, *args))


class TestRunner(Tool):
    """Pytest test runner tool.

    Provides methods for constructing pytest command arguments through uv run.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'pytest'.
        """
        return "pytest"

    @classmethod
    def get_run_tests_args(cls, *args: str) -> Args:
        """Construct uv run pytest command arguments.

        Args:
            *args: Additional arguments to append to the pytest command.

        Returns:
            Args: Command arguments for 'uv run pytest'.
        """
        return DependencyManager.get_run_args(cls.name(), *args)

    @classmethod
    def get_run_tests_in_ci_args(cls, *args: str) -> Args:
        """Construct uv run pytest command arguments for CI environment.

        Args:
            *args: Additional arguments to append to the pytest command.

        Returns:
            Args: Command arguments for 'uv run pytest' with CI-specific flags
                including log level INFO and XML coverage report.
        """
        return cls.get_run_tests_args("--log-cli-level=INFO", "--cov-report=xml", *args)


class VersionControl(Tool):
    """Git version control tool.

    Provides methods for constructing git command arguments for common
    version control operations.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'git'.
        """
        return "git"

    @classmethod
    def get_init_args(cls, *args: str) -> Args:
        """Construct git init command arguments.

        Args:
            *args: Additional arguments to append to the init command.

        Returns:
            Args: Command arguments for 'git init'.
        """
        return cls.get_args("init", *args)

    @classmethod
    def get_add_args(cls, *args: str) -> Args:
        """Construct git add command arguments.

        Args:
            *args: Files or paths to add to the staging area.

        Returns:
            Args: Command arguments for 'git add'.
        """
        return cls.get_args("add", *args)

    @classmethod
    def get_add_all_args(cls, *args: str) -> Args:
        """Construct git add command arguments for all files.

        Args:
            *args: Additional arguments to append to the add command.

        Returns:
            Args: Command arguments for 'git add .'.
        """
        return cls.get_add_args(".", *args)

    @classmethod
    def get_add_pyproject_toml_args(cls, *args: str) -> Args:
        """Construct git add command arguments for pyproject.toml.

        Args:
            *args: Additional arguments to append to the add command.

        Returns:
            Args: Command arguments for 'git add pyproject.toml'.
        """
        return cls.get_add_args("pyproject.toml", *args)

    @classmethod
    def get_add_pyproject_toml_and_uv_lock_args(cls, *args: str) -> Args:
        """Construct git add command arguments for pyproject.toml and uv.lock.

        Args:
            *args: Additional arguments to append to the add command.

        Returns:
            Args: Command arguments for 'git add pyproject.toml uv.lock'.
        """
        return cls.get_add_pyproject_toml_args("uv.lock", *args)

    @classmethod
    def get_commit_args(cls, *args: str) -> Args:
        """Construct git commit command arguments.

        Args:
            *args: Additional arguments to append to the commit command.

        Returns:
            Args: Command arguments for 'git commit'.
        """
        return cls.get_args("commit", *args)

    @classmethod
    def get_commit_no_verify_args(cls, msg: str, *args: str) -> Args:
        """Construct git commit command arguments with no verification.

        Args:
            msg: Commit message.
            *args: Additional arguments to append to the commit command.

        Returns:
            Args: Command arguments for 'git commit --no-verify -m <msg>'.
        """
        # wrap in quotes in case there are quotes in the message
        return cls.get_commit_args("--no-verify", "-m", msg, *args)

    @classmethod
    def get_push_args(cls, *args: str) -> Args:
        """Construct git push command arguments.

        Args:
            *args: Additional arguments to append to the push command.

        Returns:
            Args: Command arguments for 'git push'.
        """
        return cls.get_args("push", *args)

    @classmethod
    def get_config_args(cls, *args: str) -> Args:
        """Construct git config command arguments.

        Args:
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config'.
        """
        return cls.get_args("config", *args)

    @classmethod
    def get_config_global_args(cls, *args: str) -> Args:
        """Construct git config command arguments with --global flag.

        Args:
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config --global'.
        """
        return cls.get_config_args("--global", *args)

    @classmethod
    def get_config_local_args(cls, *args: str) -> Args:
        """Construct git config command arguments with --local flag.

        Args:
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config --local'.
        """
        return cls.get_config_args("--local", *args)

    @classmethod
    def get_config_local_user_email_args(cls, email: str, *args: str) -> Args:
        """Construct git config command arguments for user email.

        Args:
            email: Email address.
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config --local user.email <email>'.
        """
        return cls.get_config_local_args("user.email", email, *args)

    @classmethod
    def get_config_local_user_name_args(cls, name: str, *args: str) -> Args:
        """Construct git config command arguments for user name.

        Args:
            name: Name.
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config --local user.name <name>'.
        """
        return cls.get_config_local_args("user.name", name, *args)

    @classmethod
    def get_config_global_user_email_args(cls, email: str, *args: str) -> Args:
        """Construct git config command arguments for user email.

        Args:
            email: Email address.
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config user.email <email>'.
        """
        return cls.get_config_global_args("user.email", email, *args)

    @classmethod
    def get_config_global_user_name_args(cls, name: str, *args: str) -> Args:
        """Construct git config command arguments for user name.

        Args:
            name: Name.
            *args: Additional arguments to append to the config command.

        Returns:
            Args: Command arguments for 'git config user.name <name>'.
        """
        return cls.get_config_global_args("user.name", name, *args)


class PreCommit(Tool):
    """Pre-commit code quality tool.

    Provides methods for constructing pre-commit command arguments for
    installing and running hooks.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'pre-commit'.
        """
        return "pre-commit"

    @classmethod
    def get_install_args(cls, *args: str) -> Args:
        """Construct pre-commit install command arguments.

        Args:
            *args: Additional arguments to append to the install command.

        Returns:
            Args: Command arguments for 'pre-commit install'.
        """
        return cls.get_args("install", *args)

    @classmethod
    def get_run_args(cls, *args: str) -> Args:
        """Construct pre-commit run command arguments.

        Args:
            *args: Additional arguments to append to the run command.

        Returns:
            Args: Command arguments for 'pre-commit run'.
        """
        return cls.get_args("run", *args)

    @classmethod
    def get_run_all_files_args(cls, *args: str) -> Args:
        """Construct pre-commit run command arguments for all files.

        Args:
            *args: Additional arguments to append to the run command.

        Returns:
            Args: Command arguments for 'pre-commit run --all-files'.
        """
        return cls.get_run_args("--all-files", *args)

    @classmethod
    def get_run_all_files_verbose_args(cls, *args: str) -> Args:
        """Construct pre-commit run command arguments for all files with verbose output.

        Args:
            *args: Additional arguments to append to the run command.

        Returns:
            Args: Command arguments for 'pre-commit run --all-files --verbose'.
        """
        return cls.get_run_all_files_args("--verbose", *args)


class ContainerEngine(Tool):
    """Podman container engine tool.

    Provides methods for constructing podman command arguments for
    building and managing containers.
    """

    @classmethod
    def name(cls) -> str:
        """Get the tool name.

        Returns:
            str: The string 'podman'.
        """
        return "podman"

    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        """Construct podman build command arguments.

        Args:
            *args: Additional arguments to append to the build command.

        Returns:
            Args: Command arguments for 'podman build'.
        """
        return cls.get_args("build", *args)

    @classmethod
    def get_save_args(cls, *args: str) -> Args:
        """Construct podman save command arguments.

        Args:
            *args: Additional arguments to append to the save command.

        Returns:
            Args: Command arguments for 'podman save'.
        """
        return cls.get_args("save", *args)

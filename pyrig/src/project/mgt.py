"""Command-line argument and script generation utilities.

This module provides utilities for building command-line arguments and
scripts for running Python modules and CLI commands through the project
management tool (uv). It handles the translation between Python objects
(modules, functions) and the shell commands needed to invoke them.

Key functions:
    - `get_project_mgt_run_cli_cmd_args`: Build args for project CLI commands
    - `get_project_mgt_run_pyrig_cli_cmd_args`: Build args for pyrig CLI commands
    - `get_project_mgt_run_module_args`: Build args for running modules

Attributes:
    PROJECT_MGT: The project management tool name ("uv").
    PROJECT_MGT_RUN_ARGS: Base args for running commands (["uv", "run"]).
    RUN_PYTHON_MODULE_ARGS: Base args for running Python modules.

Example:
    >>> from pyrig.src.project.mgt import get_project_mgt_run_pyrig_cli_cmd_args
    >>> args = get_project_mgt_run_pyrig_cli_cmd_args(create_root)
    >>> args
    ['uv', 'run', 'pyrig', 'create-root']
"""

import logging
from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any

import pyrig
from pyrig.src.modules.package import get_project_name_from_pkg_name, get_src_package
from pyrig.src.string import make_name_from_obj

logger = logging.getLogger(__name__)


PROJECT_MGT = "uv"
"""The project management tool used by pyrig."""

PROJECT_MGT_RUN_ARGS = [PROJECT_MGT, "run"]
"""Base arguments for running commands with the project manager."""

RUN_PYTHON_MODULE_ARGS = ["python", "-m"]
"""Base arguments for running Python modules."""


def get_script_from_args(args: Iterable[str]) -> str:
    """Convert command arguments to a shell script string.

    Args:
        args: Sequence of command arguments.

    Returns:
        A space-joined string suitable for shell execution.
    """
    return " ".join(args)


def get_run_python_module_args(module: ModuleType) -> list[str]:
    """Build arguments to run a Python module with `python -m`.

    Args:
        module: The module to run.

    Returns:
        A list of arguments: ["python", "-m", "module.path"].
    """
    from pyrig.src.modules.module import (  # noqa: PLC0415  # avoid circular import
        make_obj_importpath,
    )

    return [*RUN_PYTHON_MODULE_ARGS, make_obj_importpath(module)]


def get_project_mgt_run_module_args(module: ModuleType) -> list[str]:
    """Build arguments to run a module through the project manager.

    Args:
        module: The module to run.

    Returns:
        A list of arguments: ["uv", "run", "python", "-m", "module.path"].
    """
    return [*PROJECT_MGT_RUN_ARGS, *get_run_python_module_args(module)]


def get_project_mgt_run_cli_cmd_args(
    cmd: Callable[[], Any] | None = None, extra_args: list[str] | None = None
) -> list[str]:
    """Build arguments to run a CLI command from the current project.

    Constructs the command-line arguments needed to invoke a CLI subcommand
    from the current project's entry point.

    Args:
        cmd: Optional CLI command function. If provided, its name is added
            as a subcommand (converted from snake_case to kebab-case).
        extra_args: Additional arguments to append to the command.

    Returns:
        A list of arguments: ["uv", "run", "project-name", "subcommand", ...].
    """
    args = [
        *PROJECT_MGT_RUN_ARGS,
        get_project_name_from_pkg_name(get_src_package().__name__),
    ]
    if cmd is not None:
        name = make_name_from_obj(cmd, capitalize=False)
        args.append(name)
    if extra_args is not None:
        args.extend(extra_args)
    return args


def get_project_mgt_run_pyrig_cli_cmd_args(
    cmd: Callable[[], Any] | None = None,
    extra_args: list[str] | None = None,
) -> list[str]:
    """Build arguments to run a pyrig CLI command.

    Similar to `get_project_mgt_run_cli_cmd_args`, but always uses
    "pyrig" as the project name instead of the current project.

    Args:
        cmd: Optional CLI command function to invoke.
        extra_args: Additional arguments to append.

    Returns:
        A list of arguments: ["uv", "run", "pyrig", "subcommand", ...].
    """
    args = get_project_mgt_run_cli_cmd_args(cmd, extra_args)
    args[len(PROJECT_MGT_RUN_ARGS)] = get_project_name_from_pkg_name(pyrig.__name__)
    return args


def get_project_mgt_run_cli_cmd_script(cmd: Callable[[], Any]) -> str:
    """Get a shell script string to run a project CLI command.

    Args:
        cmd: The CLI command function to invoke.

    Returns:
        A shell-executable command string.
    """
    return get_script_from_args(get_project_mgt_run_cli_cmd_args(cmd))


def get_project_mgt_run_pyrig_cli_cmd_script(cmd: Callable[[], Any]) -> str:
    """Get a shell script string to run a pyrig CLI command.

    Args:
        cmd: The pyrig CLI command function to invoke.

    Returns:
        A shell-executable command string.
    """
    return get_script_from_args(get_project_mgt_run_pyrig_cli_cmd_args(cmd))


def get_python_module_script(module: ModuleType) -> str:
    """Get a shell script string to run a Python module.

    Args:
        module: The module to run.

    Returns:
        A shell command string: "python -m module.path".
    """
    return get_script_from_args(get_run_python_module_args(module))


def get_project_mgt_run_module_script(module: ModuleType) -> str:
    """Get a shell script string to run a module via project manager.

    Args:
        module: The module to run.

    Returns:
        A shell command string: "uv run python -m module.path".
    """
    return get_script_from_args(get_project_mgt_run_module_args(module))

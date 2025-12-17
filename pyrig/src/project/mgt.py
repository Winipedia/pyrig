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
    PROJECT_MGT_RUN_ARGS: Base args for running commands ([*PROJECT_MGT_RUN_ARGS]).
    RUN_PYTHON_MODULE_ARGS: Base args for running Python modules.

Example:
    >>> from pyrig.src.project.mgt import get_project_mgt_run_pyrig_cli_cmd_args
    >>> args = get_project_mgt_run_pyrig_cli_cmd_args(create_root)
    >>> args
    ['uv', 'run', 'pyrig', 'create-root']
"""

import logging
from collections.abc import Callable, Iterable
from typing import Any

import pyrig
from pyrig.src.modules.package import get_project_name_from_pkg_name

logger = logging.getLogger(__name__)


PROJECT_MGT = "uv"
"""The project management tool used by pyrig."""

PROJECT_MGT_RUN_ARGS = [PROJECT_MGT, "run"]
"""Base arguments for running commands with the project manager."""

PROJECT_MGT_RUN_SCRIPT = " ".join(PROJECT_MGT_RUN_ARGS)
"""Base script for running commands with the project manager."""


def get_script_from_args(args: Iterable[str]) -> str:
    """Convert command arguments to a shell script string.

    Args:
        args: Sequence of command arguments.

    Returns:
        A space-joined string suitable for shell execution.
    """
    return " ".join(args)


def get_pyrig_cli_cmd_args(cmd: Callable[..., Any]) -> list[str]:
    """Returns cli args for pyrig cmd execution."""
    return [
        get_project_name_from_pkg_name(pyrig.__name__),
        get_project_name_from_pkg_name(cmd.__name__),  # ty:ignore[unresolved-attribute]
    ]


def get_pyrig_cli_cmd_script(cmd: Callable[..., Any]) -> str:
    """Returns cli script for pyrig cmd execution."""
    args = get_pyrig_cli_cmd_args(cmd)
    return get_script_from_args(args)


def get_project_mgt_run_pyrig_cli_cmd_args(cmd: Callable[..., Any]) -> list[str]:
    """Returns cli args for pyrig cmd execution through project mgt."""
    return [*PROJECT_MGT_RUN_ARGS, *get_pyrig_cli_cmd_args(cmd)]


def get_project_mgt_run_pyrig_cli_cmd_script(cmd: Callable[..., Any]) -> str:
    """Returns cli script for pyrig cmd execution through project mgt."""
    args = get_project_mgt_run_pyrig_cli_cmd_args(cmd)
    return get_script_from_args(args)

"""Project utilities for introspection and manipulation.

This module provides utility functions for working with Python projects
"""

import logging
from collections.abc import Callable, Iterable
from types import ModuleType
from typing import Any

import pyrig
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.package import get_src_package
from pyrig.src.string import make_name_from_obj

logger = logging.getLogger(__name__)


POETRY_ARG = "poetry"

POETRY_RUN_ARGS = [POETRY_ARG, "run"]

RUN_PYTHON_MODULE_ARGS = ["python", "-m"]


def get_script_from_args(args: Iterable[str]) -> str:
    """Get the script from args."""
    return " ".join(args)


def get_run_python_module_args(module: ModuleType) -> list[str]:
    """Get the args to run a module."""
    from pyrig.src.modules.module import (  # noqa: PLC0415  # avoid circular import
        make_obj_importpath,
    )

    return [*RUN_PYTHON_MODULE_ARGS, make_obj_importpath(module)]


def get_poetry_run_module_args(module: ModuleType) -> list[str]:
    """Get the args to run a module."""
    return [*POETRY_RUN_ARGS, *get_run_python_module_args(module)]


def get_poetry_run_cli_cmd_args(
    cmd: Callable[[], Any] | None = None, extra_args: list[str] | None = None
) -> list[str]:
    """Get the args to run the cli of the current project."""
    args = [
        *POETRY_RUN_ARGS,
        PyprojectConfigFile.get_project_name_from_pkg_name(get_src_package().__name__),
    ]
    if cmd is not None:
        name = make_name_from_obj(cmd, capitalize=False)
        args.append(name)
    if extra_args is not None:
        args.extend(extra_args)
    return args


def get_poetry_run_pyrig_cli_cmd_args(
    cmd: Callable[[], Any] | None = None,
    extra_args: list[str] | None = None,
) -> list[str]:
    """Get the args to run pyrig."""
    args = get_poetry_run_cli_cmd_args(cmd, extra_args)
    args[len(POETRY_RUN_ARGS)] = PyprojectConfigFile.get_project_name_from_pkg_name(
        pyrig.__name__
    )
    return args


def get_poetry_run_cli_cmd_script(cmd: Callable[[], Any]) -> str:
    """Get the script to run pyrig."""
    return get_script_from_args(get_poetry_run_cli_cmd_args(cmd))


def get_poetry_run_pyrig_cli_cmd_script(cmd: Callable[[], Any]) -> str:
    """Get the script to run pyrig."""
    return get_script_from_args(get_poetry_run_pyrig_cli_cmd_args(cmd))


def get_python_module_script(module: ModuleType) -> str:
    """Get the script to run a module."""
    return get_script_from_args(get_run_python_module_args(module))


def get_poetry_run_module_script(module: ModuleType) -> str:
    """Get the script to run a module."""
    return get_script_from_args(get_poetry_run_module_args(module))

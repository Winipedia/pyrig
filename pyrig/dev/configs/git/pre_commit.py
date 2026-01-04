"""Configuration management for pre-commit hooks.

Manages .pre-commit-config.yaml with local hooks (system-installed tools) for
code quality: ruff (lint + format), ty (type check), bandit (security), rumdl
(markdown). All hooks run on every commit.

See Also:
    pre-commit framework: https://pre-commit.com/
    ruff: https://docs.astral.sh/ruff/
    bandit: https://bandit.readthedocs.io/
"""

import logging
from pathlib import Path
from typing import Any

from pyrig.dev.configs.base.yaml import YamlConfigFile
from pyrig.dev.management.linter import Linter
from pyrig.dev.management.mdlinter import MDLinter
from pyrig.dev.management.security_checker import SecurityChecker
from pyrig.dev.management.type_checker import TypeChecker
from pyrig.src.processes import (
    Args,
)

logger = logging.getLogger(__name__)


class PreCommitConfigConfigFile(YamlConfigFile):
    """Pre-commit configuration manager.

    Generates .pre-commit-config.yaml with local hooks (system-installed tools)
    for code quality: lint-code (ruff check --fix), format-code (ruff format),
    check-types (ty check), check-security (bandit), check-markdown (rumdl check).

    Examples:
        Generate .pre-commit-config.yaml::

            PreCommitConfigConfigFile()

        Install hooks::

            pre-commit install

    Note:
        Must run `pre-commit install` after generating config.

    See Also:
        pyrig.dev.management.base.base.Args
        pre-commit documentation: https://pre-commit.com/
    """

    @classmethod
    def get_filename(cls) -> str:
        """Get the pre-commit config filename.

        Returns:
            str: ".pre-commit-config" (extension added by parent).
        """
        filename = super().get_filename()
        return f".{filename.replace('_', '-')}"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the parent directory for .pre-commit-config.yaml.

        Returns:
            Path: Project root.
        """
        return Path()

    @classmethod
    def get_hook(
        cls,
        name: str,
        args: Args,
        *,
        language: str = "system",
        pass_filenames: bool = False,
        always_run: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a pre-commit hook configuration.

        Args:
            name (str): Hook identifier and display name.
            args (Args): Command and arguments (converted to string via str()).
            language (str, optional): Hook language. Defaults to "system".
            pass_filenames (bool, optional): Pass staged filenames. Defaults to False.
            always_run (bool, optional): Run on every commit. Defaults to True.
            **kwargs (Any): Additional hook options (files, exclude, stages).

        Returns:
            dict[str, Any]: Hook configuration for .pre-commit-config.yaml.
        """
        hook: dict[str, Any] = {
            "id": name,
            "name": name,
            "entry": str(args),
            "language": language,
            "always_run": always_run,
            "pass_filenames": pass_filenames,
            **kwargs,
        }
        return hook

    @classmethod
    def _get_configs(cls) -> dict[str, Any]:
        """Get the complete pre-commit configuration.

        Generates .pre-commit-config.yaml with local hooks: lint-code (ruff check
        --fix), format-code (ruff format), check-types (ty check), check-security
        (bandit), check-markdown (rumdl check).

        Returns:
            dict[str, Any]: Complete pre-commit configuration.

        Note:
            All hooks use system-installed tools (no remote repos).
        """
        hooks: list[dict[str, Any]] = [
            cls.get_hook(
                "lint-code",
                Linter.L.get_check_fix_args(),
            ),
            cls.get_hook(
                "format-code",
                Linter.L.get_format_args(),
            ),
            cls.get_hook(
                "check-types",
                TypeChecker.L.get_check_args(),
            ),
            cls.get_hook(
                "check-security",
                SecurityChecker.L.get_run_with_config_args(),
            ),
            cls.get_hook(
                "check-markdown",
                MDLinter.L.get_check_fix_args(),
            ),
        ]
        return {
            "repos": [
                {
                    "repo": "local",
                    "hooks": hooks,
                },
            ]
        }

"""Configuration management for prek hooks.

Manages prek.toml with local hooks (system-installed tools) for
code quality: ruff (lint + format), ty (type check), bandit (security), rumdl
(markdown). All hooks run on every commit.

See Also:
    prek: https://github.com/j178/prek
    ruff: https://docs.astral.sh/ruff/
    bandit: https://bandit.readthedocs.io/
"""

from pathlib import Path
from typing import Any

from pyrig.core.subprocesses import (
    Args,
)
from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.base.toml import TomlConfigFile
from pyrig.rig.tools.linter import Linter
from pyrig.rig.tools.mdlinter import MDLinter
from pyrig.rig.tools.pre_committer import PreCommitter
from pyrig.rig.tools.security_checker import SecurityChecker
from pyrig.rig.tools.type_checker import TypeChecker


class PreCommitterConfigFile(TomlConfigFile):
    """Prek configuration manager.

    Generates prek.toml with local hooks (system-installed tools)
    for code quality: format-code (ruff format), lint-code (ruff check --fix),
    check-types (ty check), check-security (bandit), check-markdown (rumdl check).

    Examples:
        Generate prek.toml::

            PreCommitterConfigFile.I.validate()

        Install hooks::

            prek install

    Note:
        Must run `prek install` after generating config.

    See Also:
        pyrig.src.processes.Args
        prek documentation: https://github.com/j178/prek
    """

    def parent_path(self) -> Path:
        """Get parent directory (project root)."""
        return Path()

    def stem(self) -> str:
        """Get filename stem."""
        return PreCommitter.I.name()

    def hook(
        self,
        name: str,
        args: Args,
        *,
        language: str = "system",
        pass_filenames: bool = False,
        always_run: bool = True,
        **kwargs: Any,
    ) -> ConfigDict:
        """Create a prek hook configuration.

        Args:
            name (str): Hook identifier and display name.
            args (Args): Command and arguments (converted to string via str()).
            language (str, optional): Hook language. Defaults to "system".
            pass_filenames (bool, optional): Pass staged filenames. Defaults to False.
            always_run (bool, optional): Run on every commit. Defaults to True.
            **kwargs (Any): Additional hook options (files, exclude, stages).

        Returns:
            ConfigDict: Hook configuration for prek.toml.
        """
        hook: ConfigDict = {
            "id": name,
            "name": name,
            "entry": str(args),
            "language": language,
            "always_run": always_run,
            "pass_filenames": pass_filenames,
            **kwargs,
        }
        return hook

    def _configs(self) -> ConfigDict:
        """Get the complete prek configuration.

        Generates prek.toml with local hooks: format-code (ruff format),
        lint-code (ruff check --fix), check-types (ty check), check-security
        (bandit), check-markdown (rumdl check).

        Returns:
            ConfigDict: Complete prek configuration.

        Note:
            All hooks use system-installed tools (no remote repos).
        """
        hooks: list[ConfigDict] = [
            self.hook(
                "format-code",
                Linter.I.format_args(),
            ),
            self.hook(
                "lint-code",
                Linter.I.check_fix_args(),
            ),
            self.hook(
                "check-types",
                TypeChecker.I.check_args(),
            ),
            self.hook(
                "check-security",
                SecurityChecker.I.run_with_config_args(),
            ),
            self.hook(
                "lint-markdown",
                MDLinter.I.check_fix_args(),
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

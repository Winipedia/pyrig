"""Configuration management for prek pre-commit hooks.

Manages ``prek.toml`` with a local hook repository containing system-installed
tools that run on every commit to enforce code quality across formatting,
linting, type checking, security, and Markdown style.
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
    """Manages ``prek.toml`` for pre-commit hook configuration.

    Generates ``prek.toml`` at the project root with a single ``local``
    repository entry containing five hooks that cover the full code-quality
    pipeline.  All hooks use ``language: system``, meaning the tools must be
    installed on the host.

    Hooks generated:
        - ``format-code``: ``ruff format`` — auto-formats Python source.
        - ``lint-code``: ``ruff check --fix`` — lints and auto-fixes Python source.
        - ``check-types``: ``ty check`` — static type checking.
        - ``check-security``: ``bandit`` with project config — security scanning.
        - ``lint-markdown``: ``rumdl check --fix`` — Markdown style checking.

    Examples:
        Generate prek.toml::

            PreCommitterConfigFile.I.validate()

        Install hooks::

            prek install

    Note:
        Run ``prek install`` once after generating the config to register the
        hooks with git.
    """

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return the config filename stem, producing ``prek.toml``."""
        return PreCommitter.I.name()

    def _configs(self) -> ConfigDict:
        """Build the complete ``prek.toml`` configuration.

        Constructs a single ``local`` repository entry containing five hooks
        that enforce the full code-quality pipeline on every commit:

        Returns:
            Top-level prek.toml structure containing the ``repos`` list.
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
        """Build a single prek hook configuration entry.

        Creates a hook dict for inclusion in the ``hooks`` list of a
        ``repos`` entry in ``prek.toml``.  The hook ``id`` and ``name``
        fields are both set to ``name``; the ``entry`` field is the
        space-separated string representation of ``args``.

        Args:
            name: Hook identifier used for both ``id`` and ``name`` fields.
            args: Command and arguments for the hook ``entry`` field.
                Converted to a space-separated string via ``str()``.
            language: Execution environment for the hook.  ``"system"`` means
                the tool must already be installed on the host rather than
                fetched remotely by prek.  Defaults to ``"system"``.
            pass_filenames: When ``True``, prek appends staged filenames to the
                hook command at runtime.  Defaults to ``False``.
            always_run: When ``True``, the hook runs on every commit regardless
                of whether any files match the optional ``files`` filter.
                Defaults to ``True``.
            **kwargs: Additional prek hook fields passed through verbatim
                (e.g. ``files``, ``exclude``, ``stages``).

        Returns:
            Hook configuration dict ready for inclusion in the ``hooks`` list.
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

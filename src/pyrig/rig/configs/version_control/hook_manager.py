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
from pyrig.rig.tools.linting.markdown import MarkdownLinter
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.security_checker import SecurityChecker
from pyrig.rig.tools.type_checker import TypeChecker
from pyrig.rig.tools.version_control.hook_manager import (
    VersionControlHookManager,
)


class VersionControlHookManagerConfigFile(TomlConfigFile):
    """Manages ``prek.toml`` for pre-commit hook configuration.

    Generates ``prek.toml`` at the project root with a single ``local``
    repository entry containing hooks that cover the full code-quality
    pipeline.  All hooks use ``language: system``, meaning the tools must be
    installed on the host.

    Examples:
        Generate prek.toml::

            VersionControlHookManagerConfigFile.I.validate()

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
        return VersionControlHookManager.I.name()

    def _configs(self) -> ConfigDict:
        """Build the complete ``prek.toml`` configuration.

        Constructs a single ``local`` repository entry containing hooks
        that enforce the full code-quality pipeline on the project via hooks.

        Returns:
            Top-level prek.toml structure containing the prek configuration.
        """
        hooks: list[ConfigDict] = [
            self.hook(
                "format-code",
                PythonLinter.I.format_args(),
            ),
            self.hook(
                "lint-code",
                PythonLinter.I.check_fix_args(),
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
                MarkdownLinter.I.check_fix_args(),
            ),
            self.hook(
                "update-package-manager",
                PackageManager.I.update_self_args(),
                stages=["pre-push"],
            ),
            self.hook(
                "update-dependencies",
                PackageManager.I.update_dependencies_args(),
                stages=["pre-push", "post-checkout", "post-merge", "post-rewrite"],
            ),
            self.hook(
                "install-dependencies",
                PackageManager.I.install_dependencies_args(),
                stages=["pre-push", "post-checkout", "post-merge", "post-rewrite"],
            ),
        ]
        hook_types = {stage for hook in hooks for stage in hook["stages"]}
        return {
            "default_install_hook_types": list(hook_types),
            "repos": [
                {
                    "repo": "local",
                    "hooks": hooks,
                },
            ],
        }

    def hook(  # noqa: PLR0913
        self,
        name: str,
        args: Args,
        *,
        language: str = "system",
        pass_filenames: bool = False,
        always_run: bool = True,
        stages: list[str] | None = None,
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
            stages: Iterable of stages in which the hook should run.
            **kwargs: Additional prek hook fields passed through verbatim
                (e.g. ``files``, ``exclude``, ``stages``).

        Returns:
            Hook configuration dict ready for inclusion in the ``hooks`` list.
        """
        if stages is None:
            stages = ["pre-commit"]
        hook: ConfigDict = {
            "id": name,
            "name": name,
            "entry": str(args),
            "language": language,
            "always_run": always_run,
            "pass_filenames": pass_filenames,
            "stages": stages,
            **kwargs,
        }
        return hook

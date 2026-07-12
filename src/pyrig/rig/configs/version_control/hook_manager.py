"""Configuration management for version control hooks.

Declares the hook pipeline that enforces code quality and dependency hygiene
at various git stages.
"""

from pathlib import Path
from typing import Any

from pyrig.core.strings import reformat_name
from pyrig.core.subprocesses import (
    Args,
)
from pyrig.rig.cli.subcommands import sync
from pyrig.rig.configs.base.toml import TOMLConfigFile
from pyrig.rig.tools.dependencies.auditor import DependencyAuditor
from pyrig.rig.tools.dependencies.checker import DependencyChecker
from pyrig.rig.tools.linting.markdown import MarkdownLinter
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.linting.security import SecurityLinter
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.secrets_checker import SecretsChecker
from pyrig.rig.tools.spell_checker import SpellChecker
from pyrig.rig.tools.type_checker import TypeChecker
from pyrig.rig.tools.version_control.hook_manager import (
    VersionControlHookManager,
)


class VersionControlHookManagerConfigFile(TOMLConfigFile):
    """Manages `prek.toml` for version control hook configuration.

    Declares a single `local` repository entry containing hooks that cover
    the full code-quality pipeline, all running against tools already
    installed on the host rather than fetched by prek.

    Note:
        Run `prek install` once after generating the config to register the
        hooks with git.
    """

    def _configs(self) -> dict[str, Any]:
        """Build the required `prek.toml` structure.

        Returns:
            Dict with the default hook install types and the `repos` entry
            wrapping the configured hooks.
        """
        return {
            "default_install_hook_types": self.hook_types(),
            "repos": [
                {
                    "repo": "local",
                    "hooks": self.hooks(),
                },
            ],
        }

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return `"prek"`, the config filename stem."""
        return VersionControlHookManager.I.name()

    def hook_types(self) -> list[str]:
        """Return the sorted, deduplicated git stages used across all hooks."""
        return sorted({stage for hook in self.hooks() for stage in hook["stages"]})

    def hooks(self) -> list[dict[str, Any]]:
        """Return every hook configuration entry in the pipeline."""
        return [
            self.hook(
                "format-code",
                PackageManager.I.run_args(*PythonLinter.I.format_args()),
                stages=["pre-commit"],
            ),
            self.hook(
                "lint-code",
                PackageManager.I.run_args(*PythonLinter.I.check_fix_args()),
                stages=["pre-commit"],
            ),
            self.hook(
                "lint-markdown",
                PackageManager.I.run_args(*MarkdownLinter.I.check_fix_args()),
                stages=["pre-commit"],
            ),
            self.hook(
                "fix-spelling",
                PackageManager.I.run_args(*SpellChecker.I.check_fix_args()),
                stages=["pre-commit"],
            ),
            self.hook(
                "check-secrets",
                PackageManager.I.run_args(*SecretsChecker.I.check_args()),
                stages=["pre-commit"],
            ),
            self.hook(
                "check-security",
                PackageManager.I.run_args(*SecurityLinter.I.check_args()),
                stages=["pre-commit"],
            ),
            self.hook(
                "check-types",
                PackageManager.I.run_args(*TypeChecker.I.check_args()),
                stages=["pre-commit"],
            ),
            self.hook(
                "check-dependencies",
                PackageManager.I.run_args(*DependencyChecker.I.check_args()),
                stages=["pre-commit"],
            ),
            self.hook(
                "synchronize-project",
                PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=sync)),
                stages=["pre-commit"],
            ),
            self.hook(
                "update-package-manager",
                PackageManager.I.update_self_args(),
                stages=["pre-push", "post-checkout", "post-merge", "post-rewrite"],
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
            self.hook(
                "audit-dependencies",
                PackageManager.I.run_args(*DependencyAuditor.I.audit_args()),
                stages=["pre-push", "post-checkout", "post-merge", "post-rewrite"],
            ),
        ]

    def hook(  # noqa: PLR0913
        self,
        id_: str,
        args: Args,
        *,
        stages: list[str],
        language: str = "system",
        pass_filenames: bool = False,
        always_run: bool = True,
    ) -> dict[str, Any]:
        """Build a single prek hook configuration entry.

        The `name` field is derived from `id_` (e.g. `"format-code"` becomes
        `"format code"`, matching the lowercase, space-separated naming
        convention used across the pre-commit hook ecosystem); the `entry`
        field is `args` converted to a space-separated string.

        Args:
            id_: Hook identifier, used as-is for the `id` field and with
                hyphens replaced by spaces for the `name` field.
            args: Command and arguments for the hook `entry` field.
            language: Execution environment for the hook. `"system"` means
                the tool must already be installed on the host rather than
                fetched remotely by prek. Defaults to `"system"`.
            pass_filenames: When `True`, prek appends the matched filenames
                to the hook command at runtime. Defaults to `False`.
            always_run: When `True`, the hook runs on every commit regardless
                of whether any files match the optional `files` filter.
                Defaults to `True`.
            stages: Git stages in which the hook should run.

        Returns:
            Hook configuration dict ready for inclusion in the `hooks` list.
        """
        hook: dict[str, Any] = {
            "id": id_,
            "name": reformat_name(id_, split_on="-", join_on=" "),
            "entry": str(args),
            "language": language,
            "always_run": always_run,
            "pass_filenames": pass_filenames,
            "stages": stages,
        }
        return hook

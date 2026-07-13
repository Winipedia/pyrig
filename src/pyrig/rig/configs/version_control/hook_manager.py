"""Configuration management for version control hooks.

Declares the hook pipeline that enforces code quality and dependency hygiene
at various git stages.
"""

from collections.abc import Iterable
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
from pyrig.rig.tools.formatting.shell import ShellFormatter
from pyrig.rig.tools.linting.markdown import MarkdownLinter
from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.linting.security import SecurityLinter
from pyrig.rig.tools.linting.shell import ShellLinter
from pyrig.rig.tools.linting.yaml import YAMLLinter
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.security.secrets import SecretsChecker
from pyrig.rig.tools.spelling.checker import SpellChecker
from pyrig.rig.tools.typing.checker import TypeChecker
from pyrig.rig.tools.version_control.hook_manager import (
    VersionControlHookManager,
)


class VersionControlHookManagerConfigFile(TOMLConfigFile):
    """Configuration manager for `prek.toml`, the version control hook pipeline.

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
        generate_hooks = self.generate_hooks(priority=0)
        update_types_hooks = self.update_types_hooks(
            priority=self.highest_priority(generate_hooks) + 1,
        )
        update_type_hooks = self.update_type_hooks(
            priority=self.highest_priority(update_types_hooks) + 1,
        )
        check_hooks = self.check_hooks(
            priority=self.highest_priority(update_type_hooks) + 1,
        )
        transition_hooks = self.transition_hooks(priority=0)
        return [
            *generate_hooks,
            *update_types_hooks,
            *update_type_hooks,
            *check_hooks,
            *transition_hooks,
        ]

    def transition_hooks(self, priority: int) -> list[dict[str, Any]]:
        """Return the hooks that run on push, checkout, merge, and rewrite.

        Kept strictly sequential: updating the package manager must precede
        upgrading the lockfile, which must precede installing dependencies,
        which must precede auditing them.

        Every hook here scans or acts on the whole project rather than
        specific files, so all four override prek's defaults to
        `pass_filenames=False, always_run=True`.

        Args:
            priority: Priority assigned to the first hook in the chain; each
                subsequent hook runs one priority higher.

        Returns:
            Hook configuration entries for the transition-stage pipeline.
        """
        transition_stages = [
            "post-checkout",
            "post-merge",
            "post-rewrite",
            "pre-push",
        ]
        return [
            self.hook(
                "update-package-manager",
                PackageManager.I.update_self_args(),
                stages=transition_stages,
                priority=(update_package_manager_priority := priority),
                pass_filenames=False,
                always_run=True,
            ),
            self.hook(
                "update-dependencies",
                PackageManager.I.update_dependencies_args(),
                stages=transition_stages,
                priority=(
                    update_dependencies_priority := update_package_manager_priority + 1
                ),
                pass_filenames=False,
                always_run=True,
            ),
            self.hook(
                "install-dependencies",
                PackageManager.I.install_dependencies_args(),
                stages=transition_stages,
                priority=(
                    install_dependencies_priority := update_dependencies_priority + 1
                ),
                pass_filenames=False,
                always_run=True,
            ),
            self.hook(
                "audit-dependencies",
                PackageManager.I.run_args(*DependencyAuditor.I.check_args()),
                stages=transition_stages,
                priority=install_dependencies_priority + 1,
                pass_filenames=False,
                always_run=True,
            ),
        ]

    def check_hooks(self, priority: int) -> list[dict[str, Any]]:
        """Return the read-only checks that validate the fully-fixed project.

        All five checks share one priority: none of them mutate files or
        depend on each other, so prek can run them concurrently.
        `check-shell` (ShellCheck) belongs here rather than in
        `update_type_hooks` because ShellCheck has no autofix mode; it only
        ever reports, so it is a check, not a fixer, even though its target
        file type is otherwise single-file-type like Python/Markdown/YAML.

        `check-secrets` and `check-security` rely on prek's default of
        passing matched filenames, for opposite reasons from each other:
        `detect-secrets-hook` does nothing at all when given zero files
        (it does not scan a default target the way most of these tools
        do), while `bandit` scans whichever files it's told to look at
        and otherwise wastes a whole source-tree walk. `check-security`'s
        `files` filter is scoped to the package root rather than every
        `.py` file, matching bandit's previous `-r <package root>` scan:
        bandit has no notion of test code, so it flags things like assert
        statements (`B101`) that `pyproject.toml` already tells Ruff to
        ignore under `tests/`. `check-types` and `check-dependencies`
        override that default back to `pass_filenames=False,
        always_run=True`: both need whole-program analysis (unresolved
        imports, cross-file usages) that restricting to changed files
        would silently break.

        Args:
            priority: Priority shared by all five check hooks.

        Returns:
            Hook configuration entries for the check stage.
        """
        return [
            self.hook(
                "check-secrets",
                PackageManager.I.run_args(*SecretsChecker.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
            ),
            self.hook(
                "check-security",
                PackageManager.I.run_args(*SecurityLinter.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
                files=SecurityLinter.I.regex(),
            ),
            self.hook(
                "check-types",
                PackageManager.I.run_args(*TypeChecker.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
                pass_filenames=False,
                always_run=True,
            ),
            self.hook(
                "check-dependencies",
                PackageManager.I.run_args(*DependencyChecker.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
                pass_filenames=False,
                always_run=True,
            ),
            self.hook(
                "check-shell",
                PackageManager.I.run_args(*ShellLinter.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
                files=ShellLinter.I.regex(),
            ),
        ]

    def update_type_hooks(self, priority: int) -> list[dict[str, Any]]:
        r"""Return the hooks that each fix a single file type.

        Every hook here relies on prek's default of passing matched
        filenames rather than scanning the whole project: each tool's own
        scope is a single, self-contained file type with no cross-file
        dependencies to miss, unlike `check-types`/`check-dependencies` in
        `check_hooks`, which override that default. `ruff format` in
        particular *requires* this: given a Markdown file directly it
        errors outright rather than skipping it, so `format-python`'s
        `\.pyi?$` filter isn't just an optimization.

        Python linting must precede Python formatting, since autofixes can
        leave code that still needs reformatting. Every other hook here
        shares the base priority: `lint-yaml`, `lint-markdown`, and
        `format-shell` each pass a `files` filter scoped to their own
        wholly disjoint file type, so prek never hands any of them a file
        one of the others would also touch - not just because Ruff
        ignores Markdown by default today, but because prek's own file
        matching would keep a `.md` file from ever reaching `ruff format`
        even if `preview` mode and `extend-include` were turned on in
        `pyproject.toml` to format Python code fences inside Markdown.

        Args:
            priority: Priority shared by every hook here except
                `format-python`, which runs one priority after
                `lint-python`.

        Returns:
            Hook configuration entries for the single-file-type fix stage.
        """
        return [
            self.hook(
                "lint-python",
                PackageManager.I.run_args(*PythonLinter.I.check_fix_args()),
                stages=["pre-commit"],
                priority=(lint_python_priority := priority),
                files=PythonLinter.I.regex(),
            ),
            self.hook(
                "format-python",
                PackageManager.I.run_args(*PythonLinter.I.format_args()),
                stages=["pre-commit"],
                priority=lint_python_priority + 1,
                files=PythonLinter.I.regex(),
            ),
            self.hook(
                "lint-markdown",
                PackageManager.I.run_args(*MarkdownLinter.I.check_fix_args()),
                stages=["pre-commit"],
                priority=priority,
                files=MarkdownLinter.I.regex(),
            ),
            self.hook(
                "lint-yaml",
                PackageManager.I.run_args(*YAMLLinter.I.check_fix_args()),
                stages=["pre-commit"],
                priority=priority,
                files=YAMLLinter.I.regex(),
            ),
            self.hook(
                "format-shell",
                PackageManager.I.run_args(*ShellFormatter.I.format_args()),
                stages=["pre-commit"],
                priority=priority,
                files=ShellFormatter.I.regex(),
            ),
        ]

    def update_types_hooks(self, priority: int) -> list[dict[str, Any]]:
        """Return the hook that fixes spelling across every file type.

        Runs after generation and before `update_type_hooks`, since spelling
        fixes can touch any file, including ones the single-file-type
        fixers fix afterward. Scans the whole project itself rather than
        specific files, so it overrides prek's defaults accordingly.

        Args:
            priority: Priority assigned to this stage's hook.

        Returns:
            Hook configuration entries for the cross-file-type fix stage.
        """
        return [
            self.hook(
                "fix-spelling",
                PackageManager.I.run_args(*SpellChecker.I.check_fix_args()),
                stages=["pre-commit"],
                priority=priority,
                pass_filenames=False,
                always_run=True,
            ),
        ]

    def generate_hooks(self, priority: int) -> list[dict[str, Any]]:
        """Return the hook that regenerates the project's managed files.

        Runs at the lowest priority so every hook after it - fixers and
        checks alike - operates on canonical, up-to-date project files.
        Regenerates the whole project itself rather than acting on
        specific files, so it overrides prek's defaults accordingly.

        Args:
            priority: Priority assigned to this stage's hook.

        Returns:
            Hook configuration entries for the generation stage.
        """
        return [
            self.hook(
                "synchronize-project",
                PackageManager.I.run_args(*Pyrigger.I.cmd_args(cmd=sync)),
                stages=["pre-commit"],
                priority=priority,
                pass_filenames=False,
                always_run=True,
            ),
        ]

    def highest_priority(self, hooks: Iterable[dict[str, Any]]) -> int:
        """Return the highest `priority` value among the given hooks.

        Args:
            hooks: Hook configuration entries to inspect.

        Returns:
            The maximum `priority` value found.
        """
        return max(hook["priority"] for hook in hooks)

    def hook(  # noqa: PLR0913
        self,
        id_: str,
        args: Args,
        *,
        stages: list[str],
        priority: int,
        language: str = "system",
        pass_filenames: bool = True,
        always_run: bool = False,
        files: str | None = None,
    ) -> dict[str, Any]:
        """Build a single prek hook configuration entry.

        The `name` field is derived from `id_` (e.g. `"format-code"` becomes
        `"format code"`, matching the lowercase, space-separated naming
        convention used across the pre-commit hook ecosystem); the `entry`
        field is `args` converted to a space-separated string.

        `pass_filenames` and `always_run` mirror prek's own defaults (`True`
        and `False` respectively), and like `files`, are only written into
        the hook entry when the caller overrides away from that default -
        matching how the tools' own upstream `.pre-commit-hooks.yaml`
        manifests read (e.g. `bandit`'s omits both entirely, `deptry`'s
        sets both since it wants the opposite of each).

        Args:
            id_: Hook identifier, used as-is for the `id` field and with
                hyphens replaced by spaces for the `name` field.
            args: Command and arguments for the hook `entry` field.
            priority: Hook execution priority. Hooks with lower values run
                first. Defaults to `0`.
            language: Execution environment for the hook. `"system"` means
                the tool must already be installed on the host rather than
                fetched remotely by prek. Defaults to `"system"`.
            pass_filenames: When `True`, prek appends the matched filenames
                to the hook command at runtime. Defaults to `True`, prek's
                own default.
            always_run: When `True`, the hook runs on every commit regardless
                of whether any files match the optional `files` filter. Set
                `True` for a tool that scans the whole project itself
                rather than specific files. Defaults to `False`, prek's own
                default.
            stages: Git stages in which the hook should run.
            files: Regex restricting which tracked files count as a match
                for this hook. Needed alongside the default
                `pass_filenames=True` for a tool that cannot scan a
                directory itself (e.g. ShellCheck) or that would otherwise
                need to walk the whole project (e.g. shfmt, which does not
                respect `.gitignore`). Omitted from the hook entry entirely
                when `None`, since TOML has no null value to serialize it
                as.

        Returns:
            Hook configuration dict ready for inclusion in the `hooks` list.
        """
        hook: dict[str, Any] = {
            "id": id_,
            "name": reformat_name(id_, split_on="-", join_on=" "),
            "entry": str(args),
            "language": language,
        }
        if files is not None:
            hook["files"] = files
        if always_run:
            hook["always_run"] = always_run
        if not pass_filenames:
            hook["pass_filenames"] = pass_filenames
        hook["stages"] = stages
        hook["priority"] = priority
        return hook

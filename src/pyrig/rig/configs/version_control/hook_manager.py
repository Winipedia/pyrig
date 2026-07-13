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
from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.dependencies.auditor import DependencyAuditor
from pyrig.rig.tools.dependencies.checker import DependencyChecker
from pyrig.rig.tools.formatting.json import JSONFormatter
from pyrig.rig.tools.formatting.shell import ShellFormatter
from pyrig.rig.tools.linting.json import JSONLinter
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
        hooks = self.hooks()
        return {
            "default_install_hook_types": self.hook_types(hooks),
            "repos": [
                {
                    "repo": "local",
                    "hooks": hooks,
                },
            ],
        }

    def parent_path(self) -> Path:
        """Return the project root directory."""
        return Path()

    def stem(self) -> str:
        """Return `"prek"`, the config filename stem."""
        return VersionControlHookManager.I.name()

    def hook_types(self, hooks: list[dict[str, Any]]) -> list[str]:
        """Return the sorted, deduplicated git stages used across all hooks."""
        return sorted({stage for hook in hooks for stage in hook["stages"]})

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

        All six checks share one priority: none of them mutate files or
        depend on each other, so prek can run them concurrently.
        `check-shell` (ShellCheck) and `check-json` (check-json) belong here
        rather than in `update_type_hooks` because neither has an autofix
        mode; they only ever report, so they are checks, not fixers, even
        though their target file types are otherwise single-file-type like
        Python/Markdown/YAML.

        `check-secrets` and `check-security` rely on prek's default of
        passing matched filenames, for opposite reasons from each other:
        `detect-secrets-hook` does nothing at all when given zero files
        (it does not scan a default target the way most of these tools
        do), while `bandit` scans whichever files it's told to look at
        and otherwise wastes a whole source-tree walk. `check-secrets`'s
        `types` filter costs no real coverage even though secrets can hide
        in binary artifacts: `detect-secrets-hook` requires a file to
        decode as text to scan it at all, confirmed by testing a secret
        embedded in genuinely binary content, which it missed regardless
        of the file's extension. `check-security`'s `-c pyproject.toml`
        reads that file's `[tool.bandit]` section (`exclude_dirs =
        ["tests"]`) rather than restricting `types`: bandit has no notion
        of test code, so it would otherwise flag things like assert
        statements (`B101`) that `pyproject.toml` already tells Ruff to
        ignore under `tests/`.

        `check-types` and `check-dependencies` keep `pass_filenames=False`
        (both need whole-program analysis - unresolved imports, cross-file
        usages - that restricting the actual scan to changed files would
        silently break) but do *not* override `always_run`: their type
        filter still gates whether the hook runs at all, skipping it
        entirely on a commit that touches none of its relevant file types,
        since a commit that changes no Python (and, for
        `check-dependencies`, no `pyproject.toml` either) cannot possibly
        have introduced the kind of breakage these two exist to catch.
        `check-dependencies` needs `types_or` specifically, since `python`
        and `pyproject` are genuine alternatives, either one enough on its
        own to warrant a re-check; every other hook here has only one
        relevant type, so plain `types` is enough (see `PythonLinter.types`
        for why that one type is just `python`, not `python`/`pyi`).

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
                types=SecretsChecker.I.types(),
            ),
            self.hook(
                "check-security",
                PackageManager.I.run_args(
                    *SecurityLinter.I.check_config_args(PyprojectConfigFile.I.path()),
                ),
                stages=["pre-commit"],
                priority=priority,
                types=SecurityLinter.I.types(),
            ),
            self.hook(
                "check-types",
                PackageManager.I.run_args(*TypeChecker.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
                types=TypeChecker.I.types(),
                pass_filenames=False,
            ),
            self.hook(
                "check-dependencies",
                PackageManager.I.run_args(*DependencyChecker.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
                types_or=DependencyChecker.I.types(),
                pass_filenames=False,
            ),
            self.hook(
                "check-shell",
                PackageManager.I.run_args(*ShellLinter.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
                types=ShellLinter.I.types(),
            ),
            self.hook(
                "check-json",
                PackageManager.I.run_args(*JSONLinter.I.check_args()),
                stages=["pre-commit"],
                priority=priority,
                types=JSONLinter.I.types(),
            ),
        ]

    def update_type_hooks(self, priority: int) -> list[dict[str, Any]]:
        """Return the hooks that each fix a single file type.

        Every hook here relies on prek's default of passing matched
        filenames rather than scanning the whole project: each tool's own
        scope is a single, self-contained file type with no cross-file
        dependencies to miss, unlike `check-types`/`check-dependencies` in
        `check_hooks`, which override that default. `ruff format` in
        particular *requires* this: given a Markdown file directly it
        errors outright rather than skipping it, so `format-python`'s
        `types=["python"]` filter isn't just an optimization.

        Python linting must precede Python formatting, since autofixes can
        leave code that still needs reformatting. Every other hook here
        shares the base priority: `lint-yaml`, `lint-markdown`,
        `format-shell`, and `format-json` each pass a `types` filter scoped
        to their own wholly disjoint file type, so prek never hands any of
        them a file one of the others would also touch - not just because
        Ruff ignores Markdown by default today, but because prek's own file
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
                types=PythonLinter.I.types(),
            ),
            self.hook(
                "format-python",
                PackageManager.I.run_args(*PythonLinter.I.format_args()),
                stages=["pre-commit"],
                priority=lint_python_priority + 1,
                types=PythonLinter.I.types(),
            ),
            self.hook(
                "format-shell",
                PackageManager.I.run_args(*ShellFormatter.I.format_args()),
                stages=["pre-commit"],
                priority=priority,
                types=ShellFormatter.I.types(),
            ),
            self.hook(
                "lint-yaml",
                PackageManager.I.run_args(*YAMLLinter.I.check_fix_args()),
                stages=["pre-commit"],
                priority=priority,
                types=YAMLLinter.I.types(),
            ),
            self.hook(
                "format-json",
                PackageManager.I.run_args(*JSONFormatter.I.format_args()),
                stages=["pre-commit"],
                priority=priority,
                types=JSONFormatter.I.types(),
            ),
            self.hook(
                "lint-markdown",
                PackageManager.I.run_args(*MarkdownLinter.I.check_fix_args()),
                stages=["pre-commit"],
                priority=priority,
                types=MarkdownLinter.I.types(),
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
                types=SpellChecker.I.types(),
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
        types: list[str] | None = None,
        types_or: list[str] | None = None,
        pass_filenames: bool = True,
        always_run: bool = False,
    ) -> dict[str, Any]:
        """Build a single prek hook configuration entry.

        The `name` field is derived from `id_` (e.g. `"format-code"` becomes
        `"format code"`, matching the lowercase, space-separated naming
        convention used across the pre-commit hook ecosystem); the `entry`
        field is `args` converted to a space-separated string.

        `pass_filenames` and `always_run` mirror prek's own defaults (`True`
        and `False` respectively), and like `types`/`types_or`, are only
        written into the hook entry when the caller overrides away from
        that default - matching how the tools' own upstream
        `.pre-commit-hooks.yaml` manifests read (e.g. `bandit`'s omits both
        entirely, `deptry`'s sets both since it wants the opposite of each).

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
                of whether any files match `types`/`types_or`. Set `True`
                only when even `types`/`types_or` shouldn't gate whether the
                hook runs at all (e.g. a hook with no file-type concept at
                all). Defaults to `False`, prek's own default.
            stages: Git stages in which the hook should run.
            types: Optional list of file types a matched file must have
                *all* of. Defaults to `None`, meaning no type filter is
                applied.
            types_or: Optional list of file types a matched file must have
                *at least one* of - needed instead of `types` whenever the
                list has more than one entry, since a file can't carry two
                mutually exclusive tags (e.g. `python` and `pyi`) at once.
                Defaults to `None`, meaning no type filter is applied.

        Returns:
            Hook configuration dict ready for inclusion in the `hooks` list.
        """
        hook: dict[str, Any] = {
            "id": id_,
            "name": reformat_name(id_, split_on="-", join_on=" "),
            "entry": str(args),
            "language": language,
        }
        if types is not None:
            hook["types"] = types
        if types_or is not None:
            hook["types_or"] = types_or
        if always_run:
            hook["always_run"] = always_run
        if not pass_filenames:
            hook["pass_filenames"] = pass_filenames
        hook["stages"] = stages
        hook["priority"] = priority
        return hook

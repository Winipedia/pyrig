"""Argument construction for the prek pre-commit hook manager CLI."""

from collections.abc import Callable, Iterable
from types import MethodType
from typing import Any, cast

from pyrig_runtime.core.strings import snake_to_kebab_case

from pyrig.core.strings import reformat_name
from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class VersionControlHookManager(Tool):
    """Wrapper for the prek pre-commit hook manager.

    Builds `Args` for the two primary prek operations: installing hooks into
    the local git repository and running hooks against files.
    """

    def group(self) -> str:
        """Return the badge group this tool belongs to.

        `prek` doesn't itself inspect or rewrite any file; it's the
        orchestrator that invokes the actual linters, formatters, and
        checkers as git hooks. That's the same role `VersionController`
        (`git`) and `PackageManager` (`uv`) play, both grouped here rather
        than under `Group.CODE_QUALITY`.

        Returns:
            `Group.TOOLING`.
        """
        return Group.TOOLING

    def image_url(self) -> str:
        """Return the badge image URL for prek.

        Returns:
            The URL of the badge image as a string.
        """
        return "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json"

    def link_url(self) -> str:
        """Return the link URL for prek.

        Returns:
            The URL of the prek project page as a string.
        """
        return "https://github.com/j178/prek"

    def name(self) -> str:
        """Return the tool's command name.

        Returns:
            `'prek'`.
        """
        return "prek"

    def install_args(self, *args: str) -> Args:
        """Build arguments for `prek install`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `prek install [args]`.
        """
        return self.args("install", *args)

    def run_all_files_all_hooks_args(self, *args: str) -> Args:
        """Build arguments to run all hooks against every file.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `prek run --all-files --group all [args]`.
        """
        return self.run_all_files_group_args(*args, group=self.group_all())

    def run_all_files_group_args(self, *args: str, group: str) -> Args:
        """Build arguments to run hooks of a given group against every file.

        Args:
            *args: Additional arguments appended to the command.
            group: The hook group to run (e.g. `"tooling"`).

        Returns:
            Args for `prek run --all-files --group <group> [args]`.
        """
        return self.run_all_files_args("--group", group, *args)

    def run_all_files_args(self, *args: str) -> Args:
        """Build arguments to run hooks against every file in the project.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `prek run --all-files [args]`.
        """
        return self.run_args("--all-files", *args)

    def run_args(self, *args: str) -> Args:
        """Build base arguments for `prek run`.

        Args:
            *args: Additional arguments appended to the command.

        Returns:
            Args for `prek run [args]`.
        """
        return self.args("run", *args)

    def subclasses_hooks(self) -> list[dict[str, Any]]:
        """Return every concrete tool's hooks, sorted for a deterministic pipeline.

        Returns:
            Every hook returned by `version_control_hooks()` across all
            concrete `Tool` subclasses, sorted via `sort_hooks`.
        """
        return self.sort_hooks(
            [
                hook
                for tool in Tool.concrete_subclasses()
                for hook in tool().version_control_hooks()
            ],
        )

    def sort_hooks(self, hooks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort hooks by stage, then priority, then id.

        Stage groups hooks that never run in the same invocation apart first,
        since only hooks sharing a stage compete for order at all. Within a
        stage, priority orders the pipeline; id breaks ties deterministically.

        Args:
            hooks: Hook metadata dictionaries to sort.

        Returns:
            The hooks sorted by `(stages, priority, id)`.
        """
        return sorted(
            hooks,
            key=lambda hook: (hook["stages"], hook["priority"], hook["id"]),
        )

    def hook(  # noqa: PLR0913
        self,
        method: Callable[[], Args],
        *,
        priority: int,
        stages: Iterable[str] | None = None,
        language: str = "system",
        groups: Iterable[str] | None = None,
        types: Iterable[str] | None = None,
        types_or: Iterable[str] | None = None,
        files: str | None = None,
        exclude: str | None = None,
        args: Iterable[str] | None = None,
        always_run: bool | None = None,
        pass_filenames: bool | None = None,
    ) -> dict[str, Any]:
        """Build a prek hook metadata dictionary.

        Args:
            method: Bound, zero-argument method that returns the `Args` to
                run as the hook's entry. Also supplies the hook's `id` and
                `name`, derived from `method.__name__`.
            priority: This hook's position among hooks sharing its `stages`,
                lowest first. Ties break by `id`.
            stages: Git stages that trigger this hook. Defaults to
                `["pre-commit"]`.
            language: The hook's `language` value. Defaults to `"system"`,
                since every hook here wraps a tool already installed on the
                host rather than one prek should fetch itself.
            groups: Extra badge groups beyond `group_all()` to tag this hook
                with.
            types: File types this hook is restricted to.
            types_or: File types this hook is restricted to, matching any one
                of them rather than all.
            files: Regex restricting this hook to file paths that match.
                For a tool with no path filter of its own, unlike `types`
                and `types_or`, which filter by detected file type rather
                than path.
            exclude: Regex excluding matching file paths from this hook,
                even when they match `types`, `types_or`, or `files`.
            args: Extra CLI arguments appended to the hook's entry command.
            always_run: Whether to run this hook even when no matching files
                changed.
            pass_filenames: Whether to pass the matched file paths to the
                hook's entry command.

        Returns:
            Hook metadata dictionary in prek's expected schema.
        """
        entry = method()
        method = cast("MethodType", method)
        hook: dict[str, Any] = {
            "id": self.id_from_method(method),
            "name": self.name_from_method(method),
            "language": language,
            "entry": str(entry),
        }
        if args is not None:
            hook["args"] = sorted(args)
        if types is not None:
            hook["types"] = sorted(types)
        if types_or is not None:
            hook["types_or"] = sorted(types_or)
        if files is not None:
            hook["files"] = files
        if exclude is not None:
            hook["exclude"] = exclude
        hook["stages"] = sorted(stages or ["pre-commit"])
        hook["groups"] = sorted([self.group_all(), *(groups or [])])
        hook["priority"] = priority
        if always_run is not None:
            hook["always_run"] = always_run
        if pass_filenames is not None:
            hook["pass_filenames"] = pass_filenames
        return hook

    def transition_stages(self) -> list[str]:
        """Return the git stages a project's dependency state transitions on.

        Returns:
            `["post-checkout", "post-merge", "post-rewrite", "pre-push"]`,
            the events after which the lockfile, installed dependencies, or
            their audit may need to run again.
        """
        return ["post-checkout", "post-merge", "post-rewrite", "pre-push"]

    def group_all(self) -> str:
        """Return the badge group every hook is tagged with.

        Returns:
            `"all"`, so a full `prek run --all-files --group all` sweep
            always includes every hook regardless of its other groups.
        """
        return "all"

    def id_from_method(self, method: MethodType) -> str:
        """Derive a hook's `id` from its entry method's name.

        Args:
            method: The hook's bound entry method.

        Returns:
            `method.__name__` converted to kebab-case.
        """
        return snake_to_kebab_case(method.__name__)

    def name_from_method(self, method: MethodType) -> str:
        """Derive a hook's display `name` from its entry method's name.

        Args:
            method: The hook's bound entry method.

        Returns:
            `method.__name__` with underscores replaced by spaces.
        """
        return reformat_name(method.__name__, split_on="_", join_on=" ")

    def increase_priority(self, hook: dict[str, Any]) -> int:
        """Return the priority one step after another hook's.

        Used to chain a hook after one it depends on having already run.

        Args:
            hook: The hook metadata dictionary to run after.

        Returns:
            `hook`'s priority plus one.
        """
        return self.hook_priority(hook) + 1

    def hook_priority(self, hook: dict[str, Any]) -> int:
        """Return another hook's priority, for hooks that should run alongside it.

        Args:
            hook: The hook metadata dictionary to match the priority of.

        Returns:
            `hook`'s priority, unchanged.
        """
        return hook["priority"]

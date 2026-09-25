"""Command and hook-metadata construction for the prek pre-commit pipeline."""

from collections.abc import Callable, Iterable
from operator import itemgetter
from types import MethodType
from typing import Any, cast

from pyrig_runtime.core.strings import snake_to_kebab_case

from pyrig.core.strings import reformat_name
from pyrig.core.subprocesses import Args
from pyrig.rig.tools.base.tool import Group, Tool


class VersionControlHookManager(Tool):
    """Wrapper for the prek pre-commit hook manager.

    Builds `Args` for prek's own CLI: installing hooks into the local git
    repository and running them against files. Also provides the shared
    hook-metadata API every other `Tool` subclass uses to declare its own
    hooks in the pipeline, deriving each hook's `id` and `name` from its
    entry method, matching or chaining hook priorities, and sorting hooks
    into a deterministic run order.
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
            Args for `prek run --all-files --group=all [args]`.
        """
        return self.run_all_files_group_args(*args, group=self.group_all())

    def run_all_files_group_args(self, *args: str, group: str) -> Args:
        """Build arguments to run hooks of a given group against every file.

        Args:
            *args: Additional arguments appended to the command.
            group: The hook group to run (e.g. `"tooling"`).

        Returns:
            Args for `prek run --all-files --group=<group> [args]`.
        """
        return self.run_all_files_args(f"--group={group}", *args)

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

    def hook_sort_key(self, hook: dict[str, Any]) -> tuple[Any, ...]:
        """Return a sort key ordering a hook by priority, stages, then id.

        `priority` leads `stages`, matching prek's own scheduler, which
        orders hooks by `priority` alone regardless of `stages`.
        """
        return itemgetter("priority", "stages", "id")(hook)

    def local_hook(  # noqa: PLR0913
        self,
        method: Callable[[], Args],
        *,
        priority: int,
        stages: Iterable[str] = ("pre-commit",),
        groups: Iterable[str] = (),
        types: Iterable[str] | None = None,
        types_or: Iterable[str] | None = None,
        files: str | None = None,
        exclude: str | None = None,
        args: Args | None = None,
        always_run: bool | None = None,
        pass_filenames: bool | None = None,
    ) -> dict[str, Any]:
        """Build a prek hook metadata dictionary.

        Args:
            method: Bound, zero-argument method that returns the `Args` to
                run as the hook's entry. Also supplies the hook's `id` and
                `name`, derived from `method.__name__`.
            priority: Numeric priority compared across all hooks in this
                config, regardless of repo or stages; lower values run first.
                Hooks with equal priority may run concurrently.
            stages: Git stages that trigger this hook. Defaults to
                `["pre-commit"]`.
            groups: Extra prek hook groups beyond `group_all()` to tag this
                hook with.
            types: File types this hook is restricted to.
            types_or: File types this hook is restricted to, matching any one
                of them rather than all.
            files: Regex restricting this hook to file paths that match.
                Useful for a tool with no path filter of its own, unlike
                `types` and `types_or`, which filter by detected file
                type rather than path.
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
        base_hook = self.hook(
            method,
            priority=priority,
            stages=stages,
            groups=groups,
        )

        id_ = base_hook["id"]
        hook = {
            "repo": "local",
            "id": id_,
            "name": self.name_from_id(id_),
            "language": "system",
            "entry": str(method()),
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
        hook["stages"] = base_hook["stages"]
        hook["groups"] = base_hook["groups"]
        if always_run is not None:
            hook["always_run"] = always_run
        if pass_filenames is not None:
            hook["pass_filenames"] = pass_filenames
        hook["priority"] = base_hook["priority"]
        return hook

    def builtin_hook(
        self,
        method: Callable[[], Args],
        *,
        priority: int,
        stages: Iterable[str] = ("pre-commit",),
        groups: Iterable[str] = (),
    ) -> dict[str, Any]:
        """Build metadata for a builtin hook provided by prek itself.

        Args:
            method: Bound, zero-argument method whose name identifies the
                built-in hook and whose return value supplies its arguments.
            priority: This hook's position in the prek pipeline.
            stages: Git stages that trigger this hook. Defaults to
                `["pre-commit"]`.
            groups: Extra prek hook groups beyond `group_all()` to tag this
                hook with.

        Returns:
            Hook metadata dictionary in prek's built-in hook schema.
        """
        base_hook = self.hook(
            method,
            priority=priority,
            stages=stages,
            groups=groups,
        )
        hook = {
            "repo": "builtin",
            "id": base_hook["id"],
        }
        if args := method():
            hook["args"] = sorted(args)
        hook["stages"] = base_hook["stages"]
        hook["groups"] = base_hook["groups"]
        hook["priority"] = base_hook["priority"]
        return hook

    def hook(
        self,
        method: Callable[[], Args],
        priority: int,
        stages: Iterable[str] = ("pre-commit",),
        groups: Iterable[str] = (),
    ) -> dict[str, Any]:
        """Build metadata shared by local and builtin hook declarations.

        Args:
            method: Bound, zero-argument method whose name supplies the hook
                id and whose return value supplies its entry arguments.
            priority: The hook's position in the prek pipeline.
            stages: Git stages that trigger this hook.
            groups: Extra prek hook groups beyond `group_all()`.

        Returns:
            Common id, priority, stages, and groups metadata.
        """
        return {
            "id": self.id_from_method(cast("MethodType", method)),
            "priority": priority,
            "stages": sorted(stages),
            "groups": sorted((self.group_all(), *groups)),
        }

    def group_all(self) -> str:
        """Return the prek hook group every hook is tagged with.

        Returns:
            `"all"`, so a full `prek run --all-files --group=all` sweep
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

    def name_from_id(self, id_: str) -> str:
        """Derive a hook's display `name` from its id.

        Args:
            id_: The hook's kebab-case id.

        Returns:
            The id with hyphens replaced by spaces.
        """
        return reformat_name(id_, split_on="-", join_on=" ")

    def deprioritize(self, *hooks: dict[str, Any]) -> int:
        """Return the priority one step after the highest priority of the given hooks.

        Args:
            *hooks: The hook metadata dictionaries to run after.

        Returns:
            The highest priority among `hooks` plus one.
        """
        return max(self.hook_priority(hook) for hook in hooks) + 1

    def hook_priority(self, hook: dict[str, Any]) -> int:
        """Return another hook's priority, for hooks that should run alongside it.

        Args:
            hook: The hook metadata dictionary to match the priority of.

        Returns:
            `hook`'s priority, unchanged.
        """
        return hook["priority"]

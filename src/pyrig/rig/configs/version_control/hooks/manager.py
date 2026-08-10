"""Configuration management for version control hooks.

Declares the hook pipeline that enforces code quality and dependency hygiene
at various git stages.
"""

from collections import defaultdict
from pathlib import Path
from typing import Any

from pyrig.rig.configs.base.toml import TOMLConfigFile
from pyrig.rig.tools.base.hooks import VersionControlHookTool
from pyrig.rig.tools.version_control.hooks.manager import (
    VersionControlHookManager,
)


class VersionControlHookManagerConfigFile(TOMLConfigFile):
    """Configuration manager for `prek.toml`, the version control hook pipeline.

    Declares one repository entry per distinct `repo` a hook is registered
    under (`"local"` by default), each holding the hooks assigned to it, so
    that together they cover the full code-quality pipeline.
    """

    def _dump(self, configs: dict[str, Any]) -> None:
        """Dump the `prek.toml` structure to disk and install the hooks."""
        super()._dump(configs)
        VersionControlHookManager.I.install_args().run()

    def _configs(self) -> dict[str, Any]:
        """Build the required `prek.toml` structure.

        Returns:
            Dict with the default hook install types and the `repos` entry,
            with the configured hooks grouped by their `repo`.
        """
        hooks = self.hooks()
        return {
            "default_install_hook_types": self.hook_types(hooks),
            "repos": self.repositories(hooks),
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

    def repositories(self, hooks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Group hooks into prek's `repos` entries, one per distinct `repo`.

        Args:
            hooks: The hooks to group.

        Returns:
            List of `{"repo": ..., "hooks": [...]}` dicts, one per distinct
            `repo` value found across `hooks`.
        """
        by_repo = self.hooks_by_repo(hooks)
        return [{"repo": repo, "hooks": hooks} for repo, hooks in by_repo.items()]

    def hooks_by_repo(
        self,
        hooks: list[dict[str, Any]],
    ) -> defaultdict[str, list[dict[str, Any]]]:
        """Bucket hooks by their `repo` key, removing that key from each hook.

        The `repo` key only exists to route a hook into the right bucket
        here; prek's own per-hook schema has no such key, so it's popped off
        rather than left behind as an unrecognised field.

        Args:
            hooks: The hooks to bucket. Each hook is mutated in place: its
                `repo` key is removed.

        Returns:
            Dict mapping each `repo` value to the list of hooks registered
            under it, in their original relative order.
        """
        by_repo: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for hook in hooks:
            by_repo[hook.pop("repo")].append(hook)
        return by_repo

    def hooks(self) -> list[dict[str, Any]]:
        """Return every hook configuration entry in the pipeline."""
        return VersionControlHookTool.subclasses_hooks()

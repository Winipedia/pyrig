"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.core.subprocesses import Args
from pyrig.rig.configs.version_control.hook_manager import (
    VersionControlHookManagerConfigFile,
)


@pytest.fixture
def my_test_prek_config_file(
    config_file_factory: Callable[
        [type[VersionControlHookManagerConfigFile]],
        type[VersionControlHookManagerConfigFile],
    ],
) -> type[VersionControlHookManagerConfigFile]:
    """Create a test prek config file class with tmp_path."""

    class MyTestVersionControlHookManagerConfigFile(
        config_file_factory(VersionControlHookManagerConfigFile),  # ty: ignore[unsupported-base]
    ):
        """Test prek config file with tmp_path override."""

    return MyTestVersionControlHookManagerConfigFile


class TestVersionControlHookManagerConfigFile:
    """Test class."""

    def test_hook_types(self) -> None:
        """Test method."""
        assert VersionControlHookManagerConfigFile.I.hook_types() == [
            "post-checkout",
            "post-merge",
            "post-rewrite",
            "pre-commit",
            "pre-push",
        ]

    def test_hooks(self) -> None:
        """Test method."""
        hooks = VersionControlHookManagerConfigFile.I.hooks()
        assert isinstance(hooks, list)
        for hook in hooks:
            hook_id = hook["id"]
            assert isinstance(hook_id, str)
            assert hook_id
        by_id = {hook["id"]: hook for hook in hooks}
        # Each pre-commit stage runs strictly after the previous one, so
        # that later stages always see the fully-fixed, fully-generated
        # project.
        assert (
            by_id["synchronize-project"]["priority"]
            < by_id["fix-spelling"]["priority"]
            < by_id["lint-python"]["priority"]
            < by_id["check-secrets"]["priority"]
        )
        # The push/checkout/merge/rewrite hooks are a separate stage pool
        # from the pre-commit ones, so they restart from their own base
        # priority instead of continuing the pre-commit chain.
        assert by_id["update-package-manager"]["priority"] == 0

    def test_stem(self) -> None:
        """Test method."""
        assert VersionControlHookManagerConfigFile.I.stem() == "prek"

    def test_hook(self) -> None:
        """Test method."""
        hook = VersionControlHookManagerConfigFile.I.hook(
            "test",
            Args("test"),
            priority=1,
            stages=["some-stage"],
        )
        assert hook["priority"] == 1
        assert hook["id"] == "test"
        assert hook["stages"] == ["some-stage"]
        # TOML has no null value, so an unset `files` must be omitted
        # entirely rather than serialized as `None`.
        assert "files" not in hook
        # pass_filenames/always_run match prek's own defaults here, so
        # they must be omitted too rather than restated redundantly.
        assert "pass_filenames" not in hook
        assert "always_run" not in hook

        hook_with_types = VersionControlHookManagerConfigFile.I.hook(
            "test",
            Args("test"),
            priority=1,
            stages=["some-stage"],
            types=["shell"],
        )
        assert hook_with_types["types"] == ["shell"]

        hook_with_types_or = VersionControlHookManagerConfigFile.I.hook(
            "test",
            Args("test"),
            priority=1,
            stages=["some-stage"],
            types_or=["python", "pyi"],
        )
        assert hook_with_types_or["types_or"] == ["python", "pyi"]

        hook_with_overrides = VersionControlHookManagerConfigFile.I.hook(
            "test",
            Args("test"),
            priority=1,
            stages=["some-stage"],
            pass_filenames=False,
            always_run=True,
        )
        assert hook_with_overrides["pass_filenames"] is False
        assert hook_with_overrides["always_run"] is True

    def test_parent_path(
        self,
        my_test_prek_config_file: type[VersionControlHookManagerConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            parent_path = my_test_prek_config_file().parent_path()
            assert parent_path == Path(), f"Expected Path(), got {parent_path}"

    def test__configs(
        self,
        my_test_prek_config_file: type[VersionControlHookManagerConfigFile],
    ) -> None:
        """Test method."""
        configs = my_test_prek_config_file().configs()
        assert "repos" in configs, "Expected 'repos' key in configs"
        assert isinstance(configs["repos"], list), "Expected 'repos' to be a list"
        assert len(configs["repos"]) > 0, "Expected at least one repo in configs"
        repo = configs["repos"][0]
        assert repo["repo"] == "local", (
            f"Expected repo to be 'local', got {repo['repo']}"
        )
        assert "hooks" in repo, "Expected 'hooks' key in repo"
        assert isinstance(repo["hooks"], list), "Expected 'hooks' to be a list"
        assert len(repo["hooks"]) > 0, "Expected at least one hook in repo"

    def test_transition_hooks(self) -> None:
        """Test method."""
        priority = 3
        hooks = VersionControlHookManagerConfigFile.I.transition_hooks(
            priority=priority,
        )
        assert [hook["id"] for hook in hooks] == [
            "update-package-manager",
            "update-dependencies",
            "install-dependencies",
            "audit-dependencies",
        ]
        priorities = [hook["priority"] for hook in hooks]
        # Each step depends on the previous one having already run.
        assert priorities == [priority, priority + 1, priority + 2, priority + 3]
        expected_stages = [
            "post-checkout",
            "post-merge",
            "post-rewrite",
            "pre-push",
        ]
        assert all(hook["stages"] == expected_stages for hook in hooks)
        # Every hook here scans or acts on the whole project rather than
        # specific files, so all four override prek's defaults.
        assert all(hook["pass_filenames"] is False for hook in hooks)
        assert all(hook["always_run"] is True for hook in hooks)

    def test_check_hooks(self) -> None:
        """Test method."""
        priority = 3
        hooks = VersionControlHookManagerConfigFile.I.check_hooks(priority=priority)
        by_id = {hook["id"]: hook for hook in hooks}
        assert set(by_id) == {
            "check-secrets",
            "check-security",
            "check-types",
            "check-dependencies",
            "check-shell",
        }
        # All five checks are read-only and independent, so they share one
        # priority and run concurrently.
        assert all(hook["priority"] == priority for hook in hooks)
        # detect-secrets-hook can't usefully scan genuinely binary content
        # anyway (confirmed by testing), so restricting to text costs no
        # real coverage while letting a binary-only commit skip this hook.
        assert by_id["check-secrets"]["types"] == ["text"]
        assert "pass_filenames" not in by_id["check-secrets"]
        # bandit's tests/ exclusion now comes from its own config file
        # (`-c pyproject.toml`, read via `[tool.bandit] exclude_dirs`), not
        # from restricting which files match, so it only needs a type
        # filter, same shape as check-shell.
        assert by_id["check-security"]["types"] == ["python"]
        assert "pass_filenames" not in by_id["check-security"]
        assert by_id["check-shell"]["types"] == ["shell"]
        assert "pass_filenames" not in by_id["check-shell"]
        # check-types and check-dependencies keep pass_filenames=False -
        # whole-program analysis needs the actual scan to cover the whole
        # project regardless of what changed - but no longer override
        # always_run: the type filter alone gates whether the hook runs at
        # all, skipping it entirely on a commit that touches none of its
        # relevant file types, since such a commit cannot have introduced
        # the kind of breakage these two exist to catch. check-dependencies
        # needs types_or (python or pyproject, either sufficient); the
        # single-type check-types just needs types.
        assert by_id["check-types"]["types"] == ["python"]
        assert by_id["check-types"]["pass_filenames"] is False
        assert "always_run" not in by_id["check-types"]
        assert by_id["check-dependencies"]["types_or"] == ["python", "pyproject"]
        assert by_id["check-dependencies"]["pass_filenames"] is False
        assert "always_run" not in by_id["check-dependencies"]

    def test_update_type_hooks(self) -> None:
        """Test method."""
        priority = 3
        hooks = VersionControlHookManagerConfigFile.I.update_type_hooks(
            priority=priority,
        )
        by_id = {hook["id"]: hook for hook in hooks}
        assert set(by_id) == {
            "lint-python",
            "format-python",
            "lint-markdown",
            "lint-yaml",
            "format-shell",
        }
        assert by_id["lint-python"]["priority"] == priority
        # Lint fixes must run before formatting: they can leave code that
        # still needs reformatting.
        assert by_id["lint-python"]["priority"] < by_id["format-python"]["priority"]
        # YAML, Markdown, and Shell never overlap Python's file scope
        # (each hook's own `files` filter guarantees it), so all three are
        # safe to share the lint-python priority and run concurrently.
        assert by_id["lint-yaml"]["priority"] == by_id["lint-python"]["priority"]
        assert by_id["lint-markdown"]["priority"] == by_id["lint-python"]["priority"]
        assert by_id["format-shell"]["priority"] == by_id["lint-python"]["priority"]
        # Every hook here targets one self-contained file type with no
        # cross-file dependencies, so all of them rely on prek's default
        # of passing matched filenames instead of rescanning the whole
        # project on every commit - no override needed, so none of these
        # keys are present.
        for hook_id in (
            "lint-python",
            "format-python",
            "lint-markdown",
            "lint-yaml",
            "format-shell",
        ):
            assert "pass_filenames" not in by_id[hook_id]
            assert "always_run" not in by_id[hook_id]
        # Every hook here has exactly one relevant type, so plain `types`
        # is enough; none of them need `types_or`.
        assert by_id["lint-python"]["types"] == ["python"]
        assert by_id["format-python"]["types"] == ["python"]
        assert by_id["lint-markdown"]["types"] == ["markdown"]
        assert by_id["lint-yaml"]["types"] == ["yaml"]
        assert by_id["format-shell"]["types"] == ["shell"]

    def test_update_types_hooks(self) -> None:
        """Test method."""
        hooks = VersionControlHookManagerConfigFile.I.update_types_hooks(
            priority=3,
        )
        assert [hook["id"] for hook in hooks] == ["fix-spelling"]

    def test_generate_hooks(self) -> None:
        """Test method."""
        priority = 3
        hooks = VersionControlHookManagerConfigFile.I.generate_hooks(
            priority=priority,
        )
        assert [hook["id"] for hook in hooks] == ["synchronize-project"]
        assert all(hook["priority"] == priority for hook in hooks)
        # Regenerates the whole project itself, so it overrides prek's
        # defaults.
        assert all(hook["pass_filenames"] is False for hook in hooks)
        assert all(hook["always_run"] is True for hook in hooks)

    def test_highest_priority(self) -> None:
        """Test method."""
        highest = 5
        hooks = [
            {"priority": 3},
            {"priority": 1},
            {"priority": highest},
            {"priority": 2},
        ]
        assert VersionControlHookManagerConfigFile.I.highest_priority(hooks) == highest

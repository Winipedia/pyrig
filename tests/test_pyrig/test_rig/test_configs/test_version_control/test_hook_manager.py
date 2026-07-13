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

    def test_check_hooks(self) -> None:
        """Test method."""
        priority = 3
        hooks = VersionControlHookManagerConfigFile.I.check_hooks(priority=priority)
        assert {hook["id"] for hook in hooks} == {
            "check-secrets",
            "check-security",
            "check-types",
            "check-dependencies",
        }
        # All checks are read-only and independent, so they share one
        # priority and run concurrently.
        assert all(hook["priority"] == priority for hook in hooks)

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
        }
        assert by_id["lint-python"]["priority"] == priority
        # Lint fixes must run before formatting: they can leave code that
        # still needs reformatting.
        assert by_id["lint-python"]["priority"] < by_id["format-python"]["priority"]
        # YAML never overlaps Python's file scope, so it is safe to share
        # the lint-python priority and run concurrently with it.
        assert by_id["lint-yaml"]["priority"] == by_id["lint-python"]["priority"]

    def test_update_types_hooks(self) -> None:
        """Test method."""
        priority = 3
        hooks = VersionControlHookManagerConfigFile.I.update_types_hooks(
            priority=priority,
        )
        assert [hook["id"] for hook in hooks] == ["fix-spelling"]
        assert all(hook["priority"] == priority for hook in hooks)

    def test_generate_hooks(self) -> None:
        """Test method."""
        priority = 3
        hooks = VersionControlHookManagerConfigFile.I.generate_hooks(
            priority=priority,
        )
        assert [hook["id"] for hook in hooks] == ["synchronize-project"]
        assert all(hook["priority"] == priority for hook in hooks)

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

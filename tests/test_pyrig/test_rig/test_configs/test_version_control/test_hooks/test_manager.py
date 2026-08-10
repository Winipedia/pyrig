"""module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.configs.version_control.hooks.manager import (
    VersionControlHookManagerConfigFile,
)
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


class TestVersionControlHookManagerConfigFile:
    """Test class."""

    def test_hook_types(self) -> None:
        """Test method."""
        assert VersionControlHookManagerConfigFile.I.hook_types(
            VersionControlHookManagerConfigFile.I.hooks(),
        ) == [
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
        assert by_id["update-dependencies"]["priority"] == 0

    def test_stem(self) -> None:
        """Test method."""
        assert VersionControlHookManagerConfigFile.I.stem() == "prek"

    def test_parent_path(
        self,
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            parent_path = VersionControlHookManagerConfigFile.I.parent_path()
            assert parent_path == Path(), f"Expected Path(), got {parent_path}"

    def test__configs(
        self,
    ) -> None:
        """Test method."""
        configs = VersionControlHookManagerConfigFile.I.configs()
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

    def test__dump(self, mocker: MockerFixture, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            mock_hook_install = mocker.patch.object(
                VersionControlHookManager,
                VersionControlHookManager.install_args.__name__,
                return_value=mocker.Mock(run=lambda: True),
            )
            VersionControlHookManagerConfigFile.I._dump({})  # noqa: SLF001
            mock_hook_install.assert_called_once()

            VersionControlHookManagerConfigFile.I.validate()
            assert mock_hook_install.call_count == 2  # noqa: PLR2004

            VersionControlHookManagerConfigFile.I.validate()
            assert mock_hook_install.call_count == 2  # noqa: PLR2004

    def test_repositories(self) -> None:
        """Test method."""
        hooks = [
            {"repo": "local", "id": "a"},
            {"repo": "other", "id": "b"},
            {"repo": "local", "id": "c"},
        ]
        result = VersionControlHookManagerConfigFile.I.repositories(hooks)
        assert result == [
            {"repo": "local", "hooks": [{"id": "a"}, {"id": "c"}]},
            {"repo": "other", "hooks": [{"id": "b"}]},
        ]

    def test_hooks_by_repo(self) -> None:
        """Test method."""
        hooks = [
            {"repo": "local", "id": "a"},
            {"repo": "other", "id": "b"},
            {"repo": "local", "id": "c"},
        ]
        by_repo = VersionControlHookManagerConfigFile.I.hooks_by_repo(hooks)
        assert list(by_repo) == ["local", "other"]
        assert by_repo["local"] == [{"id": "a"}, {"id": "c"}]
        assert by_repo["other"] == [{"id": "b"}]
        # the "repo" key is consumed, not left behind on each hook
        assert "repo" not in hooks[0]

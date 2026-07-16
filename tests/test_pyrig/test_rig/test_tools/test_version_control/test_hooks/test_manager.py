"""module."""

from pyrig.rig.tools.version_control.hooks.manager import (
    VersionControlHookManager,
)


class TestVersionControlHookManager:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            VersionControlHookManager.I.image_url()
            == "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert VersionControlHookManager.I.link_url() == "https://github.com/j178/prek"

    def test_run_all_files_all_hooks_args(self) -> None:
        """Test method."""
        assert VersionControlHookManager.I.run_all_files_all_hooks_args() == (
            "prek",
            "run",
            "--all-files",
            "--group",
            "all",
        )

    def test_run_all_files_group_args(self) -> None:
        """Test method."""
        assert VersionControlHookManager.I.run_all_files_group_args(
            group="some-group",
        ) == (
            "prek",
            "run",
            "--all-files",
            "--group",
            "some-group",
        )

    def test_group(self) -> None:
        """Test method."""
        result = VersionControlHookManager.I.group()
        assert isinstance(result, str)
        assert result == "tooling"

    def test_name(self) -> None:
        """Test method."""
        result = VersionControlHookManager.I.name()
        assert result == "prek"

    def test_install_args(self) -> None:
        """Test method."""
        result = VersionControlHookManager.I.install_args()
        assert result == ("prek", "install")

    def test_run_args(self) -> None:
        """Test method."""
        result = VersionControlHookManager.I.run_args()
        assert result == ("prek", "run")

    def test_run_all_files_args(self) -> None:
        """Test method."""
        result = VersionControlHookManager.I.run_all_files_args()
        assert result == ("prek", "run", "--all-files")

    def test_hook(self) -> None:
        """Test method."""
        priority = 2
        hook = VersionControlHookManager.I.hook(
            VersionControlHookManager.I.run_args,
            priority=priority,
            types=["python"],
            files="^tests/",
            exclude="^tests/fixtures/",
            args=["--fix"],
        )
        assert hook["id"] == "run-args"
        assert hook["name"] == "run args"
        assert hook["language"] == "system"
        assert hook["entry"] == str(VersionControlHookManager.I.run_args())
        assert hook["args"] == ["--fix"]
        assert hook["types"] == ["python"]
        assert hook["files"] == "^tests/"
        assert hook["exclude"] == "^tests/fixtures/"
        assert hook["stages"] == ["pre-commit"]
        assert hook["groups"] == ["all"]
        assert hook["priority"] == priority
        assert "always_run" not in hook
        assert "pass_filenames" not in hook

    def test_hook_without_files(self) -> None:
        """Test method."""
        hook = VersionControlHookManager.I.hook(
            VersionControlHookManager.I.run_args,
            priority=1,
        )
        assert "files" not in hook

    def test_hook_without_exclude(self) -> None:
        """Test method."""
        hook = VersionControlHookManager.I.hook(
            VersionControlHookManager.I.run_args,
            priority=1,
        )
        assert "exclude" not in hook

    def test_transition_stages(self) -> None:
        """Test method."""
        assert VersionControlHookManager.I.transition_stages() == [
            "post-checkout",
            "post-merge",
            "post-rewrite",
            "pre-push",
        ]

    def test_group_all(self) -> None:
        """Test method."""
        assert VersionControlHookManager.I.group_all() == "all"

    def test_id_from_method(self) -> None:
        """Test method."""
        assert (
            VersionControlHookManager.I.id_from_method(
                VersionControlHookManager.I.run_args,
            )
            == "run-args"
        )

    def test_name_from_method(self) -> None:
        """Test method."""
        assert (
            VersionControlHookManager.I.name_from_method(
                VersionControlHookManager.I.run_args,
            )
            == "run args"
        )

    def test_increase_priority(self) -> None:
        """Test method."""
        priority = 5
        assert (
            VersionControlHookManager.I.increase_priority({"priority": priority})
            == priority + 1
        )

    def test_hook_priority(self) -> None:
        """Test method."""
        priority = 5
        assert (
            VersionControlHookManager.I.hook_priority({"priority": priority})
            == priority
        )

    def test_hook_sort_key(self) -> None:
        """Test method."""
        hook = {"stages": ["pre-commit"], "priority": 2, "id": "b"}
        assert VersionControlHookManager.I.hook_sort_key(hook) == (
            ["pre-commit"],
            2,
            "b",
        )

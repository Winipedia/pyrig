"""module."""

from pyrig.rig.tools.version_control import hook_manager
from pyrig.rig.tools.version_control.hook_manager import (
    VersionControlHookManager,
)


class TestVersionControlHookManager:
    """Test class."""

    def test_run_all_files_stage_pre_commit_args(self) -> None:
        """Test method."""
        assert VersionControlHookManager.I.run_all_files_stage_pre_commit_args() == (
            "prek",
            "run",
            "--all-files",
            "--hook-stage",
            "pre-commit",
        )

    def test_run_all_files_stage_args(self) -> None:
        """Test method."""
        assert VersionControlHookManager.I.run_all_files_stage_args(
            stage="some-stage"
        ) == (
            "prek",
            "run",
            "--all-files",
            "--hook-stage",
            "some-stage",
        )

    def test_group(self) -> None:
        """Test method."""
        result = VersionControlHookManager.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = VersionControlHookManager.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

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


def test_module_docstring() -> None:
    """Test module docstring."""
    assert (
        hook_manager.__doc__
        == """Tool wrapper for the version control hook manager.

Wraps version control hook manager commands and information.
"""
    )

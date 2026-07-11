"""module."""

from pyrig.rig.tools.version_control.hook_manager import (
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
            stage="some-stage",
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

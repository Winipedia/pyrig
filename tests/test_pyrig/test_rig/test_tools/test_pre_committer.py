"""module."""

from pyrig.rig.tools.pre_committer import PreCommitter


class TestPreCommitter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = PreCommitter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = PreCommitter.I.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = PreCommitter.I.name()
        assert result == "prek"

    def test_install_args(self) -> None:
        """Test method."""
        result = PreCommitter.I.install_args()
        assert result == ("prek", "install")

    def test_run_args(self) -> None:
        """Test method."""
        result = PreCommitter.I.run_args()
        assert result == ("prek", "run")

    def test_run_all_files_args(self) -> None:
        """Test method."""
        result = PreCommitter.I.run_all_files_args()
        assert result == ("prek", "run", "--all-files")

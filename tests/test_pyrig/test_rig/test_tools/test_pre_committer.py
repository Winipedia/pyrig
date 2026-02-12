"""module."""

from pyrig.rig.tools.pre_committer import PreCommitter


class TestPreCommitter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = PreCommitter.L.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_badge_urls(self) -> None:
        """Test method."""
        result = PreCommitter.L.badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_name(self) -> None:
        """Test method."""
        result = PreCommitter.L.name()
        assert result == "prek"

    def test_install_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.install_args()
        assert result == ("prek", "install")

    def test_run_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.run_args()
        assert result == ("prek", "run")

    def test_run_all_files_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.run_all_files_args()
        assert result == ("prek", "run", "--all-files")

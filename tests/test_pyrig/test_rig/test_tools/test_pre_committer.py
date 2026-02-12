"""module."""

from pyrig.rig.tools.pre_committer import PreCommitter


class TestPreCommitter:
    """Test class."""

    def test_get_group(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_get_badge_urls(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_badge_urls()
        assert isinstance(result, tuple)
        assert all(isinstance(url, str) for url in result)

    def test_get_name(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_name()
        assert result == "prek"

    def test_get_install_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_install_args()
        assert result == ("prek", "install")

    def test_get_run_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_run_args()
        assert result == ("prek", "run")

    def test_get_run_all_files_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_run_all_files_args()
        assert result == ("prek", "run", "--all-files")

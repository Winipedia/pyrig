"""module."""

from pyrig.dev.management.pre_committer import PreCommitter


class TestPreCommitter:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = PreCommitter.L.name()
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

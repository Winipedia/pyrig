"""module."""

from pyrig.dev.management.pre_committer import PreCommitter


class TestPreCommitter:
    """Test class."""

    def test_name(self) -> None:
        """Test method."""
        result = PreCommitter.L.name()
        assert result == "pre-commit"

    def test_get_install_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_install_args()
        assert result == ("pre-commit", "install")

    def test_get_run_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_run_args()
        assert result == ("pre-commit", "run")

    def test_get_run_all_files_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_run_all_files_args()
        assert result == ("pre-commit", "run", "--all-files")

    def test_get_run_all_files_verbose_args(self) -> None:
        """Test method."""
        result = PreCommitter.L.get_run_all_files_verbose_args()
        assert result == ("pre-commit", "run", "--all-files", "--verbose")

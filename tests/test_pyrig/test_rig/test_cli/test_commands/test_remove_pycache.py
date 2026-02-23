"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.cli.commands.remove_pycache import remove_pycache
from pyrig.rig.tools.package_manager import PackageManager


def test_remove_pycache(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # create __pycache__ directories in tests and package
        package_name = PackageManager.I.package_name()
        (tmp_path / "tests" / "__pycache__").mkdir(parents=True)
        (tmp_path / package_name / "__pycache__").mkdir(parents=True)

        # run remove_pycache command
        remove_pycache()

        # assert __pycache__ directories are removed
        assert not (tmp_path / "tests" / "__pycache__").exists()
        assert not (tmp_path / package_name / "__pycache__").exists()

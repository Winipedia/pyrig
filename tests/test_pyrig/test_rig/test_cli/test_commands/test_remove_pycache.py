"""module."""

from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.rig.cli.commands.remove_pycache import remove_pycache


def test_remove_pycache(
    tmp_project_root_path: Path, tmp_package_root_path: tuple[Path, ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_project_root_path):
        package_root_path, _ = tmp_package_root_path
        pycache_path = package_root_path / "__pycache__"
        pycache_path.mkdir()
        assert pycache_path.exists()
        remove_pycache()
        assert not pycache_path.exists()

        tests_path = Path("tests")
        tests_path.mkdir()
        pycache_tests_path = tests_path / "__pycache__"
        pycache_tests_path.mkdir()
        assert pycache_tests_path.exists()
        remove_pycache()
        assert not pycache_tests_path.exists()

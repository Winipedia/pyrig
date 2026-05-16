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
        module_path = package_root_path / "module.py"
        module_path.touch()
        pycache_path.mkdir()
        assert pycache_path.exists()
        remove_pycache()
        assert not pycache_path.exists()
        assert module_path.exists()

        tests_path = Path("tests")
        tests_path.mkdir()
        pycache_tests_path = tests_path / "__pycache__"
        pycache_tests_path.mkdir()
        assert pycache_tests_path.exists()
        remove_pycache()
        assert not pycache_tests_path.exists()

        # Test with no __pycache__ directories
        remove_pycache()
        assert not pycache_path.exists()
        assert not pycache_tests_path.exists()

        # check with nested __pycache__ directories
        nested_path = package_root_path / "nested"
        nested_path.mkdir()
        nested_pycache_path = nested_path / "__pycache__"
        nested_pycache_path.mkdir()
        assert nested_pycache_path.exists()
        deep_nested_pycache_path = package_root_path / "deep" / "nested" / "__pycache__"
        deep_nested_pycache_path.mkdir(parents=True)
        assert deep_nested_pycache_path.exists()
        double_nested_pycache_path = (
            package_root_path / "deep" / "__pycache__" / "__pycache__" / "__pycache__"
        )
        double_nested_pycache_path.mkdir(parents=True)
        assert double_nested_pycache_path.exists()
        remove_pycache()
        assert not nested_pycache_path.exists()
        assert not deep_nested_pycache_path.exists()

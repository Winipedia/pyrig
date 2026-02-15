"""Test module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.configs.git.gitignore import GitignoreConfigFile
from pyrig.rig.utils.packages import (
    find_namespace_packages,
    find_packages,
    src_package_is_pyrig,
)
from pyrig.rig.utils.version_control import path_is_in_ignore


def test_find_packages(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # make package in gitignore
        GitignoreConfigFile.I.validate()

        (Path.cwd() / "package1").mkdir()
        (Path.cwd() / "package1" / "__init__.py").write_text("")
        (Path.cwd() / "package1" / "sub1").mkdir()
        (Path.cwd() / "package1" / "sub1" / "__init__.py").write_text("")
        (Path.cwd() / "package1" / "sub1" / "sub2").mkdir()
        (Path.cwd() / "package1" / "sub1" / "sub2" / "__init__.py").write_text("")
        (Path.cwd() / "package2").mkdir()
        (Path.cwd() / "package2" / "__init__.py").write_text("")

        # Test without depth limit
        find_packages.cache_clear()
        result = find_packages()
        expected = ["package2", "package1", "package1.sub1", "package1.sub1.sub2"]
        assert result == expected

        # Test with depth limit
        find_packages.cache_clear()
        result = find_packages(depth=1)
        expected = ["package2", "package1", "package1.sub1"]
        assert result == expected

        # Test with depth 0
        find_packages.cache_clear()
        result = find_packages(depth=0)
        expected = ["package2", "package1"]
        assert result == expected


def test_find_namespace_packages(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # make package in gitignore
        GitignoreConfigFile.I.validate()

        (Path.cwd() / "docs").mkdir()
        find_packages.cache_clear()
        assert find_namespace_packages() == []
        (Path.cwd() / "src").mkdir()
        find_packages.cache_clear()
        assert find_namespace_packages() == ["src"]
        (Path.cwd() / "src" / "__init__.py").write_text("")
        find_packages.cache_clear()
        assert find_namespace_packages() == []

        # assert exists
        assert (Path.cwd() / ".gitignore").exists()
        assert path_is_in_ignore("dist")

        (Path.cwd() / "dist").mkdir()
        find_packages.cache_clear()
        assert find_namespace_packages() == []


def test_src_package_is_pyrig() -> None:
    """Test function."""
    assert src_package_is_pyrig()

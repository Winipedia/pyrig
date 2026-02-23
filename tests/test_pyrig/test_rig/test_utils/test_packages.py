"""Test module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.configs.git.gitignore import GitignoreConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.utils.packages import (
    find_namespace_packages,
    find_packages,
    src_package_is_pyrig,
)


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

        result = find_packages()
        expected = ["package2", "package1", "package1.sub1", "package1.sub1.sub2"]
        assert set(result) == set(expected)

        # Test with depth limit

        result = find_packages(depth=1)
        expected = ["package2", "package1", "package1.sub1"]
        assert set(result) == set(expected)

        # Test with depth 0

        result = find_packages(depth=0)
        expected = ["package2", "package1"]
        assert set(result) == set(expected)


def test_find_namespace_packages(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        (Path.cwd() / "docs").mkdir()

        assert list(find_namespace_packages()) == []

        package_name = PackageManager.I.package_name()
        (Path.cwd() / package_name).mkdir()

        assert list(find_namespace_packages()) == [package_name]
        (Path.cwd() / package_name / "__init__.py").write_text("")

        assert list(find_namespace_packages()) == []

        (Path.cwd() / "dist").mkdir()

        assert list(find_namespace_packages()) == []


def test_src_package_is_pyrig() -> None:
    """Test function."""
    assert src_package_is_pyrig()

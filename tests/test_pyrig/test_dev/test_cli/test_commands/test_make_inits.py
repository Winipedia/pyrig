"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.dev.cli.commands.make_inits import get_namespace_packages, make_init_files


def test_get_namespace_packages(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        (Path.cwd() / "docs").mkdir()
        assert get_namespace_packages() == []
        (Path.cwd() / "src").mkdir()
        assert get_namespace_packages() == ["src"]
        (Path.cwd() / "src" / "__init__.py").write_text("")
        assert get_namespace_packages() == []


def test_make_init_files(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        (Path.cwd() / "docs").mkdir()
        (Path.cwd() / "src").mkdir()
        assert get_namespace_packages() == ["src"]
        make_init_files()
        assert get_namespace_packages() == []

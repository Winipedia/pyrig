"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.cli.commands.make_inits import make_init_files
from pyrig.rig.configs.git.gitignore import GitignoreConfigFile
from pyrig.rig.utils.packages import find_namespace_packages, find_packages


def test_make_init_files(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        GitignoreConfigFile.I.validate()
        (Path.cwd() / "docs").mkdir()
        (Path.cwd() / "src").mkdir()
        find_packages.cache_clear()
        assert find_namespace_packages() == ["src"]
        make_init_files()
        find_packages.cache_clear()
        assert find_namespace_packages() == []

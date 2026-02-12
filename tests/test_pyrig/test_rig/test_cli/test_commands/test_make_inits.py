"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.cli.commands.make_inits import make_init_files
from pyrig.rig.configs.git.gitignore import GitIgnoreConfigFile
from pyrig.rig.utils.packages import find_namespace_packages


def test_make_init_files(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        GitIgnoreConfigFile()
        (Path.cwd() / "docs").mkdir()
        (Path.cwd() / "src").mkdir()
        assert find_namespace_packages() == ["src"]
        make_init_files()
        assert find_namespace_packages() == []

"""module."""

from contextlib import chdir
from pathlib import Path

from pyrig.rig.cli.commands.make_inits import make_init_files
from pyrig.rig.utils.packages import find_namespace_packages
from pyrig.src.string_ import package_name_from_cwd


def test_make_init_files(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        (Path.cwd() / "docs").mkdir()
        package_name = package_name_from_cwd()
        (Path.cwd() / package_name).mkdir()

        assert list(find_namespace_packages()) == [package_name]
        make_init_files()

        assert list(find_namespace_packages()) == []

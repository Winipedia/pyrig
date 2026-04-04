"""module."""

from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.rig.cli.commands.make_inits import make_init_files
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.utils.packages import find_namespace_packages


def test_make_init_files(
    tmp_project_root_path: Path, tmp_package_root_path: tuple[Path, ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_project_root_path):
        (Path("docs")).mkdir()
        ProjectTester.I.tests_package_root().mkdir()
        package_root_path, _ = tmp_package_root_path
        root_init = package_root_path / "__init__.py"
        root_init.unlink()
        assert not root_init.exists()

        assert set(find_namespace_packages()) == {
            PackageManager.I.package_name(),
            ProjectTester.I.tests_package_name(),
        }
        make_init_files()

        assert list(find_namespace_packages()) == []

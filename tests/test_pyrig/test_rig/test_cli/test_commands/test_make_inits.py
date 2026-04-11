"""module."""

from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.rig.cli.commands.make_inits import (
    make_init_file_with_standard_content,
    make_init_files,
    make_init_files_for_namespace_packages,
)
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.programming_language import ProgrammingLanguage
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
        # assert ends with empty line
        root_init.unlink()
        assert not root_init.exists()

        assert set(find_namespace_packages()) == {
            PackageManager.I.package_name(),
            ProjectTester.I.tests_package_name(),
        }
        make_init_files()
        assert list(find_namespace_packages()) == []
        content = root_init.read_text()
        assert content.endswith('"""\n')


def test_make_init_files_for_namespace_packages(
    tmp_project_root_path: Path, tmp_package_root_path: tuple[Path, ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_project_root_path):
        (Path("docs")).mkdir()
        ProjectTester.I.tests_package_root().mkdir()
        package_root_path, _ = tmp_package_root_path
        root_init = package_root_path / "__init__.py"
        # assert ends with empty line
        root_init.unlink()
        assert not root_init.exists()

        namespace_packages = list(find_namespace_packages())
        assert set(namespace_packages) == {
            PackageManager.I.package_name(),
            ProjectTester.I.tests_package_name(),
        }
        make_init_files_for_namespace_packages(namespace_packages)
        assert list(find_namespace_packages()) == []
        content = root_init.read_text()
        assert content.endswith('"""\n')


def test_make_init_file_with_standard_content(tmp_path: Path) -> None:
    """Test function."""
    init_path = tmp_path / "__init__.py"
    assert not init_path.exists()
    make_init_file_with_standard_content(tmp_path)
    assert init_path.exists()
    content = init_path.read_text()
    assert content.endswith('"""\n')
    assert ProgrammingLanguage.I.standard_init_content() in content

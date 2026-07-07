"""Test module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.core.root import (
    make_all_init_files,
    namespace_package_paths,
)
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.testers.project import ProjectTester


def test_make_all_init_files(
    tmp_project_root_path: Path, tmp_package_root_path: tuple[Path, ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_project_root_path):
        docs = Path("docs")
        docs.mkdir()
        ProjectTester.I.package_root().mkdir()
        package_root_path, _ = tmp_package_root_path
        root_init = package_root_path / "__init__.py"
        # assert ends with empty line
        root_init.unlink()
        assert not root_init.exists()

        assert set(namespace_package_paths()) == {
            PackageManager.I.package_root(),
            ProjectTester.I.package_root(),
        }
        make_all_init_files()
        assert list(namespace_package_paths()) == []
        content = root_init.read_text()
        assert content.endswith('"""\n')
        assert not (docs / "__init__.py").exists()


def test_namespace_package_paths(
    tmp_project_root_path: Path,
    tmp_package_root_path: tuple[Path, ModuleType],
    create_source_package: Callable[[Path], ModuleType],
) -> None:
    """Test function."""
    package_root_path, _ = tmp_package_root_path

    with chdir(tmp_project_root_path):
        Path("docs").mkdir()
        assert list(namespace_package_paths()) == []

        create_source_package(Path("package"))

        namespace_package = package_root_path / "namespace_package"
        namespace_package.mkdir()
        pycache = namespace_package / "__pycache__"
        pycache.mkdir()
        assert pycache.is_dir()
        assert list(namespace_package_paths()) == [
            namespace_package.relative_to(Path.cwd())
        ]

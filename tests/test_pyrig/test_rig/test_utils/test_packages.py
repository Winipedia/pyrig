"""Test module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.utils.packages import (
    find_namespace_packages,
    find_packages,
)


def test_find_packages(
    tmp_project_root_path: Path,
    tmp_package_root_path: tuple[Path, ModuleType],
    create_source_package: Callable[[Path], ModuleType],
    create_package: Callable[[Path], ModuleType],
) -> None:
    """Test function."""
    _, root_package = tmp_package_root_path
    with chdir(tmp_project_root_path):
        assert list(find_packages()) == [root_package.__name__]
        sub_package_path = Path("subpackage")
        sub_package = create_source_package(sub_package_path)
        assert set(find_packages()) == {root_package.__name__, sub_package.__name__}
        tests_package = create_package(ProjectTester.I.tests_package_root())
        assert set(find_packages()) == {
            root_package.__name__,
            sub_package.__name__,
            tests_package.__name__,
        }


def test_find_namespace_packages(
    tmp_project_root_path: Path,
    tmp_package_root_path: tuple[Path, ModuleType],
    create_source_package: Callable[[Path], ModuleType],
) -> None:
    """Test function."""
    package_root_path, root_package = tmp_package_root_path

    with chdir(tmp_project_root_path):
        Path("docs").mkdir()
        assert list(find_namespace_packages()) == []

        create_source_package(Path("package"))

        namespace_package = package_root_path / "namespace_package"
        namespace_package.mkdir()
        assert list(find_namespace_packages()) == [
            f"{root_package.__name__}.namespace_package"
        ]

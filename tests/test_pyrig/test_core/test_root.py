"""Test module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pytest_mock import MockerFixture

from pyrig.core.root import (
    determine_root,
    make_all_init_files,
    module_name_as_root_path,
    namespace_package_paths,
    package_name_as_root_path,
    root_path_as_module_name,
)
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.testers.project import ProjectTester


def test_module_name_as_root_path() -> None:
    """Test function."""
    name = "package.subpackage.module"
    expected_path = Path("src/package/subpackage/module.py")
    assert module_name_as_root_path(name) == expected_path

    tests_name = "tests.test_package.subpackage.test_module"
    expected_tests_path = Path("tests/test_package/subpackage/test_module.py")
    assert module_name_as_root_path(tests_name) == expected_tests_path


def test_package_name_as_root_path() -> None:
    """Test function."""
    name = "package.subpackage.subsubpackage"
    expected_path = Path("src/package/subpackage/subsubpackage")
    assert package_name_as_root_path(name) == expected_path

    tests_name = "tests.test_package.subpackage"
    expected_tests_path = Path("tests/test_package/subpackage")
    assert package_name_as_root_path(tests_name) == expected_tests_path


def test_root_path_as_module_name(mocker: MockerFixture) -> None:
    """Test function."""
    path = Path("src/something/another/thing")
    assert root_path_as_module_name(path) == "something.another.thing"

    test_path = Path("tests/test_something/test_another/test_thing.py")
    assert (
        root_path_as_module_name(test_path)
        == "tests.test_something.test_another.test_thing"
    )

    tests_root_mock = mocker.patch.object(
        ProjectTester.I,
        ProjectTester.tests_source_root.__name__,
        return_value=Path("tests_root"),
    )
    test_path = Path("no_tests_root/something/another/thing.py")
    assert (
        root_path_as_module_name(test_path) == "no_tests_root.something.another.thing"
    )
    tests_root_mock.assert_called_once()


def test_make_all_init_files(
    tmp_project_root_path: Path, tmp_package_root_path: tuple[Path, ModuleType]
) -> None:
    """Test function."""
    with chdir(tmp_project_root_path):
        docs = Path("docs")
        docs.mkdir()
        ProjectTester.I.tests_package_root().mkdir()
        package_root_path, _ = tmp_package_root_path
        root_init = package_root_path / "__init__.py"
        # assert ends with empty line
        root_init.unlink()
        assert not root_init.exists()

        assert set(namespace_package_paths()) == {
            PackageManager.I.package_root(),
            ProjectTester.I.tests_package_root(),
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


def test_determine_root() -> None:
    """Test function."""
    root = determine_root("testssndjsnbdjs")
    assert root == Path()
    root = determine_root("jbdjsdjsbdjsd")
    assert root == Path("src")

"""Test module."""

from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.rig.tools.project_tester import ProjectTester
from pyrig.rig.utils.paths import (
    module_name_as_root_path,
    package_name_as_root_path,
    root_path_as_module_name,
)


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

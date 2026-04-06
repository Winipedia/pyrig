"""Test module."""

from pathlib import Path

from pyrig.rig.utils.path import module_name_as_root_path, package_name_as_root_path


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

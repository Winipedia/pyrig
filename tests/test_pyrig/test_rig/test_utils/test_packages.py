"""Test module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockFixture

from pyrig.rig.configs.git.gitignore import GitignoreConfigFile
from pyrig.rig.utils import packages
from pyrig.rig.utils.packages import (
    find_namespace_packages,
    find_packages,
    src_package_is_pyrig,
)
from pyrig.rig.utils.version_control import path_is_in_ignore
from pyrig.src.modules.module import make_obj_importpath


def test_find_packages(mocker: MockFixture) -> None:
    """Test function."""
    # Mock setuptools find_packages
    mock_find_packages = mocker.patch(
        make_obj_importpath(packages) + "._find_packages",
        return_value=["package1", "package1.sub1", "package1.sub1.sub2", "package2"],
    )

    # Mock read_text of Path to return empty list (no gitignore patterns)
    mocker.patch(
        "pathlib.Path.read_text",
        return_value="",
    )

    # Test without depth limit
    result = find_packages()
    expected = ["package1", "package1.sub1", "package1.sub1.sub2", "package2"]
    assert result == expected, f"Expected {expected}, got {result}"

    # Test with depth limit
    result = find_packages(depth=1)
    expected = ["package1", "package1.sub1", "package2"]
    assert result == expected, f"Expected {expected}, got {result}"

    # Test with depth 0
    result = find_packages(depth=0)
    expected = ["package1", "package2"]
    assert result == expected, f"Expected {expected}, got {result}"

    # Verify that setuptools find_packages was called with empty exclude list
    mock_find_packages.assert_called_with(where=".", exclude=[], include=("*",))


def test_find_packages_with_namespace(mocker: MockFixture) -> None:
    """Test find_packages with namespace packages."""
    mock_find_namespace = mocker.patch(
        make_obj_importpath(packages) + "._find_namespace_packages",
        return_value=["ns_package1", "ns_package2"],
    )

    mocker.patch(
        "pathlib.Path.read_text",
        return_value="",
    )

    result = find_packages(include_namespace_packages=True)
    expected = ["ns_package1", "ns_package2"]
    assert result == expected, f"Expected {expected}, got {result}"

    mock_find_namespace.assert_called_once_with(where=".", exclude=[], include=("*",))


def test_find_packages_with_gitignore_filtering(mocker: MockFixture) -> None:
    """Test find_packages with gitignore patterns that should exclude packages."""
    # Mock setuptools find_packages to return only packages not excluded by gitignore
    mock_find_packages = mocker.patch(
        make_obj_importpath(packages) + "._find_packages",
        return_value=[
            "package1",
            "package2",
        ],  # dist and build are excluded by setuptools
    )

    # Mock load_gitignore to return patterns that should exclude dist and build
    mocker.patch(
        "pathlib.Path.read_text",
        return_value="""
dist/
build/
__pycache__/
""",
    )

    result = find_packages()
    expected = ["package1", "package2"]
    assert result == expected, f"Expected {expected}, got {result}"

    # Verify that setuptools find_packages was called with gitignore patterns
    expected_exclude = ["dist", "build", "__pycache__"]
    mock_find_packages.assert_called_with(
        where=".", exclude=expected_exclude, include=("*",)
    )


def test_find_namespace_packages(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # make package in gitignore
        GitignoreConfigFile.validate()

        (Path.cwd() / "docs").mkdir()
        assert find_namespace_packages() == []
        (Path.cwd() / "src").mkdir()
        assert find_namespace_packages() == ["src"]
        (Path.cwd() / "src" / "__init__.py").write_text("")
        assert find_namespace_packages() == []

        # assert exists
        assert (Path.cwd() / ".gitignore").exists()
        assert path_is_in_ignore("dist")

        (Path.cwd() / "dist").mkdir()
        assert find_namespace_packages() == []


def test_src_package_is_pyrig() -> None:
    """Test function."""
    assert src_package_is_pyrig()

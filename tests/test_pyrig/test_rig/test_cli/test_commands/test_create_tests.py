"""Tests module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockFixture

from pyrig.rig.cli.commands import create_tests as create_tests_module
from pyrig.rig.cli.commands.create_tests import (
    create_test_package,
    create_tests_for_package,
    make_test_skeletons,
)
from pyrig.src.modules.imports import import_package_with_dir_fallback
from pyrig.src.modules.module import (
    create_module,
    make_obj_importpath,
)
from pyrig.src.modules.package import create_package


def test_make_test_skeletons(mocker: MockFixture) -> None:
    """Test function."""
    # Mock the two main functions that create_tests calls to verify orchestration

    mock_create_tests_for_src_package = mocker.patch(
        make_obj_importpath(create_tests_module) + ".create_tests_for_package"
    )

    # Call the function
    make_test_skeletons()

    src_count = mock_create_tests_for_src_package.call_count

    assert src_count == 1, (
        f"Expected create_tests_for_src_package called once, got {src_count}"
    )


def test_create_tests_for_package(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        # Create a source package with a module
        package_path = Path("src_package")
        subpackage_path = package_path / "subpackage"
        mod1_path = package_path / "mod1.py"
        mod2_path = package_path / "mod2.py"
        sub_mod1_path = subpackage_path / "sub_mod1.py"
        sub_mod2_path = subpackage_path / "sub_mod2.py"

        # create the package and modules
        create_package(package_path)
        create_package(subpackage_path)
        create_module(mod1_path)
        create_module(mod2_path)
        create_module(sub_mod1_path)
        create_module(sub_mod2_path)

        assert mod1_path.exists()
        assert mod2_path.exists()
        assert sub_mod1_path.exists()

        package = import_package_with_dir_fallback(package_path)
        create_tests_for_package(package)

        # assert the test modules were created
        test_mod1_path = Path("tests/test_src_package/test_mod1.py")
        test_mod2_path = Path("tests/test_src_package/test_mod2.py")
        test_sub_mod1_path = Path(
            "tests/test_src_package/test_subpackage/test_sub_mod1.py"
        )
        test_sub_mod2_path = Path(
            "tests/test_src_package/test_subpackage/test_sub_mod2.py"
        )
        assert test_mod1_path.exists()
        assert test_mod2_path.exists()
        assert test_sub_mod1_path.exists()
        assert test_sub_mod2_path.exists()


def test_create_test_package(tmp_path: Path) -> None:
    """Test function."""
    package_name = create_test_package.__name__
    package_path = tmp_path / package_name
    with chdir(tmp_path):
        package = create_package(package_path)
        create_test_package(package)
        test_package_path = tmp_path / f"tests/{test_create_test_package.__name__}"
        assert test_package_path.exists()

"""module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

import pyrig
from pyrig.rig.configs.python.package_init import PackageInitConfigFile


class TestPackageInitConfigFile:
    """Test class."""

    def test_create_file(self, mocker: MockerFixture) -> None:
        """Test method."""
        spy = mocker.spy(
            PackageInitConfigFile,
            PackageInitConfigFile.I.delete_root_main.__name__,
        )
        PackageInitConfigFile.I.create_file()
        spy.assert_called_once()

    def test_delete_root_main(self, tmp_path: Path) -> None:
        """Test method."""
        with chdir(tmp_path):
            # Create a dummy main.py file
            main_file = tmp_path / "main.py"
            main_file.write_text("print('Hello, World!')")

            # Ensure the file exists
            assert main_file.exists(), "main.py should exist before deletion"

            # Call the delete_root_main method
            PackageInitConfigFile.I.delete_root_main()

            # Check that the file has been deleted
            assert not main_file.exists(), "main.py should be deleted"

    def test_src_module(self) -> None:
        """Test method."""
        module = PackageInitConfigFile.I.src_module()
        assert module == pyrig

        # get the docstring of the init file to check
        # it is generic and not pyrig specific
        docstring = module.__doc__
        assert docstring == """The top-level package for the project."""

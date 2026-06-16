"""module."""

import pyrig
from pyrig.rig.configs.package_init import PackageInitConfigFile


class TestPackageInitConfigFile:
    """Test class."""

    def test_copy_module(self) -> None:
        """Test method."""
        module = PackageInitConfigFile.I.copy_module()
        assert module == pyrig

        # get the docstring of the init file to check
        # it is generic and not pyrig specific
        docstring = module.__doc__
        assert docstring == """The top-level package for the project."""

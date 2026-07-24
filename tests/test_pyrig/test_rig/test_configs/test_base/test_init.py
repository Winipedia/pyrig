"""module."""

from pathlib import Path
from types import ModuleType

from pyrig_resources.rig.configs.resources_init import ResourcesInitConfigFile

from pyrig.rig.configs.base.init import CopyInitConfigFile
from pyrig.rig.configs.package_init import PackageInitConfigFile


class TestCopyInitConfigFile:
    """Test class."""

    def test_import_path(self) -> None:
        """Test method."""
        assert ResourcesInitConfigFile.I.import_path() == Path(
            "src/pyrig/rig/resources",
        )

    def test_module_path(self) -> None:
        """Test method."""
        # Create a mock module to test
        module = ModuleType("test_package.test_subpackage.test_subpackage2")
        module.__file__ = "test_package/test_subpackage/test_subpackage2/__init__.py"

        # Generate the subclass config file
        subclass = CopyInitConfigFile.generate_subclass(module)

        # Verify the generated subclass has the correct module_path method
        subclass_instance = subclass()
        expected_path = Path("src/pyrig/test_subpackage/test_subpackage2/__init__.py")
        actual_path = subclass_instance.module_path()
        assert actual_path == expected_path

    def test_parent_path(self) -> None:
        """Test method."""
        assert PackageInitConfigFile.I.parent_path() == Path("src/pyrig/")

    def test_stem(self) -> None:
        """Test method."""
        assert ResourcesInitConfigFile.I.stem() == "__init__"
        assert PackageInitConfigFile.I.stem() == "__init__"

"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest

from pyrig.rig import tests
from pyrig.rig.tests import mirror_test
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.src.modules.module import create_module


@pytest.fixture
def my_test_mirror_test_config_file(
    config_file_factory: Callable[
        [type[MirrorTestConfigFile]], type[MirrorTestConfigFile]
    ],
    tmp_path: Path,
) -> type[MirrorTestConfigFile]:
    """Create a test mirror test config file class with tmp_path."""
    with chdir(tmp_path):
        path = Path("mirror_test_module.py")
        # write a simple class with one method to the module
        path.write_text("""
class MirrorClass:
    def mirror_method(self):
        pass

def mirror_function():
    pass
""")
        mock_module = create_module(path)

    class MyTestMirrorTestConfigFile(config_file_factory(MirrorTestConfigFile)):  # ty:ignore[unsupported-base]
        """Test mirror test config file with tmp_path override."""

        @classmethod
        def get_src_module(cls) -> ModuleType:
            """Get the source module."""
            return mock_module

    return MyTestMirrorTestConfigFile


class TestMirrorTestConfigFile:
    """Test class."""

    def test_get_obj_from_test_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_obj_from_test_obj(TestMirrorTestConfigFile)
        assert result.__name__ == MirrorTestConfigFile.__name__

    def test_get_test_obj_from_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_test_obj_from_obj(MirrorTestConfigFile)
        assert result.__name__ == TestMirrorTestConfigFile.__name__

    def test_get_test_obj_importpath_from_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_test_obj_importpath_from_obj(
            MirrorTestConfigFile
        )
        expected = "tests.test_pyrig.test_rig.test_tests.test_mirror_test.TestMirrorTestConfigFile"  # noqa: E501
        assert result == expected

    def test_get_obj_importpath_from_test_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_obj_importpath_from_test_obj(
            TestMirrorTestConfigFile
        )
        assert result == "pyrig.rig.tests.mirror_test.MirrorTestConfigFile"

    def test_get_test_name_for_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_test_name_for_obj(MirrorTestConfigFile)
        assert result == "TestMirrorTestConfigFile"

    def test_remove_test_prefix_from_test_name(self) -> None:
        """Test method."""
        test_name = "test_mirror_method"
        obj_name = MirrorTestConfigFile.remove_test_prefix_from_test_name(test_name)
        assert obj_name == "mirror_method"

    def test_get_test_prefix_for_obj(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_test_prefix_for_obj(
            MirrorTestConfigFile.L.get_test_prefix_for_obj
        )
        assert result == "test_"
        result = MirrorTestConfigFile.get_test_prefix_for_obj(MirrorTestConfigFile)
        assert result == "Test"

    def test_get_test_prefixes(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_test_prefixes()
        assert result == ("test_", "Test", "test_")

    def test_get_test_func_prefix(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_test_func_prefix()
        assert result == "test_"

    def test_get_test_class_prefix(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_test_class_prefix()
        assert result == "Test"

    def test_get_test_module_prefix(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_test_module_prefix()
        assert result == "test_"

    def test_get_tests_package_name(self) -> None:
        """Test method."""
        result = MirrorTestConfigFile.get_tests_package_name()
        assert result == "tests"

    def test_add_missing_configs(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            my_test_mirror_test_config_file.create_file()
            assert (
                my_test_mirror_test_config_file.add_missing_configs()
                == my_test_mirror_test_config_file.get_configs()
            )

    def test_definition_package(self) -> None:
        """Test method."""
        assert MirrorTestConfigFile.definition_package() is tests

    def test_leaf(self) -> None:
        """Test method."""
        leaf = MirrorTestConfigFile.L
        assert leaf is MirrorTestConfigFile

    def test_get_src_module(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        src_module = my_test_mirror_test_config_file.get_src_module()
        assert src_module.__name__ == "mirror_test_module"

    def test_get_filename(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        filename = my_test_mirror_test_config_file.get_filename()
        assert filename == "test_mirror_test_module"

    def test_get_parent_path(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        # tmp path bc factory of pattern in config_file_factory
        with chdir(tmp_path):
            parent_path = my_test_mirror_test_config_file.get_parent_path()
            assert parent_path == Path(MirrorTestConfigFile.get_tests_package_name())

    def test_get_lines(
        self,
        my_test_mirror_test_config_file: type[MirrorTestConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            # create the file first to not trigger dump in get_content_str
            my_test_mirror_test_config_file.create_file()
            lines = my_test_mirror_test_config_file.get_lines()
            content = "\n".join(lines)
            assert "def test_mirror_method" in content
            assert "def test_mirror_function" in content
            assert "class TestMirrorClass" in content

    def test_override_content(self) -> None:
        """Test method."""
        assert MirrorTestConfigFile.override_content(), "Expected True"

    def test_is_correct(self) -> None:
        """Test method."""
        subclass = MirrorTestConfigFile.make_subclass_for_module(mirror_test)
        assert subclass.is_correct()

    def test_get_test_path(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        test_path = my_test_mirror_test_config_file.get_test_path()
        assert test_path == Path("tests/test_mirror_test_module.py")

    def test_get_test_module_name(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        test_module_name = my_test_mirror_test_config_file.get_test_module_name()
        assert test_module_name == "tests.test_mirror_test_module"

    def test_get_test_module_name_from_src_module(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        test_module_name = (
            my_test_mirror_test_config_file.get_test_module_name_from_src_module(
                my_test_mirror_test_config_file.get_src_module()
            )
        )
        assert test_module_name == "tests.test_mirror_test_module"

    def test_get_test_module(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        test_module = my_test_mirror_test_config_file.get_test_module()
        assert test_module.__name__ == "tests.test_mirror_test_module"

    def test_get_test_module_content_with_skeletons(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        # create the file first
        my_test_mirror_test_config_file.create_file()
        content = (
            my_test_mirror_test_config_file.get_test_module_content_with_skeletons()
        )
        assert "def test_mirror_method" in content
        assert "def test_mirror_function" in content
        assert "class TestMirrorClass" in content

    def test_get_test_module_content_with_func_skeletons(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        # create the file first
        my_test_mirror_test_config_file.create_file()
        content = (
            my_test_mirror_test_config_file.get_test_module_content_with_func_skeletons(
                my_test_mirror_test_config_file.get_test_module_content_with_skeletons()
            )
        )
        assert "def test_mirror_method" in content
        assert "def test_mirror_function" in content
        assert "class TestMirrorClass" in content

    def test_get_untested_func_names(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        # create the file first
        my_test_mirror_test_config_file.create_file()
        untested_func_names = my_test_mirror_test_config_file.get_untested_func_names()
        assert len(untested_func_names) > 0

    def test_get_test_func_skeleton(self) -> None:
        """Test method."""
        skeleton = MirrorTestConfigFile.get_test_func_skeleton("test_func")
        assert "def test_func" in skeleton
        assert "NotImplementedError" in skeleton

    def test_get_test_module_content_with_class_skeletons(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        # create the file first
        my_test_mirror_test_config_file.create_file()
        content = my_test_mirror_test_config_file.get_test_module_content_with_class_skeletons(  # noqa: E501
            my_test_mirror_test_config_file.get_test_module_content_with_skeletons()
        )
        assert "def test_mirror_method" in content
        assert "def test_mirror_function" in content
        assert "class TestMirrorClass" in content

    def test_get_untested_class_and_method_names(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        # create the file first
        my_test_mirror_test_config_file.create_file()
        untested_class_and_method_names = (
            my_test_mirror_test_config_file.get_untested_class_and_method_names()
        )
        assert len(untested_class_and_method_names) > 0

    def test_get_test_class_skeleton(self) -> None:
        """Test method."""
        skeleton = MirrorTestConfigFile.get_test_class_skeleton("TestClass")
        assert "class TestClass" in skeleton

    def test_get_test_method_skeleton(self) -> None:
        """Test method."""
        skeleton = MirrorTestConfigFile.get_test_method_skeleton("test_method")
        assert "def test_method" in skeleton
        assert "NotImplementedError" in skeleton

    def test_make_subclasses_for_modules(self) -> None:
        """Test method."""
        subclasses = MirrorTestConfigFile.make_subclasses_for_modules([mirror_test])
        assert len(subclasses) > 0

    def test_make_subclass_for_module(self) -> None:
        """Test method."""
        subclass = MirrorTestConfigFile.make_subclass_for_module(mirror_test)
        assert subclass.get_src_module() == mirror_test

    def test_create_test_modules(self) -> None:
        """Test method."""
        MirrorTestConfigFile.create_test_modules([mirror_test])

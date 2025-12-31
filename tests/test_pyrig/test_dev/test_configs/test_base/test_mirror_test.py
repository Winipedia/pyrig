"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType

import pytest

from pyrig.dev.configs.base.mirror_test import MirrorTestConfigFile
from pyrig.src.modules.module import create_module
from pyrig.src.modules.package import get_objs_from_obj
from pyrig.src.testing.convention import TESTS_PACKAGE_NAME


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
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        parent_path = my_test_mirror_test_config_file.get_parent_path()
        assert parent_path == Path(TESTS_PACKAGE_NAME)

    def test_get_content_str(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        content = my_test_mirror_test_config_file.get_content_str()
        assert "def test_mirror_method" in content
        assert "def test_mirror_function" in content
        assert "class TestMirrorClass" in content

    def test__dump(
        self, my_test_mirror_test_config_file: type[MirrorTestConfigFile]
    ) -> None:
        """Test method."""
        module = my_test_mirror_test_config_file.get_test_module()
        objs = get_objs_from_obj(module)
        my_test_mirror_test_config_file()
        module_after = my_test_mirror_test_config_file.get_test_module()
        objs_after = get_objs_from_obj(module_after)
        assert len(objs_after) > len(objs)

    def test_override_content(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_is_correct(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_path(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_module_name(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_module_name_from_src_module(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_module(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_module_content_with_skeletons(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_module_content_with_func_skeletons(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_untested_func_names(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_func_skeleton(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_module_content_with_class_skeletons(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_untested_class_and_method_names(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_class_skeleton(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_get_test_method_skeleton(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_make_subclasses_for_modules(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_make_subclass_for_module(self) -> None:
        """Test method."""
        raise NotImplementedError

    def test_create_test_modules(self) -> None:
        """Test method."""
        raise NotImplementedError

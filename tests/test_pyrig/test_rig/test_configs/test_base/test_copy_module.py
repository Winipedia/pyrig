"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile
from pyrig.rig.configs.base.py_package import PythonPackageConfigFile


@pytest.fixture
def my_test_copy_module_config_file(
    config_file_factory: Callable[
        [type[PythonPackageConfigFile]], type[PythonPackageConfigFile]
    ],
    tmp_path: Path,
) -> type[PythonPackageConfigFile]:
    """Create a test copy module config file class with tmp_path."""
    # Create a mock module for testing

    mock_module = ModuleType("test_package.test_subpackage.test_module")
    mock_module.__file__ = str(
        tmp_path / "test_package" / "test_subpackage" / "test_module.py"
    )

    # Create the module file with some content
    module_path = Path(mock_module.__file__)
    module_path.parent.mkdir(parents=True, exist_ok=True)
    test_content = (
        '"""Test module content."""\n\n'
        "def test_func():\n"
        '    """Test function."""\n'
        "    pass\n"
    )
    module_path.write_text(test_content)

    class MyTestCopyModuleConfigFile(config_file_factory(CopyModuleConfigFile)):  # type: ignore [misc]
        """Test copy module config file with tmp_path override."""

        def src_module(self) -> ModuleType:
            """Get the source module."""
            return mock_module

        def _dump(self, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config file."""
            with chdir(tmp_path):
                super()._dump(config)

    return MyTestCopyModuleConfigFile


class TestCopyModuleConfigFile:
    """Test class."""

    def test_src_module(
        self, my_test_copy_module_config_file: type[CopyModuleConfigFile]
    ) -> None:
        """Test method."""
        src_module = my_test_copy_module_config_file().src_module()
        assert isinstance(src_module, ModuleType), "Expected ModuleType"
        expected_name = "test_package.test_subpackage.test_module"
        assert src_module.__name__ == expected_name, (
            f"Expected '{expected_name}', got {src_module.__name__}"
        )

    def test_parent_path(
        self, my_test_copy_module_config_file: type[CopyModuleConfigFile]
    ) -> None:
        """Test method."""
        parent_path = my_test_copy_module_config_file().parent_path()
        assert isinstance(parent_path, Path), "Expected Path"

    def test_lines(
        self, my_test_copy_module_config_file: type[CopyModuleConfigFile]
    ) -> None:
        """Test method."""
        lines = my_test_copy_module_config_file().lines()
        content_str = "\n".join(lines)
        assert len(content_str) > 0, "Expected non-empty string"
        # Verify it contains the module content
        assert "Test module content" in content_str, "Expected module content in string"

    def test_filename(
        self, my_test_copy_module_config_file: type[CopyModuleConfigFile]
    ) -> None:
        """Test method."""
        filename = my_test_copy_module_config_file().filename()
        assert filename == "test_module", f"Expected 'test_module', got {filename}"

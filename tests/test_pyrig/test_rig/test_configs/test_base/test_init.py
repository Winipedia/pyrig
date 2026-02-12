"""module."""

from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

from pyrig.rig.configs.base.init import InitConfigFile


@pytest.fixture
def my_test_init_config_file(
    config_file_factory: Callable[[type[InitConfigFile]], type[InitConfigFile]],
    tmp_path: Path,
) -> type[InitConfigFile]:
    """Create a test init config file class with tmp_path."""
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

    class MyTestInitConfigFile(
        config_file_factory(InitConfigFile),  # type: ignore [misc]
    ):
        """Test init config file with tmp_path override."""

        @classmethod
        def src_module(cls) -> ModuleType:
            """Get the source module."""
            return mock_module

    return MyTestInitConfigFile


class TestInitConfigFile:
    """Test class."""

    def test_parent_path(self, my_test_init_config_file: type[InitConfigFile]) -> None:
        """Test method."""
        assert isinstance(my_test_init_config_file.parent_path(), Path)

    def test_filename(self, my_test_init_config_file: type[InitConfigFile]) -> None:
        """Test method."""
        expected = "__init__"
        actual = my_test_init_config_file.filename()
        assert expected == actual, f"Expected {expected}, got {actual}"

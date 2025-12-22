"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from pyrig.dev.configs.base.copy_module_docstr import CopyModuleOnlyDocstringConfigFile


@pytest.fixture
def my_test_copy_module_only_docstring_config_file(
    config_file_factory: Callable[
        [type[CopyModuleOnlyDocstringConfigFile]],
        type[CopyModuleOnlyDocstringConfigFile],
    ],
    tmp_path: Path,
) -> type[CopyModuleOnlyDocstringConfigFile]:
    """Create a test copy module only docstring config file class with tmp_path."""
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

    class MyTestCopyModuleOnlyDocstringConfigFile(
        config_file_factory(CopyModuleOnlyDocstringConfigFile)  # type: ignore [misc]
    ):
        """Test copy module only docstring config file with tmp_path override."""

        @classmethod
        def get_src_module(cls) -> ModuleType:
            """Get the source module."""
            return mock_module

        @classmethod
        def dump(cls, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config file."""
            with chdir(tmp_path):
                super().dump(config)

    return MyTestCopyModuleOnlyDocstringConfigFile


class TestCopyModuleOnlyDocstringConfigFile:
    """Test class."""

    def test_get_content_str(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleOnlyDocstringConfigFile
        ],
    ) -> None:
        """Test method."""
        content_str = my_test_copy_module_only_docstring_config_file.get_content_str()

        # assert its only the docstring
        assert content_str == '"""Test module content."""\n', (
            "Expected only docstring in string"
        )

    @pytest.mark.skip(reason="Problems with tmp paths.")
    def test_is_correct(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleOnlyDocstringConfigFile
        ],
    ) -> None:
        """Test method."""

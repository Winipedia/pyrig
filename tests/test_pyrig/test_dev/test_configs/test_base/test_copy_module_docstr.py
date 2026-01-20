"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from pyrig.dev.configs.base.copy_module_docstr import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.configs.licence import LicenceConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile


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
    mock_module.__doc__ = "Test module content."

    # Create the module file with some content
    module_path = Path(mock_module.__file__)
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text(mock_module.__doc__)

    class MyTestCopyModuleOnlyDocstringConfigFile(
        config_file_factory(CopyModuleOnlyDocstringConfigFile)  # type: ignore [misc]
    ):
        """Test copy module only docstring config file with tmp_path override."""

        @classmethod
        def get_src_module(cls) -> ModuleType:
            """Get the source module."""
            return mock_module

        @classmethod
        def _dump(cls, config: dict[str, Any] | list[Any]) -> None:
            """Dump the config file."""
            with chdir(tmp_path):
                super()._dump(config)

    return MyTestCopyModuleOnlyDocstringConfigFile


class TestCopyModuleOnlyDocstringConfigFile:
    """Test class."""

    def test_get_lines(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleOnlyDocstringConfigFile
        ],
    ) -> None:
        """Test method."""
        lines = my_test_copy_module_only_docstring_config_file.get_lines()
        content_str = "\n".join(lines)

        # assert its only the docstring
        # note with extra newline at the end
        assert content_str == '"""Test module content."""', (
            "Expected only docstring in string"
        )

    def test_is_correct(
        self,
        my_test_copy_module_only_docstring_config_file: type[
            CopyModuleOnlyDocstringConfigFile
        ],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            LicenceConfigFile()
            PyprojectConfigFile()
            my_test_copy_module_only_docstring_config_file()
            assert my_test_copy_module_only_docstring_config_file.is_correct()

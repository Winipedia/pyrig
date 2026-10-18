"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_module
"""

from pathlib import Path
from types import ModuleType

from pyrig.core.introspection.modules import (
    leaf_module_name,
    module_content,
)


def test_module_content(tmp_path: Path) -> None:
    """Test function."""
    module_path = tmp_path / "example.py"
    content = '"""Test module."""\n\nvalue = 1\n'
    module_path.write_text(content)
    module = ModuleType("example")
    module.__file__ = str(module_path)
    assert module_content(module) == content

    module_path.write_text("value = 2\n")
    assert module_content(module) == "value = 2\n"


def test_leaf_module_name() -> None:
    """Test function."""
    assert leaf_module_name(ModuleType("package.subcommands")) == "subcommands"

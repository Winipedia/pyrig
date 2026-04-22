"""Tests module."""

import re
from pathlib import Path
from types import ModuleType

from pyrig.core.strings import (
    kebab_to_snake_case,
    make_linked_badge_markdown,
    make_name_from_obj,
    make_summary_error_msg,
    package_req_name_split_pattern,
    read_text_utf8,
    snake_to_kebab_case,
    split_on_uppercase,
    write_text_utf8,
)
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger


def test_kebab_to_snake_case() -> None:
    """Test function."""
    project_name = "test-project"
    package_name = kebab_to_snake_case(project_name)
    expected_package_name = "test_project"
    assert package_name == expected_package_name


def test_snake_to_kebab_case() -> None:
    """Test function."""
    package_name = "test_project"
    project_name = snake_to_kebab_case(package_name)
    expected_project_name = "test-project"
    assert project_name == expected_project_name


def test_project_name_from_cwd() -> None:
    """Test function."""
    project_name = PackageManager.I.project_name()
    expected_project_name = Pyrigger.I.name()
    assert project_name == expected_project_name


def test_split_on_uppercase() -> None:
    """Test function."""
    # Test with simple string
    result = list(split_on_uppercase("HelloWorld"))
    assert result == ["Hello", "World"]

    # Test with multiple uppercase letters
    result = list(split_on_uppercase("SplitCamelCase"))
    assert result == ["Split", "Camel", "Case"], (
        f"Expected ['Split', 'Camel', 'Case'], got {result}"
    )

    # Test with all uppercase
    result = list(split_on_uppercase("ALLUPPERCASE"))
    assert result == list("ALLUPPERCASE"), (
        f"Expected {list('ALLUPPERCASE')}, got {result}"
    )

    # Test with all lowercase
    result = list(split_on_uppercase("alllowercase"))
    assert result == ["alllowercase"]

    # test with numbers
    result = list(split_on_uppercase("split1Camel2Case"))
    assert result == ["split1", "Camel2", "Case"], (
        f"Expected ['split1', 'Camel2', 'Case'], got {result}"
    )

    # entire sentence
    result = list(split_on_uppercase("Split some Camel Case"))
    expected = ["Split some ", "Camel ", "Case"]
    assert result == expected


def test_make_name_from_obj() -> None:
    """Test function."""
    # Create mock source package
    mock_src_package = ModuleType("some_package")
    mock_src_package.__name__ = "some_package"

    result = make_name_from_obj(mock_src_package)
    expected = "Some-Package"
    assert result == expected, f"Expected '{expected}', got '{result}'"

    result = make_name_from_obj(mock_src_package, capitalize=False)
    expected = "some-package"
    assert result == expected, f"Expected '{expected}', got '{result}'"


def test_make_summary_error_msg() -> None:
    """Test func."""
    # Test with empty list
    empty_msg = make_summary_error_msg([])
    assert isinstance(empty_msg, str)

    # Test with one item
    one_item_msg = make_summary_error_msg([Path("error_file.py")])
    assert isinstance(one_item_msg, str)

    # Test with multiple items
    items = [
        Path("path/to/error_file1.py"),
        Path("path/to/error_file2.py"),
        Path("path/to/error_file3.py"),
    ]
    multi_item_msg = make_summary_error_msg(items)
    assert isinstance(multi_item_msg, str)

    for item in items:
        assert str(item) in multi_item_msg


def test_make_linked_badge_markdown() -> None:
    """Test function."""
    result = make_linked_badge_markdown(
        badge_url="https://example.com/badge.svg",
        link_url="https://example.com/",
        alt_text="Example Badge",
    )
    expected = "[![Example Badge](https://example.com/badge.svg)](https://example.com/)"
    assert result == expected, f"Expected '{expected}', got '{result}'"


def test_package_req_name_split_pattern() -> None:
    """Test function."""
    result = package_req_name_split_pattern()
    assert isinstance(result, re.Pattern), (
        f"Expected a compiled regex pattern, got {type(result)}"
    )


def test_read_text_utf8(tmp_path: Path) -> None:
    """Test function."""
    text = "Hello, world! 👋"
    file_path = tmp_path / "test.txt"
    file_path.write_text(text, encoding="utf-8")

    result = read_text_utf8(file_path)
    assert result == text

    # assert the function .read_text is not used in this project
    # to ensure consistent UTF-8 encoding handling
    source_path = PackageManager.I.source_root()
    for source_file in source_path.rglob("*.py"):
        content = source_file.read_text(encoding="utf-8")
        # skip the file if def read_text_utf8 is defined in it,
        # since it is the only one supposed to use .read_text internally
        if "def read_text_utf8(path: Path) -> str:" in content:
            continue
        assert ".read_text(" not in content, (
            f"Direct use of .read_text detected in {source_file}. "
            "Use read_text_utf8() instead for consistent UTF-8 handling."
        )


def test_write_text_utf8(tmp_path: Path) -> None:
    """Test function."""
    text = "Hello, world! 👋"
    file_path = tmp_path / "test_write.txt"
    write_text_utf8(file_path, text)

    result = file_path.read_text(encoding="utf-8")
    assert result == text

    # assert the function .write_text is not used in this project
    # to ensure consistent UTF-8 encoding handling
    source_path = PackageManager.I.source_root()
    for source_file in source_path.rglob("*.py"):
        content = source_file.read_text(encoding="utf-8")
        # skip the file if def write_text_utf8 is defined in it,
        # since it is the only one supposed to use .write_text internally
        if "def write_text_utf8(path: Path, content: str) -> int:" in content:
            continue
        assert ".write_text(" not in content, (
            f"Direct use of .write_text detected in {source_file}. "
            "Use write_text_utf8() instead for consistent UTF-8 handling."
        )

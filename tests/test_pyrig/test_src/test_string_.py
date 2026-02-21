"""Tests module."""

import re
from types import ModuleType

import pytest

import pyrig
from pyrig.src.string_ import (
    kebab_to_snake_case,
    make_linked_badge_markdown,
    make_name_from_obj,
    make_summary_error_msg,
    package_name_from_cwd,
    package_req_name_split_pattern,
    project_name_from_cwd,
    re_search_excluding_docstrings,
    snake_to_kebab_case,
    split_on_uppercase,
)


def test_kebab_to_snake_case() -> None:
    """Test function."""
    project_name = "test-project"
    package_name = kebab_to_snake_case(project_name)
    expected_package_name = "test_project"
    assert package_name == expected_package_name, (
        f"Expected {expected_package_name}, got {package_name}"
    )


def test_snake_to_kebab_case() -> None:
    """Test function."""
    package_name = "test_project"
    project_name = snake_to_kebab_case(package_name)
    expected_project_name = "test-project"
    assert project_name == expected_project_name, (
        f"Expected {expected_project_name}, got {project_name}"
    )


def test_project_name_from_cwd() -> None:
    """Test function."""
    project_name = project_name_from_cwd()
    expected_project_name = pyrig.__name__
    assert project_name == expected_project_name, (
        f"Expected {expected_project_name}, got {project_name}"
    )


def test_package_name_from_cwd() -> None:
    """Test function."""
    package_name = package_name_from_cwd()
    expected_package_name = pyrig.__name__
    assert package_name == expected_package_name, (
        f"Expected {expected_package_name}, got {package_name}"
    )


def test_split_on_uppercase() -> None:
    """Test function."""
    # Test with simple string
    result = list(split_on_uppercase("HelloWorld"))
    assert result == ["Hello", "World"], f"Expected ['Hello', 'World'], got {result}"

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
    assert result == ["alllowercase"], f"Expected ['alllowercase'], got {result}"

    # test with numbers
    result = list(split_on_uppercase("split1Camel2Case"))
    assert result == ["split1", "Camel2", "Case"], (
        f"Expected ['split1', 'Camel2', 'Case'], got {result}"
    )

    # entire sentence
    result = list(split_on_uppercase("Split some Camel Case"))
    expected = ["Split some ", "Camel ", "Case"]
    assert result == expected, f"Expected {expected}, got {result}"


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


def test_make_name_from_obj_empty_input() -> None:
    """Test that empty or separator-only inputs raise ValueError."""
    # Empty string should raise ValueError
    with pytest.raises(ValueError, match="no valid parts"):
        make_name_from_obj("")

    # String with only separators should raise ValueError
    with pytest.raises(ValueError, match="no valid parts"):
        make_name_from_obj("_")

    with pytest.raises(ValueError, match="no valid parts"):
        make_name_from_obj("__")

    with pytest.raises(ValueError, match="no valid parts"):
        make_name_from_obj("___")


def test_re_search_excluding_docstrings() -> None:
    """Test function."""
    content = '''"""Test module."""

def test_function() -> str:
    """Test function."""
    return "test"
'''
    # first pattern is: Test module.
    pattern = r"Test\s+module\."
    result = re_search_excluding_docstrings(pattern, content)
    # should not find bc it is in docstring
    assert result is None, f"Expected no match for '{pattern}', got {result}"

    # second pattern is: Test function.
    pattern = r"Test\s+function\."
    result = re_search_excluding_docstrings(pattern, content)
    # should not find bc it is in docstring
    assert result is None, f"Expected no match for '{pattern}', got {result}"

    # third pattern is: return "test"
    pattern = r'return\s+"test"'
    result = re_search_excluding_docstrings(pattern, content)
    # should find it
    assert result is not None, f"Expected match for '{pattern}', got {result}"

    # Unclosed docstring - content inside will NOT be excluded
    unclosed_content = '''"""This docstring is never closed
some_code = True
'''
    pattern = r"some_code"
    result = re_search_excluding_docstrings(pattern, unclosed_content)
    # This WILL match because the unclosed docstring is not stripped
    # This is documented behavior, not a bug
    assert result is not None, "Expected match in unclosed docstring (known limitation)"


def test_make_summary_error_msg() -> None:
    """Test func."""
    # Test with empty list
    empty_msg = make_summary_error_msg([])
    assert isinstance(empty_msg, str)

    # Test with one item
    one_item_msg = make_summary_error_msg(["module.function"])
    assert isinstance(one_item_msg, str)

    # Test with multiple items
    items = ["module.function1", "module.class.method", "another_module"]
    multi_item_msg = make_summary_error_msg(items)
    assert isinstance(multi_item_msg, str)

    for item in items:
        assert item in multi_item_msg


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

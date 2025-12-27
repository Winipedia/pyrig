"""Tests module."""

from types import ModuleType

from pyrig.src.string import (
    make_name_from_obj,
    re_search_excluding_docstrings,
    split_on_uppercase,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_split_on_uppercase() -> None:
    """Test func for split_on_uppercase."""
    # Test with simple string
    result = split_on_uppercase("HelloWorld")
    assert_with_msg(
        result == ["Hello", "World"],
        f"Expected ['Hello', 'World'], got {result}",
    )

    # Test with multiple uppercase letters
    result = split_on_uppercase("SplitCamelCase")
    assert_with_msg(
        result == ["Split", "Camel", "Case"],
        f"Expected ['Split', 'Camel', 'Case'], got {result}",
    )

    # Test with all uppercase
    result = split_on_uppercase("ALLUPPERCASE")
    assert_with_msg(
        result == list("ALLUPPERCASE"),
        f"Expected {list('ALLUPPERCASE')}, got {result}",
    )

    # Test with all lowercase
    result = split_on_uppercase("alllowercase")
    assert_with_msg(
        result == ["alllowercase"],
        f"Expected ['alllowercase'], got {result}",
    )

    # test with numbers
    result = split_on_uppercase("split1Camel2Case")
    assert_with_msg(
        result == ["split1", "Camel2", "Case"],
        f"Expected ['split1', 'Camel2', 'Case'], got {result}",
    )

    # entire sentence
    result = split_on_uppercase("Split some Camel Case")
    expected = ["Split some ", "Camel ", "Case"]
    assert_with_msg(
        result == expected,
        f"Expected {expected}, got {result}",
    )


def test_make_name_from_obj() -> None:
    """Test func for make_project_name."""
    # Create mock source package
    mock_src_package = ModuleType("some_package")
    mock_src_package.__name__ = "some_package"

    result = make_name_from_obj(mock_src_package)
    expected = "Some-Package"
    assert_with_msg(
        result == expected,
        f"Expected '{expected}', got '{result}'",
    )

    result = make_name_from_obj(mock_src_package, capitalize=False)
    expected = "some-package"
    assert_with_msg(
        result == expected,
        f"Expected '{expected}', got '{result}'",
    )


def test_re_search_excluding_docstrings() -> None:
    """Test func for re_search_excluding_docstrings."""
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

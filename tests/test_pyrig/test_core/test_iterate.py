"""module."""

from typing import Any

from pyrig.core.iterate import (
    both_dicts,
    both_dicts_or_lists,
    both_lists,
    iterator_has_items,
    match_list_items,
    merge_nested_structures,
    nested_structure_is_subset,
)


def test_iterator_has_items() -> None:
    """Test function."""
    iterable_with_items = [1, 2, 3]
    gen = (x for x in iterable_with_items)
    has_items, items = iterator_has_items(gen)
    assert has_items is True
    assert list(items) == iterable_with_items

    empty_iterable: list[Any] = []
    gen = (x for x in empty_iterable)
    has_items, items = iterator_has_items(gen)
    assert has_items is False
    assert list(items) == []


def test_merge_nested_structures() -> None:
    """Test function."""
    # conflicting primitive is overwritten; missing list item and nested value
    # are filled in; superset-only key is preserved.
    subset = {"a": 1, "b": [2, 3, {"c": 4}]}
    superset = {"a": 0, "b": [2, {"c": 5}], "d": 6}
    merged = merge_nested_structures(subset, superset)
    assert merged == {"a": 1, "b": [2, 3, {"c": 4}], "d": 6}

    # an already-satisfied key is left untouched; superset-only key is kept.
    assert merge_nested_structures({"a": 1}, {"a": 1, "z": 9}) == {"a": 1, "z": 9}

    # a required null-valued key that is absent is added ("missing" is not
    # conflated with "present and None").
    assert merge_nested_structures({"x": None}, {}) == {"x": None}

    # list: items missing from a shorter superset are appended.
    assert merge_nested_structures([2, 3], [2]) == [2, 3]

    # list: a not-yet-contained item is merged into the positional element.
    assert merge_nested_structures([[1, 2]], [[1]]) == [[1, 2]]

    # mismatched top-level container types leave the superset untouched.
    assert merge_nested_structures({"a": 1}, [1]) == [1]

    assert merge_nested_structures([1, 1, "", 1, ""], []) == [1, 1, "", 1, ""]

    assert merge_nested_structures({"key": [1, 1, "", 1, ""]}, {"key": [1, 2]}) == {
        "key": [1, 1, "", 1, "", 2],
    }


def test_nested_structure_is_subset() -> None:
    """Test function."""
    # extra keys and list items in the superset are allowed.
    assert nested_structure_is_subset(
        {"a": 1, "b": [2, 3, {"c": 4}]},
        {"a": 1, "b": [2, 3, {"c": 4}, 5], "d": 6},
    )
    # a differing nested primitive breaks containment.
    assert not nested_structure_is_subset(
        {"a": 1, "b": [2, 3, {"c": 4}]},
        {"a": 1, "b": [2, 3, {"c": 5}]},
    )
    # list matching is order-independent.
    assert nested_structure_is_subset(
        {"b": [2, 3, {"d": 5}, {"c": 4}]},
        {"b": [3, 2, {"c": 4}, {"d": 5}]},
    )
    # a required null-valued key that is absent is NOT contained.
    assert not nested_structure_is_subset({"a": None}, {})
    assert not nested_structure_is_subset([1, None], [1])
    # primitives compare by equality.
    assert nested_structure_is_subset(1, 1)


def test_both_dicts_or_lists() -> None:
    """Test function."""
    assert both_dicts_or_lists({}, {"a": 1})
    assert both_dicts_or_lists([1], [])
    assert not both_dicts_or_lists({}, [])
    assert not both_dicts_or_lists({}, 1)
    assert not both_dicts_or_lists(1, 2)


def test_both_dicts() -> None:
    """Test function."""
    assert both_dicts({}, {"a": 1})
    assert not both_dicts({}, [])
    assert not both_dicts({}, 1)
    assert not both_dicts(1, 2)


def test_both_lists() -> None:
    """Test function."""
    assert both_lists([], [1])
    assert not both_lists([], {})
    assert not both_lists([], 1)
    assert not both_lists(1, 2)


def test_match_list_items() -> None:
    """Test function."""
    # a value present once can satisfy only one occurrence in subset.
    assert match_list_items(["", ""], [""]) == [True, False]

    # each superset item is matched by at most one subset item.
    assert match_list_items(["", "a", ""], ["", "z"]) == [True, False, False]

    # order does not matter, and every subset item gets a distinct match.
    assert match_list_items([1, 2], [2, 1, 3]) == [True, True]

    # nested subset semantics still apply per matched item.
    assert match_list_items([{"a": 1}], [{"a": 1, "b": 2}]) == [True]

    assert match_list_items([], []) == []

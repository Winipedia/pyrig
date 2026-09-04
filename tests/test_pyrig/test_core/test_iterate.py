"""module."""

from typing import Any

from pyrig.core.iterate import (
    both_dicts,
    both_dicts_or_lists,
    both_lists,
    deep_sorted_dict,
    dict_insert,
    iterator_has_items,
    match_list_items,
    merge_structures,
    structure_is_subset,
    traverse_structure,
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


def test_merge_structures() -> None:
    """Test function."""
    # conflicting primitive is NOT overridden; missing list item and
    # superset-only key are pulled into subset.
    subset = {"a": 1, "b": [2, 3]}
    superset = {"a": 0, "b": [2], "d": 6}
    merged = merge_structures(subset, superset)
    assert merged == {"a": 1, "b": [2, 3], "d": 6}

    # a key missing from subset is inserted at its position in superset,
    # not just appended at the end.
    subset = {"a": 1, "c": 3}
    superset = {"a": 0, "b": 2, "c": 3, "d": 4}
    merged = merge_structures(subset, superset)
    assert merged == {"a": 1, "b": 2, "c": 3, "d": 4}
    assert list(merged.keys()) == ["a", "b", "c", "d"]

    # an already-satisfied key is left untouched; superset-only key is pulled in.
    assert merge_structures({"a": 1}, {"a": 1, "z": 9}) == {"a": 1, "z": 9}

    # a key already present with a null value is untouched by an empty superset
    # ("missing" is not conflated with "present and None").
    assert merge_structures({"x": None}, {}) == {"x": None}

    # a null-valued key absent from subset is pulled in from superset.
    assert merge_structures({}, {"x": None}) == {"x": None}

    # list: items missing from a shorter subset are inserted from superset.
    assert merge_structures([2], [2, 3]) == [2, 3]

    # list: a not-yet-contained item is merged into the positional element.
    assert merge_structures([[1]], [[1, 2]]) == [[1, 2]]

    # mismatched top-level container types leave subset untouched.
    assert merge_structures({"a": 1}, [1]) == {"a": 1}

    assert merge_structures([], [1, 1, "", 1, ""]) == [1, 1, "", 1, ""]

    assert merge_structures({"key": [1, 2]}, {"key": [1, 1, "", 1, ""]}) == {
        "key": [1, 1, "", 1, "", 2],
    }


def test_structure_is_subset() -> None:
    """Test function."""
    # extra keys and list items in the superset are allowed.
    assert structure_is_subset(
        {"a": 1, "b": [2, 3, {"c": 4}]},
        {"a": 1, "b": [2, 3, {"c": 4}, 5], "d": 6},
    )
    # a differing nested primitive breaks containment.
    assert not structure_is_subset(
        {"a": 1, "b": [2, 3, {"c": 4}]},
        {"a": 1, "b": [2, 3, {"c": 5}]},
    )
    # list matching is order-independent.
    assert structure_is_subset(
        {"b": [2, 3, {"d": 5}, {"c": 4}]},
        {"b": [3, 2, {"c": 4}, {"d": 5}]},
    )
    # a required null-valued key that is absent is NOT contained.
    assert not structure_is_subset({"a": None}, {})
    assert not structure_is_subset([1, None], [1])
    # primitives compare by equality.
    assert structure_is_subset(1, 1)


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


def test_deep_sorted_dict() -> None:
    """Test function."""
    unsorted: dict[str, Any] = {
        "b": 2,
        "a": {"d": 4, "c": 3},
        "e": [{"g": 7, "f": 6}, {"i": 9, "h": 8}],
    }
    sorted_dict = deep_sorted_dict(unsorted)
    assert list(sorted_dict.keys()) == ["a", "b", "e"]
    assert list(sorted_dict["a"].keys()) == ["c", "d"]
    assert list(sorted_dict["e"][0].keys()) == ["f", "g"]
    assert list(sorted_dict["e"][1].keys()) == ["h", "i"]

    assert sorted_dict == unsorted  # values are unchanged
    assert sorted_dict is not unsorted  # a new dict is returned


def test_dict_insert() -> None:
    """Test function."""
    d = {"a": 1, "b": 2}
    dict_insert(d, index=1, key="c", value=3)
    assert d == {"a": 1, "c": 3, "b": 2}

    d = {"a": 1, "b": 2, "c": 3, "d": 4}
    dict_insert(d, index=0, key="c", value=5)
    assert d == {"c": 5, "a": 1, "b": 2, "d": 4}

    d = {"a": 1, "b": 2, "c": 3, "d": 4}
    dict_insert(d, index=2, key="b", value=5)
    assert d == {"a": 1, "c": 3, "b": 5, "d": 4}

    d = {"a": 1, "b": 2, "c": 3, "d": 4}
    dict_insert(d, index=10, key="e", value=5)
    assert d == {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}


def test_traverse_structure() -> None:
    """Test function."""
    result = list(traverse_structure({"a": [1, {"b": 2}], "c": 3}))
    assert result == [1, 2, 3]

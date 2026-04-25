"""module."""

from typing import Any

from pyrig.core.iterate import (
    add_missing_dict_val,
    combine_generators,
    empty_generator,
    generator_has_items,
    generator_length,
    insert_missing_list_val,
    merge_nested_structures,
    nested_structure_is_subset,
)


def test_nested_structure_is_subset() -> None:
    """Test function."""
    subset: dict[str, Any] = {
        "a": 1,
        "b": [2, 3, {"c": 4}],
    }
    superset: dict[str, Any] = {
        "a": 1,
        "b": [2, 3, {"c": 4}, 5],
        "d": 6,
    }
    assert nested_structure_is_subset(subset, superset), (
        "Expected subset to be subset of superset"
    )

    subset = {
        "a": 1,
        "b": [2, 3, {"c": 4}],
    }
    superset = {
        "a": 1,
        "b": [2, 3, {"c": 5}],
    }
    assert not nested_structure_is_subset(subset, superset), (
        "Expected subset not to be subset of superset"
    )

    false_values: list[Any] = []

    def on_dict_mismatch(
        subset_obj: dict[str, Any], _superset_obj: dict[str, Any], key: str
    ) -> None:
        fv = subset_obj[key]
        false_values.append(fv)

    def on_list_mismatch(
        subset_obj: list[Any], _superset_obj: list[Any], index: int
    ) -> None:
        fv = subset_obj[index]
        false_values.append(fv)

    subset = {
        "a": 1,
        "b": [2, 0, {"c": 4}],
    }
    superset = {
        "a": 1,
        "b": [2, 3, {"c": 5}],
    }
    nested_structure_is_subset(subset, superset, on_dict_mismatch, on_list_mismatch)
    expected_false_values: list[Any] = [0, 4, {"c": 4}, [2, 0, {"c": 4}]]
    assert false_values == expected_false_values, (
        f"Expected false values to be {expected_false_values}, got {false_values}"
    )

    subset = {
        "a": 1,
        "b": [2, 3, {"d": 5}, {"c": 4}],
    }
    superset = {
        "a": 1,
        "b": [3, 2, {"c": 4}, {"d": 5}],
    }
    is_nested_subset = nested_structure_is_subset(
        subset, superset, on_dict_mismatch, on_list_mismatch
    )
    assert is_nested_subset, "Expected subset to be subset of superset"


def test_combine_generators() -> None:
    """Test function."""
    gen1 = (x for x in [1, 2, 3])
    gen2 = (x for x in ["a", "b"])
    combined_gen = combine_generators(gen1, gen2)
    assert list(combined_gen) == [1, 2, 3, "a", "b"], (
        "Expected combined generator to yield all items from both generators in order"
    )

    # assert gen1 and gen2 are exhausted after combining and consuming combined_gen
    assert list(gen1) == [], "Expected gen1 to be exhausted after combining"
    assert list(gen2) == [], "Expected gen2 to be exhausted after combining"


def test_generator_length() -> None:
    """Test function."""
    length = 5
    gen = (x for x in range(length))
    assert generator_length(gen) == length, f"Expected generator length to be {length}"

    gen = (x for x in [])
    assert generator_length(gen) == 0, "Expected generator length to be 0"


def test_empty_generator() -> None:
    """Test function."""
    assert list(empty_generator()) == [], "Expected empty generator to yield no items"


def test_generator_has_items() -> None:
    """Test function."""
    iterable_with_items = [1, 2, 3]
    gen = (x for x in iterable_with_items)
    has_items, items = generator_has_items(gen)
    assert has_items is True
    assert list(items) == iterable_with_items, (
        "Expected generator to yield all items from the iterable"
    )


def test_merge_nested_structures() -> None:
    """Test function."""
    subset = {
        "a": 1,
        "b": [2, 3, {"c": 4}],
    }
    superset = {
        "a": 0,
        "b": [2, {"c": 5}],
        "d": 6,
    }
    merged = merge_nested_structures(subset, superset)
    expected_merged = {
        "a": 1,
        "b": [2, 3, {"c": 4}],
        "d": 6,
    }
    assert merged == expected_merged


def test_add_missing_dict_val() -> None:
    """Test function."""
    expected_dict = {"key1": "value1", "key2": {"nested_key": "nested_value"}}
    actual_dict = {"key2": {"nested_key": "old_value"}, "key3": "value3"}
    add_missing_dict_val(expected_dict, actual_dict, "key1")
    add_missing_dict_val(expected_dict, actual_dict, "key2")
    assert actual_dict == {
        "key1": "value1",
        "key2": {"nested_key": "nested_value"},
        "key3": "value3",
    }, "Expected actual dict to be updated with missing values from expected dict"


def test_insert_missing_list_val() -> None:
    """Test function."""
    expected_list = [1, 2, 3]
    actual_list = [1, 3]
    insert_missing_list_val(expected_list, actual_list, 1)
    assert actual_list == [1, 2, 3]

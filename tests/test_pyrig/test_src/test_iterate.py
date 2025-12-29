"""module."""

from typing import Any

from pyrig.src.iterate import nested_structure_is_subset


def test_nested_structure_is_subset() -> None:
    """Test func for nested_structure_is_subset."""
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

    def on_false_dict_action(
        subset_obj: dict[str, Any], _superset_obj: dict[str, Any], key: str
    ) -> None:
        fv = subset_obj[key]
        false_values.append(fv)

    def on_false_list_action(
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
    nested_structure_is_subset(
        subset, superset, on_false_dict_action, on_false_list_action
    )
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
        subset, superset, on_false_dict_action, on_false_list_action
    )
    assert is_nested_subset, "Expected subset to be subset of superset"

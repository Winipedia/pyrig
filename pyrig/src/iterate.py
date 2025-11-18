"""Iterating utilities for handling iterables.

This module provides utility functions for working with iterables,
including getting the length of an iterable with a default value.
These utilities help with iterable operations and manipulations.
"""

from collections.abc import Callable, Iterable
from typing import Any


def nested_structure_is_subset(
    subset: dict[Any, Any] | list[Any] | Any,
    superset: dict[Any, Any] | list[Any] | Any,
    on_false_dict_action: Callable[[dict[Any, Any], dict[Any, Any], Any], Any]
    | None = None,
    on_false_list_action: Callable[[list[Any], list[Any], int], Any] | None = None,
) -> bool:
    """Check if a dictionary is a nested subset of another dictionary.

    Args:
        subset: Dictionary to check
        superset: Dictionary to check against
        on_false_dict_action: Action to take on each false dict comparison
            must return a bool to indicate if after action is still false
        on_false_list_action: Action to take on each false list comparison
            must return a bool to indicate if after action is still false

    Each value of a key must be equal to the value of the same key in the superset.
    If the value is dictionary, the function is called recursively.
    If the value is list, each item must be in the list of the same key in the superset.
    The order in lists does not matter.

    Returns:
        True if subset is a nested subset of superset, False otherwise
    """
    if isinstance(subset, dict) and isinstance(superset, dict):
        iterable: Iterable[tuple[Any, Any]] = subset.items()
        on_false_action: Callable[[Any, Any, Any], Any] | None = on_false_dict_action

        def get_actual(key_or_index: Any) -> Any:
            """Get actual value from superset."""
            return superset.get(key_or_index)

    elif isinstance(subset, list) and isinstance(superset, list):
        iterable = enumerate(subset)
        on_false_action = on_false_list_action

        def get_actual(key_or_index: Any) -> Any:
            """Get actual value from superset."""
            subset_val = subset[key_or_index]
            for superset_val in superset:
                if nested_structure_is_subset(subset_val, superset_val):
                    return superset_val

            return superset[key_or_index] if key_or_index < len(superset) else None
    else:
        return subset == superset

    all_good = True
    for key_or_index, value in iterable:
        actual_value = get_actual(key_or_index)
        if not nested_structure_is_subset(
            value, actual_value, on_false_dict_action, on_false_list_action
        ):
            all_good = False
            if on_false_action is not None:
                on_false_action(subset, superset, key_or_index)
                all_good = nested_structure_is_subset(subset, superset)

    return all_good

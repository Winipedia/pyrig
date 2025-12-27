"""Utilities for deep comparison and validation of nested data structures.

Provides subset checking for nested dictionaries and lists,
with optional auto-correction callbacks.
Used primarily for configuration file validation.
"""

import logging
from collections.abc import Callable, Iterable
from typing import Any

logger = logging.getLogger(__name__)


def nested_structure_is_subset(  # noqa: C901
    subset: dict[Any, Any] | list[Any] | Any,
    superset: dict[Any, Any] | list[Any] | Any,
    on_false_dict_action: Callable[[dict[Any, Any], dict[Any, Any], Any], Any]
    | None = None,
    on_false_list_action: Callable[[list[Any], list[Any], int], Any] | None = None,
) -> bool:
    """Check if nested structure is subset of another.

    Recursively compares nested dicts/lists. Superset may contain additional elements.

    Comparison rules:
        - Dicts: All subset keys must exist in superset with matching values.
        - Lists: All subset items must exist in superset (order-independent).
        - Primitives: Must be exactly equal.

    Optional callbacks enable auto-correction when mismatches detected.

    Args:
        subset: Structure to check.
        superset: Structure to check against.
        on_false_dict_action:
            Callback for dict mismatches (subset_dict, superset_dict, key).
        on_false_list_action:
            Callback for list mismatches (subset_list, superset_list, index).

    Returns:
        True if subset contained in superset.

    Note:
        List comparison is order-independent.
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
                on_false_action(subset, superset, key_or_index)  # ty:ignore[invalid-argument-type]
                all_good = nested_structure_is_subset(subset, superset)

                if not all_good:
                    # make an informational log
                    logger.debug(
                        """
                        -------------------------------------------------------------------------------
                        Subset:
                        %s
                        -------------------
                        is not a subset of
                        -------------------
                        Superset:
                        %s
                        -------------------------------------------------------------------------------
                        """,
                        subset,
                        superset,
                    )

    return all_good

"""Utilities for iterating over data structures."""

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
    """Check if a nested structure is a subset of another nested structure.

    Performs deep comparison of nested dictionaries and lists to verify that
    all keys/values in `subset` exist in `superset`. This enables validation
    that required configuration values are present while allowing additional
    values in the superset.

    The comparison rules are:
        - Dictionaries: All keys in subset must exist in superset with matching
          values (superset may have additional keys).
        - Lists: All items in subset must exist somewhere in superset
          (order does not matter, superset may have additional items).
        - Primitives: Must be exactly equal.

    Args:
        subset: The structure that should be contained within superset.
            Can be a dict, list, or primitive value.
        superset: The structure to check against. Should contain all
            elements from subset (and possibly more).
        on_false_dict_action: Optional callback invoked when a dict comparison
            fails. Receives (subset_dict, superset_dict, failing_key). Can
            modify the structures to fix the mismatch; comparison is retried
            after the action.
        on_false_list_action: Optional callback invoked when a list comparison
            fails. Receives (subset_list, superset_list, failing_index). Can
            modify the structures to fix the mismatch; comparison is retried
            after the action.

    Returns:
        True if all elements in subset exist in superset with matching values,
        False otherwise.

    Note:
        The optional action callbacks enable auto-correction behavior: when a
        mismatch is found, the callback can modify the superset to include the
        missing value, and the comparison is retried. This is used by ConfigFile
        to automatically add missing required settings to config files.
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

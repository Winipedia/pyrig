"""Utilities for deep comparison and validation of nested data structures.

Provides subset checking for nested dictionaries and lists, with optional
auto-correction callbacks that modify the superset in-place when mismatches
are detected. Used primarily by ConfigFile to validate and merge configuration
files.

See Also:
    pyrig.dev.configs.base.base.ConfigFile: Primary consumer of this module.
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
    """Check if a nested structure is a subset of another with optional auto-correction.

    Recursively compares nested dicts and lists. The superset may contain additional
    elements not present in the subset.

    Comparison rules:
        - Dicts: All subset keys must exist in superset with matching values.
        - Lists: All subset items must exist in superset (order-independent).
        - Primitives: Must be exactly equal.

    When callbacks are provided and a mismatch is detected, the appropriate callback
    is invoked. Callbacks should modify the superset in-place to correct the mismatch.
    After each callback invocation, the function re-checks the entire structure; if
    the mismatch is corrected, ``True`` is returned.

    Args:
        subset: The expected structure to check (treated as the "required" values).
        superset: The actual structure to check against (may contain additional values).
        on_false_dict_action: Callback invoked on dict mismatches. Receives
            ``(subset_dict, superset_dict, key)`` where ``key`` is the mismatched key.
            Should modify ``superset_dict`` in-place to add/fix the missing value.
        on_false_list_action: Callback invoked on list mismatches. Receives
            ``(subset_list, superset_list, index)`` where ``index`` is the position
            of the missing item in subset. Should modify ``superset_list`` in-place.

    Returns:
        True if subset is contained in superset (or if callbacks successfully
        corrected all mismatches), False otherwise.

    Example:
        Basic subset check::

            >>> nested_structure_is_subset({"a": 1}, {"a": 1, "b": 2})
            True
            >>> nested_structure_is_subset({"a": 1}, {"a": 2})
            False

        With auto-correction callback (as used by ConfigFile)::

            >>> actual = {"a": 1}
            >>> expected = {"a": 1, "b": 2}
            >>> def add_missing(exp, act, key):
            ...     act[key] = exp[key]
            >>> nested_structure_is_subset(expected, actual, add_missing)
            True
            >>> actual
            {'a': 1, 'b': 2}
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
            """Find matching element in superset list (order-independent).

            Searches superset for an element that contains subset_val as a subset.
            Falls back to index-based lookup if no match found, or None if out of
            bounds.
            """
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

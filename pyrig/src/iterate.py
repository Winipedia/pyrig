"""Utilities for deep comparison and validation of nested data structures.

This module provides utilities for comparing nested dictionaries and lists,
primarily used for configuration file validation. The core function enables
checking whether one nested structure is a subset of another, with optional
auto-correction callbacks.

The primary use case is validating that configuration files contain all required
settings while allowing users to add extra configuration. This powers pyrig's
ConfigFile system, which automatically adds missing configuration values to
existing files.

Example:
    >>> from pyrig.src.iterate import nested_structure_is_subset
    >>> required = {"database": {"host": "localhost", "port": 5432}}
    >>> actual = {"database": {"host": "localhost", "port": 5432, "ssl": True}}
    >>> nested_structure_is_subset(required, actual)
    True

See Also:
    pyrig.dev.configs.base.base.ConfigFile: Uses this for config validation
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
    """Check if a nested structure is a subset of another nested structure.

    Performs deep recursive comparison of nested dictionaries and lists to verify
    that all keys/values in `subset` exist in `superset`. This enables validation
    that required configuration values are present while allowing additional
    values in the superset.

    The comparison is performed recursively with the following rules:
        - **Dictionaries**: All keys in subset must exist in superset with
          matching values. Superset may have additional keys that are ignored.
        - **Lists**: All items in subset must exist somewhere in superset.
          Order does not matter, and superset may have additional items.
        - **Primitives**: Must be exactly equal (using `==` comparison).

    Optional action callbacks enable auto-correction: when a mismatch is detected,
    the callback can modify the superset to add the missing value, and the
    comparison is automatically retried. This powers pyrig's ConfigFile system,
    which automatically adds missing required settings to configuration files.

    Args:
        subset: The structure that should be contained within superset. Can be
            a dict, list, or primitive value (str, int, bool, etc.).
        superset: The structure to check against. Should contain all elements
            from subset (and possibly more).
        on_false_dict_action: Optional callback invoked when a dictionary key
            comparison fails. Receives `(subset_dict, superset_dict, failing_key)`.
            Can modify `superset_dict` to add the missing key/value; the
            comparison is retried after the callback returns.
        on_false_list_action: Optional callback invoked when a list item
            comparison fails. Receives `(subset_list, superset_list, failing_index)`.
            Can modify `superset_list` to add the missing item; the comparison
            is retried after the callback returns.

    Returns:
        True if all elements in subset exist in superset with matching values,
        False otherwise. When action callbacks are provided and successfully
        fix mismatches, returns True after the fixes are applied.

    Example:
        Basic subset checking::

            >>> subset = {"a": 1, "b": [2, 3]}
            >>> superset = {"a": 1, "b": [2, 3, 4], "c": 5}
            >>> nested_structure_is_subset(subset, superset)
            True

        With auto-correction callback::

            >>> def add_missing(subset_dict, superset_dict, key):
            ...     superset_dict[key] = subset_dict[key]
            >>> subset = {"required": "value"}
            >>> superset = {}
            >>> nested_structure_is_subset(subset, superset, add_missing)
            True
            >>> superset
            {'required': 'value'}

    Note:
        - The function is recursive and handles arbitrarily nested structures.
        - When callbacks are provided, they can modify the superset in-place.
        - If a callback fails to fix the mismatch, a debug log is generated
          showing the subset and superset for troubleshooting.
        - List comparison is order-independent: `[1, 2]` is a subset of `[2, 1]`.

    See Also:
        pyrig.dev.configs.base.base.ConfigFile.add_missing_configs: Uses this
            with callbacks to auto-add missing configuration values
        pyrig.dev.configs.base.base.ConfigFile.is_correct_recursively: Uses this
            for validation without callbacks
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

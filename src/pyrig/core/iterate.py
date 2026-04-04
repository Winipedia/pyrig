"""Utilities for deep comparison and validation of nested data structures.

Provides subset checking for nested dictionaries and lists, with optional
auto-correction callbacks that modify the superset in-place when mismatches
are detected. Used primarily by `ConfigFile` to validate and merge configuration
files.

See Also:
    pyrig.rig.configs.base.base.ConfigFile: Primary consumer of this module.
"""

import logging
from collections.abc import Callable, Generator, Iterable
from typing import Any

logger = logging.getLogger(__name__)


def empty_generator() -> Generator[Any, None, None]:
    """Return an empty generator."""
    if False:
        yield


def generator(iterable: Iterable[Any]) -> Generator[Any, None, None]:
    """Convert an iterable to a generator."""
    yield from iterable


def generator_has_items[T](
    gen: Generator[T, Any, Any],
) -> tuple[bool, Generator[T, Any, Any]]:
    """Check if a generator has any items without consuming them.

    Returns a tuple of (has_items, generator). The returned generator will yield
    all the original items including the first one that was checked.

    Example:
        >>> gen = (x for x in [1, 2, 3])
        >>> has_items, gen = generator_has_items(gen)
        >>> has_items
        True
        >>> list(gen)
        [1, 2, 3]

        >>> empty_gen = (x for x in [])
        >>> has_items, empty_gen = generator_has_items(empty_gen)
        >>> has_items
        False
        >>> list(empty_gen)
        []
    """
    sentinel = object()
    first = next(gen, sentinel)
    if first is sentinel:
        return False, empty_generator()
    return True, combine_generators(generator((first,)), gen)


def combine_generators(*generators: Iterable[Any]) -> Generator[Any, None, None]:
    """Combine multiple generators into a single generator.

    Args:
        *generators: Any number of generators to combine.

    Yields:
        Items from all generators in the order they were provided.
    """
    for generator in generators:
        yield from generator


def generator_length(generator: Generator[Any, None, None]) -> int:
    """Calculate the length of a generator without consuming it.

    Warning:
    This function will consume the generator, so it should only be used when
    the generator is not needed afterward or when it can be recreated. If you need
    to both calculate the length and use the items, consider converting the generator
    to a Sequence first.

    Args:
        generator: The generator to measure.

    Returns:
        The number of items in the generator.
    """
    return sum(1 for _ in generator)


def nested_structure_is_subset(  # noqa: C901
    subset: dict[Any, Any] | list[Any] | Any,
    superset: dict[Any, Any] | list[Any] | Any,
    on_dict_mismatch: Callable[[dict[Any, Any], dict[Any, Any], Any], Any]
    | None = None,
    on_list_mismatch: Callable[[list[Any], list[Any], int], Any] | None = None,
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
    the mismatch is corrected, `True` is returned.

    Args:
        subset: The expected structure to check (treated as the "required" values).
        superset: The actual structure to check against (may contain additional values).
        on_dict_mismatch: Callback invoked on dict mismatches. Receives
            `(subset, superset, key)` where the first two arguments are the full
            dict structures being compared and `key` is the mismatched key.
            Should modify `superset` in-place to add/fix the missing value.
        on_list_mismatch: Callback invoked on list mismatches. Receives
            `(subset, superset, index)` where the first two arguments are the full
            list structures being compared and `index` is the position of the missing
            item in subset. Should modify `superset` in-place.

    Returns:
        True if subset is contained in superset (or if callbacks successfully
        corrected all mismatches), False otherwise.

    Example:
        Basic subset check::

            >>> nested_structure_is_subset({"a": 1}, {"a": 1, "b": 2})
            True
            >>> nested_structure_is_subset({"a": 1}, {"a": 2})
            False

        With auto-correction callback (as used by `ConfigFile`)::

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
        on_false_action: Callable[[Any, Any, Any], Any] | None = on_dict_mismatch

        def get_actual(key_or_index: Any) -> Any:
            """Get actual value from superset."""
            return superset.get(key_or_index)

    elif isinstance(subset, list) and isinstance(superset, list):
        iterable = enumerate(subset)
        on_false_action = on_list_mismatch

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
            value, actual_value, on_dict_mismatch, on_list_mismatch
        ):
            all_good = False
            if on_false_action is not None:
                on_false_action(subset, superset, key_or_index)  # ty: ignore[invalid-argument-type]
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

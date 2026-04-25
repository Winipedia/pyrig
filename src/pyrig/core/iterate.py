"""Utilities for working with generators and nested data structures.

Provides helpers for safely inspecting and combining generators, as well as
recursive subset comparison and in-place merging of nested dicts and lists.
"""

import logging
from collections.abc import Callable, Generator, Iterable
from typing import Any

logger = logging.getLogger(__name__)


def generator_has_items[T](
    gen: Generator[T, Any, Any],
) -> tuple[bool, Generator[T, Any, Any]]:
    """Peek at a generator to check whether it yields any items.

    Advances the generator by one item to determine if it is non-empty, then
    reconstructs a new generator that prepends the consumed item so no data
    is lost.

    Args:
        gen: The generator to inspect.

    Returns:
        A two-element tuple ``(has_items, gen)`` where ``has_items`` is
        ``True`` if the generator yielded at least one item, and ``gen`` is
        a new generator that will yield all original items including the first.

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
    return True, combine_generators(((first,)), gen)


def combine_generators(*generators: Iterable[Any]) -> Generator[Any, None, None]:
    """Chain multiple iterables into a single generator.

    Args:
        *generators: Iterables to chain together.

    Yields:
        Items from each iterable in the order provided.
    """
    for generator in generators:
        yield from generator


def empty_generator() -> Generator[Any, None, None]:
    """Return a generator that yields no items."""
    if False:
        yield


def generator_length(generator: Generator[Any, None, None]) -> int:
    """Count the number of items in a generator by consuming it.

    Warning:
        This function exhausts the generator. Only use it when the generator
        will not be needed afterward, or when it can be recreated cheaply.
        If you need both the count and the items, convert to a list first.

    Args:
        generator: The generator to measure.

    Returns:
        The number of items yielded by the generator.
    """
    return sum(1 for _ in generator)


def merge_nested_structures[T: dict[Any, Any] | list[Any]](
    subset: T,
    superset: T,
) -> T:
    """Merge all values from subset into superset, filling in any gaps.

    Walks both structures recursively. For every key or index present in
    ``subset`` that is missing or has a different value in ``superset``,
    the superset is updated in-place. Keys or elements present only in
    the superset are left untouched.

    Args:
        subset: The structure whose values are treated as required.
        superset: The structure to update. Modified in-place.

    Returns:
        The updated ``superset``.
    """
    nested_structure_is_subset(
        subset=subset,
        superset=superset,
        on_dict_mismatch=add_missing_dict_val,
        on_list_mismatch=insert_missing_list_val,
    )
    return superset


def nested_structure_is_subset(  # noqa: C901
    subset: dict[Any, Any] | list[Any] | Any,
    superset: dict[Any, Any] | list[Any] | Any,
    on_dict_mismatch: Callable[[dict[Any, Any], dict[Any, Any], Any], Any]
    | None = None,
    on_list_mismatch: Callable[[list[Any], list[Any], int], Any] | None = None,
) -> bool:
    """Recursively check whether one nested structure is contained within another.

    Compares dicts, lists, and primitives according to subset semantics:

    - **Dicts**: every key in ``subset`` must exist in ``superset`` with a
      matching value. Extra keys in ``superset`` are ignored.
    - **Lists**: every item in ``subset`` must appear somewhere in ``superset``
      (order-independent). Matching is done recursively using this same function.
    - **Primitives**: values must be exactly equal (``==``).

    When a mismatch is found and a callback is provided, the callback is called
    with the two structures being compared and the offending key or index. The
    callback is expected to fix the superset in-place. After each correction the
    entire structure is re-checked; if the correction resolves the mismatch,
    ``True`` is returned.

    Args:
        subset: The expected (required) structure.
        superset: The actual structure to check. May contain additional
            elements not present in ``subset``.
        on_dict_mismatch: Optional callback invoked when a dict key is
            missing or has the wrong value. Receives
            ``(subset_dict, superset_dict, key)`` and should update
            ``superset_dict`` in-place.
        on_list_mismatch: Optional callback invoked when a list item is
            missing. Receives ``(subset_list, superset_list, index)`` and
            should insert the missing item into ``superset_list`` in-place.

    Returns:
        ``True`` if ``subset`` is fully contained within ``superset`` (or if
        callbacks corrected all mismatches). ``False`` if any mismatch remains
        after callbacks run (or no callbacks were provided).

    Example:
        Basic subset check::

            >>> nested_structure_is_subset({"a": 1}, {"a": 1, "b": 2})
            True
            >>> nested_structure_is_subset({"a": 1}, {"a": 2})
            False

        With auto-correction via callback::

            >>> actual = {"a": 1}
            >>> template = {"a": 1, "b": 2}
            >>> def add_missing(tmpl, act, key):
            ...     act[key] = tmpl[key]
            >>> nested_structure_is_subset(template, actual, add_missing)
            True
            >>> actual
            {'a': 1, 'b': 2}
    """
    if isinstance(subset, dict) and isinstance(superset, dict):
        iterable: Iterable[tuple[Any, Any]] = subset.items()
        on_false_action: Callable[[Any, Any, Any], Any] | None = on_dict_mismatch

        def get_actual(key_or_index: Any) -> Any:
            """Return the value for ``key_or_index`` from the superset dict."""
            return superset.get(key_or_index)

    elif isinstance(subset, list) and isinstance(superset, list):
        iterable = enumerate(subset)
        on_false_action = on_list_mismatch

        def get_actual(key_or_index: Any) -> Any:
            """Find the matching element in the superset list (order-independent).

            Scans superset for an element that contains ``subset[key_or_index]``
            as a subset. Falls back to index-based lookup if no match is found,
            or ``None`` if the index is out of bounds.
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


def add_missing_dict_val(
    expected_dict: dict[Any, Any], actual_dict: dict[Any, Any], key: Any
) -> None:
    """Add or overwrite a key in ``actual_dict`` with the value from ``expected_dict``.

    Used as the ``on_dict_mismatch`` callback in :func:`merge_nested_structures`.
    The merge strategy depends on the value types:

    - **Both values are dicts**: ``actual_dict[key]`` is updated in-place with
      all entries from ``expected_dict[key]``. Overlapping keys take the expected
      value; keys present only in ``actual_dict[key]`` are kept.
    - **Any other type**: ``actual_dict[key]`` is replaced entirely by
      ``expected_dict[key]``.

    Args:
        expected_dict: Dict containing the value to apply.
        actual_dict: Dict to update in-place.
        key: Key to add or overwrite.
    """
    expected_val: Any = expected_dict[key]
    actual_val = actual_dict.get(key)
    actual_dict.setdefault(key, expected_val)

    if isinstance(expected_val, dict) and isinstance(actual_val, dict):
        actual_val.update(expected_val)
    else:
        actual_dict[key] = expected_val


def insert_missing_list_val(
    expected_list: list[Any], actual_list: list[Any], index: int
) -> None:
    """Insert a missing item from ``expected_list`` into ``actual_list`` at ``index``.

    Used as the ``on_list_mismatch`` callback in :func:`merge_nested_structures`.

    Args:
        expected_list: List containing the item to insert.
        actual_list: List to modify in-place.
        index: Position at which to insert the item.
    """
    actual_list.insert(index, expected_list[index])

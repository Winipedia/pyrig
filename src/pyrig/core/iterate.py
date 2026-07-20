"""Utilities for iterables and nested data structures."""

from collections.abc import Iterator
from itertools import chain
from typing import Any, cast, overload

from pyrig_runtime.core.constants import MISSING


def iterator_has_items[T](
    iterable: Iterator[T],
) -> tuple[bool, Iterator[T]]:
    """Peek at an iterator to check whether it yields any items.

    The original iterator is consumed and must not be used again; iterate the
    returned iterator instead, which yields the full original sequence with no
    items lost.

    Args:
        iterable: The iterator to inspect. Consumed by this call.

    Returns:
        A `(has_items, iterator)` tuple where `has_items` is `True` if the
        input yielded at least one item, and `iterator` yields all of the
        original items including the first.

    Examples:
        >>> gen = (x for x in [1, 2, 3])
        >>> has_items, gen = iterator_has_items(gen)
        >>> has_items
        True
        >>> list(gen)
        [1, 2, 3]

        >>> empty_gen = (x for x in [])
        >>> has_items, empty_gen = iterator_has_items(empty_gen)
        >>> has_items
        False
        >>> list(empty_gen)
        []
    """
    first = next(iterable, MISSING)
    if first is MISSING:
        return False, iter(())
    first = cast("T", first)
    return True, chain((first,), iterable)


@overload
def merge_nested_structures(
    subset: dict[Any, Any],
    superset: dict[Any, Any],
) -> dict[Any, Any]: ...
@overload
def merge_nested_structures(subset: list[Any], superset: list[Any]) -> list[Any]: ...
@overload
def merge_nested_structures[T](subset: T, superset: T) -> T: ...
def merge_nested_structures(subset: Any, superset: Any) -> Any:
    """Merge all values from `subset` into `superset`, filling in any gaps.

    Applies deeply to nested dicts and lists: for every key or item present in
    `subset` that is missing from, or different in, `superset`, the superset is
    updated. Nested dicts and lists are merged recursively; keys and items
    present only in `superset` are left untouched. Anything that is not a pair
    of dicts or a pair of lists is returned unchanged.

    Note:
        Lists are matched order-independently, but multiplicity is respected:
        an item that occurs N times in `subset` requires N distinct matches in
        `superset` (see `match_list_items`). An item without a match is merged
        into the item at the same index when both are dicts or both are
        lists, and otherwise inserted at that index.

    Args:
        subset: The structure whose values are treated as required.
        superset: The structure to update. Modified in-place.

    Returns:
        The updated `superset`.

    Examples:
        >>> merge_nested_structures({"a": 1, "b": 2}, {"a": 1})
        {'a': 1, 'b': 2}
        >>> merge_nested_structures([2, 3], [2])
        [2, 3]
        >>> merge_nested_structures(["", "", "---"], [""])
        ['', '', '---']
    """
    if both_dicts(subset, superset):
        for index, (key, sub_val) in enumerate(subset.items()):
            sup_val = superset.get(key, MISSING)
            if both_dicts_or_lists(sub_val, sup_val):
                merge_nested_structures(sub_val, sup_val)
            elif not nested_structure_is_subset(sub_val, sup_val):
                dict_insert_key(superset, index=index, key=key, value=sub_val)

    elif both_lists(subset, superset):
        matched = match_list_items(subset, superset)
        for index, sub_val in enumerate(subset):
            if matched[index]:
                continue
            sup_val = superset[index] if index < len(superset) else MISSING
            if both_dicts_or_lists(sub_val, sup_val):
                merge_nested_structures(sub_val, sup_val)
            else:
                superset.insert(index, sub_val)

    return superset


def dict_insert_key[K, V](
    dict_: dict[K, V],
    *,
    index: int,
    key: K,
    value: V,
) -> None:
    """Insert a key/value pair into a dict at a specific index.

    This handles inserting at the beginning and at the end if
    the given index is out of bounds. The dict is modified in-place.

    Args:
        dict_: The dict to modify.
        index: The index at which to insert the new key/value pair.
        key: The key to insert.
        value: The value to insert.

    Examples:
        >>> d = {"a": 1, "b": 2}
        >>> dict_insert_key(d, index=1, key="c", value=3)
        >>> d
        {'a': 1, 'c': 3, 'b': 2}
    """
    dict_.pop(key, None)
    items = list(dict_.items())
    items.insert(index, (key, value))
    dict_.clear()
    dict_.update(items)


@overload
def nested_structure_is_subset(
    subset: dict[Any, Any],
    superset: dict[Any, Any],
) -> bool: ...
@overload
def nested_structure_is_subset(subset: list[Any], superset: list[Any]) -> bool: ...
@overload
def nested_structure_is_subset[T](subset: T, superset: T) -> bool: ...
def nested_structure_is_subset(subset: Any, superset: Any) -> bool:
    """Check whether one nested structure is contained within another.

    Compares dicts, lists, and primitives using subset semantics:

    - Dicts: every key in `subset` must exist in `superset` with a value that
      is itself a subset. Extra keys in `superset` are ignored.
    - Lists: every item in `subset` must match a distinct item in `superset`
      (order-independent, see `match_list_items`), so an item occurring N
      times in `subset` requires N matching items in `superset`. Extra items
      are ignored.
    - Everything else: values must be equal (`==`).

    Args:
        subset: The expected (required) structure.
        superset: The actual structure to check. May contain additional
            elements not present in `subset`.

    Returns:
        `True` if `subset` is fully contained within `superset`.

    Examples:
        >>> nested_structure_is_subset({"a": 1}, {"a": 1, "b": 2})
        True
        >>> nested_structure_is_subset({"a": 1}, {"a": 2})
        False
        >>> nested_structure_is_subset([2, 3], [1, 2, 3])
        True
        >>> nested_structure_is_subset({"a": None}, {})
        False
        >>> nested_structure_is_subset(["", ""], [""])
        False
    """
    if both_dicts(subset, superset):
        return all(
            key in superset and nested_structure_is_subset(value, superset[key])
            for key, value in subset.items()
        )
    if both_lists(subset, superset):
        return all(match_list_items(subset, superset))
    return subset == superset


def match_list_items(subset: list[Any], superset: list[Any]) -> list[bool]:
    """Check whether each `subset` item is satisfied by a distinct `superset` item.

    Each `superset` item can satisfy at most one `subset` item, so a value
    that occurs multiple times in `subset` requires that many distinct
    matches in `superset` rather than being satisfied by a single occurrence.

    Args:
        subset: Items to find matches for.
        superset: Items to match against. Not modified.

    Returns:
        One entry per item in `subset`, in order: `True` if a distinct,
        not-yet-matched `superset` item satisfies it, `False` otherwise.

    Examples:
        >>> match_list_items(["", ""], [""])
        [True, False]
        >>> match_list_items(["", "a", ""], ["", "z"])
        [True, False, False]
    """
    pool = list(superset)
    matched: list[bool] = []
    for sub_val in subset:
        for index, other in enumerate(pool):
            if nested_structure_is_subset(sub_val, other):
                del pool[index]
                matched.append(True)
                break
        else:
            matched.append(False)
    return matched


def both_dicts_or_lists(a: object, b: object) -> bool:
    """Return whether `a` and `b` are both dicts or both lists.

    Such a pair is merged recursively by `merge_nested_structures` rather than
    overwritten.

    Args:
        a: First value.
        b: Second value.

    Returns:
        `True` if both values are dicts or both are lists.
    """
    return both_dicts(a, b) or both_lists(a, b)


@overload
def deep_sorted_dict[T](value: list[T]) -> list[T]: ...
@overload
def deep_sorted_dict[K, V](value: dict[K, V]) -> dict[K, V]: ...
@overload
def deep_sorted_dict[T](value: T) -> T: ...
def deep_sorted_dict(value: Any) -> Any:
    """Recursively sort a nested dict by keys."""
    if isinstance(value, dict):
        return {key: deep_sorted_dict(item) for key, item in sorted(value.items())}

    if isinstance(value, list):
        return [deep_sorted_dict(item) for item in value]

    return value


def both_dicts(a: object, b: object) -> bool:
    """Return whether `a` and `b` are both dicts.

    Such a pair is merged recursively by `merge_nested_structures` rather than
    overwritten.

    Args:
        a: First value.
        b: Second value.

    Returns:
        `True` if both values are dicts.
    """
    return isinstance(a, dict) and isinstance(b, dict)


def both_lists(a: object, b: object) -> bool:
    """Return whether `a` and `b` are both lists.

    Such a pair is merged recursively by `merge_nested_structures` rather than
    overwritten.

    Args:
        a: First value.
        b: Second value.

    Returns:
        `True` if both values are lists.
    """
    return isinstance(a, list) and isinstance(b, list)

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
def merge_structures(
    subset: dict[Any, Any],
    superset: dict[Any, Any],
) -> dict[Any, Any]: ...
@overload
def merge_structures(subset: list[Any], superset: list[Any]) -> list[Any]: ...
@overload
def merge_structures[T](subset: T, superset: T) -> T: ...
def merge_structures(subset: Any, superset: Any) -> Any:
    """Merge all values from `superset` into `subset`, filling in any gaps.

    Applies deeply to nested dicts and lists: for every key or item present in
    `superset` that is missing from `subset`, `subset` is extended with it, at
    the position it occupies in `superset`. Nested dicts and lists are merged
    recursively. A value already present in `subset` always wins: `superset`
    can only add what is missing, never override what is already there.
    Anything that is not a pair of dicts or a pair of lists is returned
    unchanged.

    Args:
        subset: The structure whose values take priority. Modified in-place.
        superset: The structure to pull missing values from.

    Returns:
        The updated `subset`.

    Examples:
        >>> merge_structures({"a": 1}, {"a": 0, "b": 2})
        {'a': 1, 'b': 2}
        >>> merge_structures([2], [2, 3])
        [2, 3]
        >>> merge_structures([""], ["", "", "---"])
        ['', '', '---']

    Note:
        Lists are matched order-independently, but multiplicity is respected:
        an item that occurs N times in `superset` requires N distinct matches
        in `subset` (see `match_list_items`). An item without a match is
        merged into the item at the same index when both are dicts or both
        are lists, and otherwise inserted at that index.
    """
    if both_dicts(subset, superset):
        for index, (key, sup_val) in enumerate(superset.items()):
            sub_val = subset.get(key, MISSING)
            if both_dicts_or_lists(sub_val, sup_val):
                merge_structures(sub_val, sup_val)
            elif sub_val is MISSING:
                dict_insert(subset, index=index, key=key, value=sup_val)

    elif both_lists(subset, superset):
        matched = match_list_items(superset, subset)
        for index, sup_val in enumerate(superset):
            if matched[index]:
                continue
            sub_val = subset[index] if index < len(subset) else MISSING
            if both_dicts_or_lists(sub_val, sup_val):
                merge_structures(sub_val, sup_val)
            else:
                subset.insert(index, sup_val)

    return subset


def dict_insert[K, V](
    dict_: dict[K, V],
    *,
    index: int,
    key: K,
    value: V,
) -> None:
    """Insert a key/value pair into a dict at a specific index.

    If `key` already exists in `dict_`, its current entry is removed first,
    so the key moves to the new position with the new value instead of
    appearing twice. An out-of-bounds index inserts at the beginning or end.
    The dict is modified in-place.

    Args:
        dict_: The dict to modify.
        index: The index at which to insert the new key/value pair.
        key: The key to insert.
        value: The value to insert.

    Examples:
        >>> d = {"a": 1, "b": 2}
        >>> dict_insert(d, index=1, key="c", value=3)
        >>> d
        {'a': 1, 'c': 3, 'b': 2}
    """
    dict_.pop(key, None)
    items = list(dict_.items())
    items.insert(index, (key, value))
    dict_.clear()
    dict_.update(items)


@overload
def structure_is_subset(
    subset: dict[Any, Any],
    superset: dict[Any, Any],
) -> bool: ...
@overload
def structure_is_subset(subset: list[Any], superset: list[Any]) -> bool: ...
@overload
def structure_is_subset[T](subset: T, superset: T) -> bool: ...
def structure_is_subset(subset: Any, superset: Any) -> bool:
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
        >>> structure_is_subset({"a": 1}, {"a": 1, "b": 2})
        True
        >>> structure_is_subset({"a": 1}, {"a": 2})
        False
        >>> structure_is_subset([2, 3], [1, 2, 3])
        True
        >>> structure_is_subset({"a": None}, {})
        False
        >>> structure_is_subset(["", ""], [""])
        False
    """
    if both_dicts(subset, superset):
        return all(
            key in superset and structure_is_subset(value, superset[key])
            for key, value in subset.items()
        )
    if both_lists(subset, superset):
        return all(match_list_items(subset, superset))
    return subset == superset


def match_list_items(subset: list[Any], superset: list[Any]) -> list[bool]:
    """Check whether each `subset` item is satisfied by a distinct `superset` item.

    An item satisfies another using the same nested subset semantics as
    `structure_is_subset`, not plain equality. Each `superset` item
    can satisfy at most one `subset` item, so a value that occurs multiple
    times in `subset` requires that many distinct matches in `superset`
    rather than being satisfied by a single occurrence.

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
            if structure_is_subset(sub_val, other):
                del pool[index]
                matched.append(True)
                break
        else:
            matched.append(False)
    return matched


def both_dicts_or_lists(a: object, b: object) -> bool:
    """Return whether `a` and `b` are both dicts or both lists."""
    return both_dicts(a, b) or both_lists(a, b)


@overload
def deep_sorted_dict[T](value: list[T]) -> list[T]: ...
@overload
def deep_sorted_dict[K, V](value: dict[K, V]) -> dict[K, V]: ...
@overload
def deep_sorted_dict[T](value: T) -> T: ...
def deep_sorted_dict(value: Any) -> Any:
    """Recursively sort every nested dict by key.

    Lists are recursed into item by item without reordering them, and any
    value that is neither a dict nor a list is returned unchanged.

    Args:
        value: The dict, list, or other value to sort.

    Returns:
        A new copy of `value` with every dict layer sorted by key; `value`
        itself is not modified.
    """
    if isinstance(value, dict):
        return {key: deep_sorted_dict(item) for key, item in sorted(value.items())}

    if isinstance(value, list):
        return [deep_sorted_dict(item) for item in value]

    return value


def both_dicts(a: object, b: object) -> bool:
    """Return whether `a` and `b` are both dicts."""
    return isinstance(a, dict) and isinstance(b, dict)


def both_lists(a: object, b: object) -> bool:
    """Return whether `a` and `b` are both lists."""
    return isinstance(a, list) and isinstance(b, list)


def traverse_structure(structure: object) -> Iterator[Any]:
    """Yield leaf values from nested dictionaries and lists.

    Args:
        structure: The nested dict/list structure to walk.

    Yields:
        All values that are not themselves dictionaries or lists, in traversal order.
    """
    if isinstance(structure, dict):
        for value in structure.values():
            yield from traverse_structure(value)
    elif isinstance(structure, list):
        for item in structure:
            yield from traverse_structure(item)
    else:
        yield structure

"""Utilities for selecting definitions from Python syntax trees."""

import ast
from collections.abc import Iterator

FUNC_DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
type FuncDefs = ast.FunctionDef | ast.AsyncFunctionDef


def cls_definitions(tree: ast.Module) -> Iterator[ast.ClassDef]:
    """Yield class definitions declared directly in a module.

    Args:
        tree: Module syntax tree to inspect.

    Yields:
        Class definitions in source order.
    """
    return (c for c in tree.body if isinstance(c, ast.ClassDef))


def func_definitions(tree: ast.Module) -> Iterator[FuncDefs]:
    """Yield function definitions declared directly in a module.

    Args:
        tree: Module syntax tree to inspect.

    Yields:
        Synchronous and asynchronous function definitions in source order.
    """
    return (func for func in tree.body if isinstance(func, FUNC_DEFINITIONS))


def method_definitions(cls: ast.ClassDef) -> Iterator[FuncDefs]:
    """Yield method definitions declared directly in a class.

    Args:
        cls: Class syntax tree to inspect.

    Yields:
        Synchronous and asynchronous method definitions in source order.
    """
    return (func for func in cls.body if isinstance(func, FUNC_DEFINITIONS))

"""Test module."""

import ast

from pyrig.core.introspection.ast import (
    cls_definitions,
    func_definitions,
    method_definitions,
)


def test_cls_definitions() -> None:
    """Test function."""
    tree = ast.parse("""
class First:
    class Nested:
        pass

def func():
    class Local:
        pass

class Second:
    pass
""")
    assert [cls.name for cls in cls_definitions(tree)] == ["First", "Second"]
    assert list(cls_definitions(ast.parse(""))) == []


def test_func_definitions() -> None:
    """Test function."""
    tree = ast.parse("""
value = 1

def first():
    def nested():
        pass

class Example:
    def method(self):
        pass

async def second():
    pass
""")
    funcs = list(func_definitions(tree))
    assert [func.name for func in funcs] == ["first", "second"]
    assert isinstance(funcs[0], ast.FunctionDef)
    assert isinstance(funcs[1], ast.AsyncFunctionDef)
    assert list(func_definitions(ast.parse(""))) == []


def test_method_definitions() -> None:
    """Test function."""
    tree = ast.parse("""
class Example:
    value = 1

    def first(self):
        def nested():
            pass

    class Nested:
        def nested_method(self):
            pass

    async def second(self):
        pass

class Empty:
    pass
""")
    example, empty = cls_definitions(tree)
    methods = list(method_definitions(example))
    assert [method.name for method in methods] == ["first", "second"]
    assert isinstance(methods[0], ast.FunctionDef)
    assert isinstance(methods[1], ast.AsyncFunctionDef)
    assert list(method_definitions(empty)) == []

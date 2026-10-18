"""Test module."""

import ast

from pyrig.core.introspection.ast import class_defs, func_defs, method_defs


def test_func_defs() -> None:
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
    funcs = list(func_defs(tree))
    assert [func.name for func in funcs] == ["first", "second"]
    assert isinstance(funcs[0], ast.FunctionDef)
    assert isinstance(funcs[1], ast.AsyncFunctionDef)
    assert list(func_defs(ast.parse(""))) == []


def test_class_defs() -> None:
    """Test function."""
    tree = ast.parse("""
class First:
    class Nested:
        pass

def function():
    class Local:
        pass

class Second:
    pass
""")
    assert [cls.name for cls in class_defs(tree)] == ["First", "Second"]
    assert list(class_defs(ast.parse(""))) == []


def test_method_defs() -> None:
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
    example, empty = class_defs(tree)
    methods = list(method_defs(example))
    assert [method.name for method in methods] == ["first", "second"]
    assert isinstance(methods[0], ast.FunctionDef)
    assert isinstance(methods[1], ast.AsyncFunctionDef)
    assert list(method_defs(empty)) == []

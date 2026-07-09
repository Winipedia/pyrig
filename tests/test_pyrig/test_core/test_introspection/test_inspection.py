"""module for the following module path (maybe truncated).

tests.test_pyrig.test_modules.test_inspection
"""

from pyrig.core.introspection.inspection import def_line, def_line_sorted


def test_def_line() -> None:
    """Test function."""

    # Test with a function defined in this module
    def test_function() -> None:
        """Test function."""

    line_num = def_line(test_function)
    assert line_num > 0, f"Expected positive integer line number, got {line_num}"

    # Test with a class method
    class TestClass:
        def test_method(self) -> None:
            """Test method."""

        @property
        def test_property(self) -> str:
            """Test property."""
            return "test"

    method_line = def_line(TestClass.test_method)
    assert method_line > 0

    # Test with a property
    prop_line = def_line(TestClass.test_property)
    assert prop_line > 0


def test_def_line_sorted() -> None:
    """Test function."""

    def test_func_a() -> None:
        pass

    def test_func_b() -> None:
        pass

    def test_func_c() -> None:
        pass

    funcs = [
        test_func_b,
        test_func_c,
        test_func_a,
        test_def_line_sorted,
    ]
    sorted_funcs = def_line_sorted(funcs)
    assert sorted_funcs == [
        test_def_line_sorted,
        test_func_a,
        test_func_b,
        test_func_c,
    ], "Expected functions sorted by definition line"

"""Tests for pyrig.src.testing.create_tests module."""

import inspect
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pytest_mock import MockFixture

from pyrig.dev.cli.commands import create_tests as create_tests_module
from pyrig.dev.cli.commands.create_tests import (
    create_test_module,
    create_test_package,
    create_tests_for_package,
    get_test_classes_content,
    get_test_functions_content,
    get_test_module_content,
    make_test_skeletons,
)
from pyrig.src.modules.module import (
    create_module,
    import_module_with_file_fallback,
    make_obj_importpath,
)
from pyrig.src.modules.package import create_package
from pyrig.src.testing.assertions import assert_with_msg


def test_make_test_skeletons(mocker: MockFixture) -> None:
    """Test func for create_tests."""
    # Mock the two main functions that create_tests calls to verify orchestration

    mock_create_tests_for_src_package = mocker.patch(
        make_obj_importpath(create_tests_module) + ".create_tests_for_package"
    )

    # Call the function
    make_test_skeletons()

    src_count = mock_create_tests_for_src_package.call_count

    assert_with_msg(
        src_count == 1,
        f"Expected create_tests_for_src_package called once, got {src_count}",
    )


def test_create_tests_for_package(mocker: MockFixture) -> None:
    """Test func for create_tests_for_src_package."""
    # Mock the dependencies
    mock_walk_package = mocker.patch(
        make_obj_importpath(create_tests_module) + ".walk_package"
    )
    mock_create_test_package = mocker.patch(
        make_obj_importpath(create_tests_module) + ".create_test_package"
    )
    mock_create_test_module = mocker.patch(
        make_obj_importpath(create_tests_module) + ".create_test_module"
    )

    # Create mock package and modules
    mock_package = mocker.MagicMock(spec=ModuleType)
    mock_module1 = mocker.MagicMock(spec=ModuleType)
    mock_module2 = mocker.MagicMock(spec=ModuleType)

    # Set up mock return values
    mock_walk_package.return_value = [(mock_package, [mock_module1, mock_module2])]

    # Call the function
    create_tests_for_package(package=mock_package)

    # Verify walk_package was called with the source package
    mock_walk_package.assert_called_once_with(mock_package)

    # Verify create_test_package was called for the package
    mock_create_test_package.assert_called_once_with(mock_package)

    # Verify create_test_module was called for each module
    expected_module_calls = 2
    actual_module_calls = mock_create_test_module.call_count
    assert_with_msg(
        actual_module_calls == expected_module_calls,
        f"Expected create_test_module called {expected_module_calls} times, "
        f"got {actual_module_calls}",
    )


def test_create_test_package(tmp_path: Path) -> None:
    """Test func for create_test_package."""
    package_name = create_test_package.__name__
    package_path = tmp_path / package_name
    with chdir(tmp_path):
        package = create_package(package_path)
        create_test_package(package)
        test_package_path = tmp_path / f"tests/{test_create_test_package.__name__}"
        assert test_package_path.exists()


def test_create_test_module(tmp_path: Path) -> None:
    """Test func for create_test_module."""
    # Create a real source module
    module_name = create_test_module.__name__
    module_path = tmp_path / f"{module_name}.py"
    with chdir(tmp_path):
        module = create_module(module_path)
        create_test_module(module)
        test_module_path = tmp_path / f"tests/{test_create_test_module.__name__}.py"
        assert test_module_path.exists()


def test_get_test_module_content(tmp_path: Path) -> None:
    """Test func for get_test_module_content."""
    module_name = test_get_test_module_content.__name__
    module_path = tmp_path / f"{module_name}.py"
    # write a function in the module
    module_content = """
def function_a() -> str:
    return "a"
"""
    module_path.write_text(module_content)
    with chdir(tmp_path):
        # Create the modules
        module = import_module_with_file_fallback(module_path)
        create_test_module(module)

        test_module_content = get_test_module_content(module)
        assert "def test_function_a" in test_module_content


def test_get_test_functions_content(tmp_path: Path) -> None:
    """Test func for get_test_functions_content."""
    # Create a real source module with functions
    source_module_content = '''"""Test source module."""

def function_a() -> str:
    """First function."""
    return "a"

def function_b() -> int:
    """Second function."""
    return 42
'''

    # Create a test module with one existing test
    test_module_content = '''"""Test module."""

def test_function_a() -> None:
    """Test func for function_a."""
    pass
'''

    with chdir(tmp_path):
        # Create the modules
        source_file = tmp_path / "source_module_test_functions_content.py"
        test_file = tmp_path / "test_module_test_functions_content.py"

        source_file.write_text(source_module_content)
        test_file.write_text(test_module_content)

        # Import the modules
        source_module = import_module_with_file_fallback(source_file)
        test_module = import_module_with_file_fallback(test_file)

        # Call the function
        result = get_test_functions_content(
            source_module, test_module, test_module_content
        )
        assert_with_msg(
            "def test_function_b() -> None:" in result,
            "Expected result to contain test_function_b",
        )

        # both are just once in there
        function_a_count = result.count("def test_function_a() -> None:")
        assert_with_msg(
            function_a_count == 1,
            f"Expected one test_function_a, found {function_a_count} occurrences",
        )
        function_b_count = result.count("def test_function_b() -> None:")
        assert_with_msg(
            function_b_count == 1,
            f"Expected one test_function_b, found {function_b_count} occurrences",
        )


def test_get_test_classes_content(tmp_path: Path) -> None:
    """Test func for get_test_classes_content."""
    # Create a real source module with classes
    source_module_content = '''"""Test source module."""

class Calculator:
    """Calculator class."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

class StringHelper:
    """String helper class."""

    def reverse(self, text: str) -> str:
        """Reverse a string."""
        return text[::-1]
'''

    # Create a test module with one existing test class
    test_module_content = '''"""Test module."""

class TestCalculator:
    """Test class."""

    def test_add(self) -> None:
        """Test method for add."""
        pass
'''

    with chdir(tmp_path):
        # Create the modules
        source_file = tmp_path / "source_module_test_classes_content.py"
        test_file = tmp_path / "test_module_test_classes_content.py"
        source_file.write_text(source_module_content)
        test_file.write_text(test_module_content)
        source_module = import_module_with_file_fallback(source_file)
        test_module = import_module_with_file_fallback(test_file)
        # assert inspect.getmembers retunr the classes
        members = inspect.getmembers(source_module, inspect.isclass)
        assert_with_msg(
            len(members) > 1,
            f"Expected 2 classes, got {len(members)}",
        )
        result = get_test_classes_content(
            source_module, test_module, test_module_content
        )
        assert_with_msg(
            "class TestStringHelper:" in result,
            "Expected result to contain TestStringHelper",
        )
        assert_with_msg(
            "def test_reverse(self) -> None:" in result,
            "Expected result to contain test_reverse method",
        )
        assert_with_msg(
            "def test_multiply(self) -> None:" in result,
            "Expected result to contain test_multiply method",
        )

        # both are just once in there
        test_string_helper_count = result.count("class TestStringHelper:")
        assert_with_msg(
            test_string_helper_count == 1,
            f"Expected one TestStringHelper, found {test_string_helper_count} occurrences",  # noqa: E501
        )
        test_multiply_count = result.count("def test_multiply(self) -> None:")
        assert_with_msg(
            test_multiply_count == 1,
            f"Expected one test_multiply, found {test_multiply_count} occurrences",
        )

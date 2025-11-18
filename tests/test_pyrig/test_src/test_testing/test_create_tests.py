"""Tests for pyrig.src.testing.create_tests module."""

import inspect
import os
from contextlib import chdir
from pathlib import Path
from types import ModuleType

from pytest_mock import MockFixture

from pyrig.src.modules.module import import_module_from_path, make_obj_importpath
from pyrig.src.testing import create_tests as create_tests_module
from pyrig.src.testing.assertions import assert_with_msg
from pyrig.src.testing.create_tests import (
    create_test_module,
    create_test_package,
    create_tests,
    create_tests_base,
    create_tests_for_package,
    get_test_classes_content,
    get_test_functions_content,
    get_test_module_content,
)


def test_create_tests(mocker: MockFixture) -> None:
    """Test func for create_tests."""
    # Mock the two main functions that create_tests calls to verify orchestration
    mock_create_tests_base = mocker.patch(
        make_obj_importpath(create_tests_module) + ".create_tests_base"
    )
    mock_create_tests_for_src_package = mocker.patch(
        make_obj_importpath(create_tests_module) + ".create_tests_for_package"
    )

    # Call the function
    create_tests()

    # Verify both functions were called exactly once
    base_count = mock_create_tests_base.call_count
    src_count = mock_create_tests_for_src_package.call_count

    assert_with_msg(
        base_count == 1,
        f"Expected create_tests_base called once, got {base_count}",
    )

    assert_with_msg(
        src_count == 1,
        f"Expected create_tests_for_src_package called once, got {src_count}",
    )


def test_create_tests_base(tmp_path: Path, mocker: MockFixture) -> None:
    """Test func for create_tests_base."""
    # Change to tmp directory for testing
    original_cwd = Path.cwd()
    try:
        os.chdir(tmp_path)

        # Mock only the external dependencies we can't easily test
        mock_copy_package = mocker.patch(
            make_obj_importpath(create_tests_module) + ".copy_package"
        )

        # Create tests directory first (since copy_package is mocked)
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir(exist_ok=True)

        # Call the function
        create_tests_base()

        # Verify copy_package was called
        assert_with_msg(
            mock_copy_package.called,
            "Expected copy_package to be called",
        )

    finally:
        os.chdir(original_cwd)


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


def test_create_test_package(mocker: MockFixture) -> None:
    """Test func for create_test_package."""
    # Mock the dependencies
    mock_make_test_obj_importpath_from_obj = mocker.patch(
        make_obj_importpath(create_tests_module) + ".make_test_obj_importpath_from_obj"
    )
    mock_create_module = mocker.patch(
        make_obj_importpath(create_tests_module) + ".create_module"
    )

    # Create mock package
    mock_package = mocker.MagicMock(spec=ModuleType)

    # Set up mock return values
    test_package_name = "tests.test_package"
    mock_make_test_obj_importpath_from_obj.return_value = test_package_name

    # Call the function
    create_test_package(mock_package)

    # Verify make_test_obj_importpath_from_obj was called with the package
    mock_make_test_obj_importpath_from_obj.assert_called_once_with(mock_package)

    # Verify create_module was called with the test package name and is_package=True
    mock_create_module.assert_called_once_with(test_package_name, is_package=True)


def test_create_test_module(mocker: MockFixture) -> None:
    """Test func for create_test_module."""
    # Mock the dependencies
    mock_make_test_obj_importpath_from_obj = mocker.patch(
        make_obj_importpath(create_tests_module) + ".make_test_obj_importpath_from_obj"
    )
    mock_create_module = mocker.patch(
        make_obj_importpath(create_tests_module) + ".create_module"
    )
    mock_to_path = mocker.patch(make_obj_importpath(create_tests_module) + ".to_path")
    mock_get_test_module_content = mocker.patch(
        make_obj_importpath(create_tests_module) + ".get_test_module_content"
    )

    # Create mock module and path
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_test_module = mocker.MagicMock(spec=ModuleType)
    mock_path = mocker.MagicMock()

    # Set up mock return values
    test_module_name = "tests.test_module"
    test_content = "test module content"
    mock_make_test_obj_importpath_from_obj.return_value = test_module_name
    mock_create_module.return_value = mock_test_module
    mock_to_path.return_value = mock_path
    mock_get_test_module_content.return_value = test_content

    # Call the function
    create_test_module(mock_module)

    # Verify make_test_obj_importpath_from_obj was called
    mock_make_test_obj_importpath_from_obj.assert_called_once_with(mock_module)

    # Verify create_module was called with correct parameters
    mock_create_module.assert_called_once_with(test_module_name, is_package=False)

    # Verify to_path was called with the test module
    mock_to_path.assert_called_once_with(mock_test_module, is_package=False)

    # Verify get_test_module_content was called
    mock_get_test_module_content.assert_called_once_with(mock_module)

    # Verify the content was written to the path
    mock_path.write_text.assert_called_once_with(test_content)


def test_get_test_module_content(mocker: MockFixture) -> None:
    """Test func for get_test_module_content."""
    # Mock the dependencies
    mock_get_test_obj_from_obj = mocker.patch(
        make_obj_importpath(create_tests_module) + ".get_test_obj_from_obj"
    )
    mock_get_module_content_as_str = mocker.patch(
        make_obj_importpath(create_tests_module) + ".get_module_content_as_str"
    )
    mock_get_test_functions_content = mocker.patch(
        make_obj_importpath(create_tests_module) + ".get_test_functions_content"
    )
    mock_get_test_classes_content = mocker.patch(
        make_obj_importpath(create_tests_module) + ".get_test_classes_content"
    )

    # Create mock modules
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_test_module = mocker.MagicMock(spec=ModuleType)

    # Set up mock return values
    initial_content = "initial test module content"
    functions_content = "content with functions"
    final_content = "final content with classes"

    mock_get_test_obj_from_obj.return_value = mock_test_module
    mock_get_module_content_as_str.return_value = initial_content
    mock_get_test_functions_content.return_value = functions_content
    mock_get_test_classes_content.return_value = final_content

    # Call the function
    result = get_test_module_content(mock_module)

    # Verify the result
    assert_with_msg(
        result == final_content,
        f"Expected final content, got {result}",
    )

    # Verify all functions were called in the correct order
    mock_get_test_obj_from_obj.assert_called_once_with(mock_module)
    mock_get_module_content_as_str.assert_called_once_with(mock_test_module)
    mock_get_test_functions_content.assert_called_once_with(
        mock_module, mock_test_module, initial_content
    )
    mock_get_test_classes_content.assert_called_once_with(
        mock_module, mock_test_module, functions_content
    )


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
        source_module = import_module_from_path(source_file)
        test_module = import_module_from_path(test_file)

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
        source_module = import_module_from_path(source_file)
        test_module = import_module_from_path(test_file)
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

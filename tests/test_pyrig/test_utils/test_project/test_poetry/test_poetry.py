"""Tests for pyrig.utils.projects.poetry.poetry module."""

from types import ModuleType

from pytest_mock import MockFixture

from pyrig.utils.project.poetry.poetry import (
    get_poetry_run_cli_cmd_args,
    get_poetry_run_cli_cmd_script,
    get_poetry_run_module_args,
    get_poetry_run_module_script,
    get_poetry_run_pyrig_cli_cmd_args,
    get_poetry_run_pyrig_cli_cmd_script,
    get_python_module_script,
    get_run_python_module_args,
    get_script_from_args,
)
from pyrig.utils.testing.assertions import assert_with_msg


def test_get_script_from_args() -> None:
    """Test func for get_script_from_args."""
    # Test with simple args
    result = get_script_from_args(["poetry", "run", "pytest"])
    assert_with_msg(
        result == "poetry run pytest",
        f"Expected 'poetry run pytest', got '{result}'",
    )

    # Test with single arg
    result = get_script_from_args(["python"])
    assert_with_msg(
        result == "python",
        f"Expected 'python', got '{result}'",
    )

    # Test with empty args
    result = get_script_from_args([])
    assert_with_msg(
        result == "",
        f"Expected empty string, got '{result}'",
    )


def test_get_run_python_module_args(mocker: MockFixture) -> None:
    """Test func for get_run_python_module_args."""
    # Create a mock module
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_module.__name__ = "test_module"

    result = get_run_python_module_args(mock_module)
    assert_with_msg(
        result == ["python", "-m", "test_module"],
        f"Expected ['python', '-m', 'test_module'], got {result}",
    )


def test_get_poetry_run_module_args(mocker: MockFixture) -> None:
    """Test func for get_poetry_run_module_args."""
    # Create a mock module
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_module.__name__ = "test_module"
    result = get_poetry_run_module_args(mock_module)
    assert_with_msg(
        result == ["poetry", "run", "python", "-m", "test_module"],
        f"Expected ['poetry', 'run', 'python', '-m', 'test_module'], got {result}",
    )


def test_get_python_module_script(mocker: MockFixture) -> None:
    """Test func for get_run_python_module_script."""
    # Create a mock module
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_module.__name__ = "my_module"

    result = get_python_module_script(mock_module)
    assert_with_msg(
        result == "python -m my_module",
        f"Expected 'python -m my_module', got '{result}'",
    )


def test_get_poetry_run_module_script(mocker: MockFixture) -> None:
    """Test func for get_poetry_run_module_script."""
    # Create a mock module
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_module.__name__ = "app_module"

    result = get_poetry_run_module_script(mock_module)
    assert_with_msg(
        result == "poetry run python -m app_module",
        f"Expected 'poetry run python -m app_module', got '{result}'",
    )


def test_get_poetry_run_cli_cmd_args() -> None:
    """Test func for get_poetry_run_cli_cmd_args."""

    # Create a mock cmd
    def mock_cmd() -> None:
        pass

    result = get_poetry_run_cli_cmd_args(mock_cmd)
    assert_with_msg(
        result == ["poetry", "run", "pyrig", "mock-cmd"],
        f"Expected ['poetry', 'run', 'pyrig', 'mock-cmd'], got {result}",
    )


def test_get_poetry_run_pyrig_cli_cmd_args() -> None:
    """Test func for get_poetry_run_pyrig_cli_cmd_args."""

    # Create a mock cmd
    def mock_cmd() -> None:
        pass

    result = get_poetry_run_pyrig_cli_cmd_args(mock_cmd)
    assert_with_msg(
        result == ["poetry", "run", "pyrig", "mock-cmd"],
        f"Expected ['poetry', 'run', 'pyrig', 'mock-cmd'], got {result}",
    )


def test_get_poetry_run_cli_cmd_script() -> None:
    """Test func for get_poetry_run_cli_cmd_script."""

    # Create a mock cmd
    def mock_cmd() -> None:
        pass

    result = get_poetry_run_cli_cmd_script(mock_cmd)
    assert_with_msg(
        result == "poetry run pyrig mock-cmd",
        f"Expected 'poetry run pyrig mock-cmd', got '{result}'",
    )


def test_get_poetry_run_pyrig_cli_cmd_script() -> None:
    """Test func for get_poetry_run_pyrig_cli_cmd_script."""

    # Create a mock cmd
    def mock_cmd() -> None:
        pass

    result = get_poetry_run_pyrig_cli_cmd_script(mock_cmd)
    assert_with_msg(
        result == "poetry run pyrig mock-cmd",
        f"Expected 'poetry run pyrig mock-cmd', got '{result}'",
    )

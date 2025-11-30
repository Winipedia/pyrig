"""Tests module."""

from types import ModuleType

from pytest_mock import MockFixture

from pyrig.src.project.mgt import (
    get_project_mgt_run_cli_cmd_args,
    get_project_mgt_run_cli_cmd_script,
    get_project_mgt_run_module_args,
    get_project_mgt_run_module_script,
    get_project_mgt_run_pyrig_cli_cmd_args,
    get_project_mgt_run_pyrig_cli_cmd_script,
    get_python_module_script,
    get_run_python_module_args,
    get_script_from_args,
)
from pyrig.src.testing.assertions import assert_with_msg


def test_get_script_from_args() -> None:
    """Test func for get_script_from_args."""
    # Test with simple args
    result = get_script_from_args(["smth1", "smth2", "smth3"])
    assert result == "smth1 smth2 smth3"

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


def test_get_project_mgt_run_module_args(mocker: MockFixture) -> None:
    """Test func for get_project_mgt_run_module_args."""
    # Create a mock module
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_module.__name__ = "test_module"
    result = get_project_mgt_run_module_args(mock_module)
    assert_with_msg(
        result == ["uv", "run", "python", "-m", "test_module"],
        f"Expected ['uv', 'run', 'python', '-m', 'test_module'], got {result}",
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


def test_get_project_mgt_run_module_script(mocker: MockFixture) -> None:
    """Test func for get_project_mgt_run_module_script."""
    # Create a mock module
    mock_module = mocker.MagicMock(spec=ModuleType)
    mock_module.__name__ = "app_module"

    result = get_project_mgt_run_module_script(mock_module)
    assert_with_msg(
        result == "uv run python -m app_module",
        f"Expected 'uv run python -m app_module', got '{result}'",
    )


def test_get_project_mgt_run_cli_cmd_args() -> None:
    """Test func for get_project_mgt_run_cli_cmd_args."""

    # Create a mock cmd
    def mock_cmd() -> None:
        pass

    result = get_project_mgt_run_cli_cmd_args(mock_cmd)
    assert_with_msg(
        result == ["uv", "run", "pyrig", "mock-cmd"],
        f"Expected ['uv', 'run', 'pyrig', 'mock-cmd'], got {result}",
    )


def test_get_project_mgt_run_pyrig_cli_cmd_args() -> None:
    """Test func for get_project_mgt_run_pyrig_cli_cmd_args."""

    # Create a mock cmd
    def mock_cmd() -> None:
        pass

    result = get_project_mgt_run_pyrig_cli_cmd_args(mock_cmd)
    assert_with_msg(
        result == ["uv", "run", "pyrig", "mock-cmd"],
        f"Expected ['uv', 'run', 'pyrig', 'mock-cmd'], got {result}",
    )


def test_get_project_mgt_run_cli_cmd_script() -> None:
    """Test func for get_project_mgt_run_cli_cmd_script."""

    # Create a mock cmd
    def mock_cmd() -> None:
        pass

    result = get_project_mgt_run_cli_cmd_script(mock_cmd)
    assert_with_msg(
        result == "uv run pyrig mock-cmd",
        f"Expected 'uv run pyrig mock-cmd', got '{result}'",
    )


def test_get_project_mgt_run_pyrig_cli_cmd_script() -> None:
    """Test func for get_project_mgt_run_pyrig_cli_cmd_script."""

    # Create a mock cmd
    def mock_cmd() -> None:
        pass

    result = get_project_mgt_run_pyrig_cli_cmd_script(mock_cmd)
    assert_with_msg(
        result == "uv run pyrig mock-cmd",
        f"Expected 'uv run pyrig mock-cmd', got '{result}'",
    )

"""module."""

from pyrig.src.os.os import run_subprocess
from pyrig.src.project.poetry.poetry import get_poetry_run_pyrig_cli_cmd_args
from pyrig.src.testing.assertions import assert_with_msg


def test_create_root() -> None:
    """Test func for create_root."""
    # run --help comd to see if its available
    stoud = run_subprocess(
        get_poetry_run_pyrig_cli_cmd_args(extra_args=["--help"])
    ).stdout.decode("utf-8")
    assert_with_msg(
        "create-root" in stoud,
        f"Expected create-root in stdout, got {stoud}",
    )


def test_create_tests() -> None:
    """Test func for create_tests."""
    # run --help comd to see if its available
    stoud = run_subprocess(
        get_poetry_run_pyrig_cli_cmd_args(extra_args=["--help"])
    ).stdout.decode("utf-8")
    assert_with_msg(
        "create-tests" in stoud,
        f"Expected create-tests in stdout, got {stoud}",
    )


def test_init() -> None:
    """Test func for setup."""
    # run --help comd to see if its available
    stoud = run_subprocess(
        get_poetry_run_pyrig_cli_cmd_args(extra_args=["--help"])
    ).stdout.decode("utf-8")
    assert_with_msg(
        "init" in stoud,
        f"Expected setup in stdout, got {stoud}",
    )


def test_build() -> None:
    """Test func for build."""
    # run --help comd to see if its available
    stoud = run_subprocess(
        get_poetry_run_pyrig_cli_cmd_args(extra_args=["--help"])
    ).stdout.decode("utf-8")
    assert_with_msg(
        "build" in stoud,
        f"Expected build in stdout, got {stoud}",
    )


def test_protect_repo() -> None:
    """Test func for protect_repo."""
    # run --help comd to see if its available
    stoud = run_subprocess(
        get_poetry_run_pyrig_cli_cmd_args(extra_args=["--help"])
    ).stdout.decode("utf-8")
    assert_with_msg(
        "protect-repo" in stoud,
        f"Expected protect-repo in stdout, got {stoud}",
    )

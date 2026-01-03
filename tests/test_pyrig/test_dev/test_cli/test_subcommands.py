"""module."""

from pyrig.dev.cli.subcommands import (
    build,
    init,
    mkinits,
    mkroot,
    mktests,
    protect_repo,
)
from pyrig.dev.management.pyrigger import Pyrigger


def test_mkroot() -> None:
    """Test func for create_root."""
    # run --help comd to see if its available
    args = Pyrigger.L.get_cmd_args(mkroot, "--help")
    stoud = args.run().stdout.decode("utf-8")
    assert mkroot.__name__ in stoud, (
        f"Expected {mkroot.__name__} in stdout, got {stoud}"
    )


def test_mktests() -> None:
    """Test func for create_tests."""
    # run --help comd to see if its available
    args = Pyrigger.L.get_cmd_args(mktests, "--help")
    stoud = args.run().stdout.decode("utf-8")
    assert mktests.__name__ in stoud, (
        f"Expected {mktests.__name__} in stdout, got {stoud}"
    )


def test_mkinits() -> None:
    """Test func for mkinits."""
    # run --help comd to see if its available
    args = Pyrigger.L.get_cmd_args(mkinits, "--help")
    stoud = args.run().stdout.decode("utf-8")

    assert mkinits.__name__ in stoud, (
        f"Expected {mkinits.__name__} in stdout, got {stoud}"
    )


def test_init() -> None:
    """Test func for setup."""
    # run --help comd to see if its available
    args = Pyrigger.L.get_cmd_args(init, "--help")
    stoud = args.run().stdout.decode("utf-8")
    assert init.__name__ in stoud, f"Expected {init.__name__} in stdout, got {stoud}"


def test_build() -> None:
    """Test func for build."""
    # run --help comd to see if its available
    args = Pyrigger.L.get_cmd_args(build, "--help")
    stoud = args.run().stdout.decode("utf-8")
    assert build.__name__ in stoud, f"Expected {build.__name__} in stdout, got {stoud}"


def test_protect_repo() -> None:
    """Test func for protect_repo."""
    # run --help comd to see if its available
    args = Pyrigger.L.get_cmd_args(protect_repo, "--help")
    stoud = args.run().stdout.decode("utf-8")
    name = protect_repo.__name__.replace("_", "-")
    assert name in stoud, f"Expected {name} in stdout, got {stoud}"

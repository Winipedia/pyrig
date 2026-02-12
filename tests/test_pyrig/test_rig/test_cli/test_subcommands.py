"""module."""

from pyrig.rig.cli.subcommands import (
    build,
    init,
    mkinits,
    mkroot,
    mktests,
    protect_repo,
)
from pyrig.rig.tools.pyrigger import Pyrigger


def test_mkroot() -> None:
    """Test function."""
    # run --help comd to see if its available
    args = Pyrigger.L.cmd_args("--help", cmd=mkroot)
    stoud = args.run().stdout
    assert mkroot.__name__ in stoud, (
        f"Expected {mkroot.__name__} in stdout, got {stoud}"
    )


def test_mktests() -> None:
    """Test function."""
    # run --help comd to see if its available
    args = Pyrigger.L.cmd_args("--help", cmd=mktests)
    stoud = args.run().stdout
    assert mktests.__name__ in stoud, (
        f"Expected {mktests.__name__} in stdout, got {stoud}"
    )


def test_mkinits() -> None:
    """Test function."""
    # run --help comd to see if its available
    args = Pyrigger.L.cmd_args("--help", cmd=mkinits)
    stoud = args.run().stdout

    assert mkinits.__name__ in stoud, (
        f"Expected {mkinits.__name__} in stdout, got {stoud}"
    )


def test_init() -> None:
    """Test function."""
    # run --help comd to see if its available
    args = Pyrigger.L.cmd_args("--help", cmd=init)
    stoud = args.run().stdout
    assert init.__name__ in stoud, f"Expected {init.__name__} in stdout, got {stoud}"


def test_build() -> None:
    """Test function."""
    # run --help comd to see if its available
    args = Pyrigger.L.cmd_args("--help", cmd=build)
    stoud = args.run().stdout
    assert build.__name__ in stoud, f"Expected {build.__name__} in stdout, got {stoud}"


def test_protect_repo() -> None:
    """Test function."""
    # run --help comd to see if its available
    args = Pyrigger.L.cmd_args("--help", cmd=protect_repo)
    stoud = args.run().stdout
    name = protect_repo.__name__.replace("_", "-")
    assert name in stoud, f"Expected {name} in stdout, got {stoud}"

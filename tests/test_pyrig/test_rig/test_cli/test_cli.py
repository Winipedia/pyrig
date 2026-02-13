"""Contains a simple test for cli."""

import logging

from pyrig.rig.cli.cli import configure_logging
from pyrig.rig.tools.pyrigger import Pyrigger


def test_add_subcommands() -> None:
    """Test for the add_subcommands func."""
    # run --help comd to see if its available
    args = Pyrigger.I.args("--help")
    result = args.run()
    stdout = result.stdout
    assert "pyrig" in stdout, f"Expected pyrig in stdout, got {stdout}"


def test_add_shared_subcommands() -> None:
    """Test function."""
    args = Pyrigger.I.args("--help")
    result = args.run()
    stdout = result.stdout
    assert "version" in stdout, f"Expected version in stdout, got {stdout}"


def test_main() -> None:
    """Test for the main cli entrypoint."""
    args = Pyrigger.I.args("--help")
    result = args.run()
    assert result.returncode == 0, "Expected returncode 0"


def test_configure_logging() -> None:
    """Test that configure_logging sets the correct logging level."""
    # Test default (INFO level)
    configure_logging(verbose=0, quiet=False)
    assert logging.root.level == logging.INFO

    # Test quiet mode (WARNING level)
    configure_logging(verbose=0, quiet=True)
    assert logging.root.level == logging.WARNING

    # Test verbose mode (DEBUG level)
    configure_logging(verbose=1, quiet=False)
    assert logging.root.level == logging.DEBUG

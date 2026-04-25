"""Contains a simple test for cli."""

import logging

import pytest
from pytest_mock import MockerFixture

from pyrig.core.cli import package_name_from_argv
from pyrig.core.introspection.modules import import_module_with_default
from pyrig.rig.cli import cli, subcommands
from pyrig.rig.cli.cli import (
    add_shared_subcommands,
    add_subcommands,
    app,
    callback,
    configure_logging,
    main,
)


def test_add_subcommands(mocker: MockerFixture) -> None:
    """Test for the add_subcommands func."""
    argv_mock = mocker.patch(
        cli.__name__ + "." + package_name_from_argv.__name__, return_value="pyrig"
    )
    add_subcommands()
    argv_mock.assert_called_once()
    # check that mkroot is in the app commands
    commands = {cmd.callback.__name__ for cmd in app.registered_commands}  # ty:ignore[unresolved-attribute]
    assert {"mkroot", "mkcmd", "mktests"}.issubset(commands)

    # reset registered commands for other tests
    app.registered_commands = []

    # mock import_module_with_default to return None
    import_module_mock = mocker.patch(
        cli.__name__ + "." + import_module_with_default.__name__,
        return_value=None,
    )
    add_subcommands()
    import_module_mock.assert_called_once_with(subcommands.__name__)

    # assert registered commands is empty since subcommands module could not be imported
    assert len(app.registered_commands) == 0


def test_add_shared_subcommands(mocker: MockerFixture) -> None:
    """Test function."""
    # mock package_name_from_argv to return pyrig for testing
    # bc in pytest it would return pytest instead of pyrig
    argv_mock = mocker.patch(
        cli.__name__ + "." + package_name_from_argv.__name__, return_value="pyrig"
    )
    add_shared_subcommands()
    argv_mock.assert_called_once()
    # check that version is in the app commands
    commands = {cmd.callback.__name__ for cmd in app.registered_commands}  # ty:ignore[unresolved-attribute]
    assert {"version"}.issubset(commands)


def test_main(mocker: MockerFixture) -> None:
    """Test for the main cli entrypoint."""
    # mock package_name_from_argv to return pyrig for testing
    argv_mock = mocker.patch(
        cli.__name__ + "." + package_name_from_argv.__name__, return_value="pyrig"
    )
    with pytest.raises(SystemExit):
        main()
    argv_mock.assert_called()
    commands = {cmd.callback.__name__ for cmd in app.registered_commands}  # ty:ignore[unresolved-attribute]
    assert {"mkroot", "mkcmd", "mktests", "version"}.issubset(commands)


def test_configure_logging() -> None:
    """Test that configure_logging sets the correct logging level."""
    # Test default (INFO level)
    configure_logging(verbose=0, quiet=0)
    assert logging.root.level == logging.INFO

    # Test quiet mode (WARNING level)
    configure_logging(verbose=1, quiet=2)
    assert logging.root.level == logging.WARNING

    # Test verbose mode (DEBUG level)
    configure_logging(verbose=3, quiet=2)
    assert logging.root.level == logging.DEBUG

    # Test very verbose mode (DEBUG level with module names)
    configure_logging(verbose=2, quiet=0)
    assert logging.root.level < logging.DEBUG

    # Test very verbose mode (DEBUG level with timestamps)
    configure_logging(verbose=3, quiet=0)
    assert logging.root.level < logging.DEBUG


def test_callback(mocker: MockerFixture) -> None:
    """Test function."""
    configure_logging_mock = mocker.patch(
        cli.__name__ + "." + configure_logging.__name__
    )
    callback()
    configure_logging_mock.assert_called()

"""Test module."""

import pytest
from pytest_mock import MockerFixture

from pyrig.rig.cli.cli.cli import CLI
from pyrig.rig.cli.commands.version import project_version


def test_project_version(
    capsys: pytest.CaptureFixture[str], mocker: MockerFixture
) -> None:
    """Test function."""
    # mock project_name_from_argv to return "pyrig"
    argv_mock = mocker.patch.object(
        CLI,
        attribute=CLI.project_name.__name__,
        return_value="pyrig",
    )

    assert CLI.I.project_name() == "pyrig"

    assert project_version() is None

    argv_mock.assert_called()

    captured = capsys.readouterr()
    out, err = captured.out, captured.err
    assert out.startswith("pyrig ")
    assert err == ""

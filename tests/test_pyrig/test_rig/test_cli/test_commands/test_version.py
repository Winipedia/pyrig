"""Test module."""

import pytest
from pytest_mock import MockerFixture

from pyrig.core.cli import project_name_from_argv
from pyrig.rig.cli.commands.version import project_version


def test_project_version(
    capsys: pytest.CaptureFixture[str], mocker: MockerFixture
) -> None:
    """Test function."""
    # mock project_name_from_argv to return "pyrig"
    argv_mock = mocker.patch(
        project_version.__module__ + "." + project_name_from_argv.__name__,
        return_value="pyrig",
    )

    assert project_version() is None

    argv_mock.assert_called_once()

    captured = capsys.readouterr()
    out, err = captured.out, captured.err
    assert out.startswith("pyrig version ")
    assert err == ""

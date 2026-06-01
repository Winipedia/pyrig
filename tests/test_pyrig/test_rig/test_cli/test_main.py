"""Contains a simple test for cli."""

import pytest
from pytest_mock import MockerFixture

from pyrig.rig.cli.cli.cli import CLI
from pyrig.rig.cli.main import main


def test_main(mocker: MockerFixture) -> None:
    """Test function."""
    # mock project_name so subcommands resolve to pyrig for testing
    project_name_mock = mocker.patch.object(
        CLI.I, CLI.project_name.__name__, return_value="pyrig"
    )
    with pytest.raises(SystemExit):
        main()
    project_name_mock.assert_called()

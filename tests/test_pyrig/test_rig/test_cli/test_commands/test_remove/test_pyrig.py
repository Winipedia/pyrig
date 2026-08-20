"""Test module."""

from contextlib import chdir
from pathlib import Path

from pytest_mock import MockerFixture

from pyrig.core.subprocesses import Args
from pyrig.rig.cli.commands.remove import pyrig
from pyrig.rig.cli.commands.remove.pyrig import (
    remove_pyrig,
    remove_pyrig_hooks,
    uninstall_pyrig,
)
from pyrig.rig.configs.version_control.hooks.manager import (
    VersionControlHookManagerConfigFile,
)
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.version_control.hooks.manager import VersionControlHookManager


def test_remove_pyrig(mocker: MockerFixture, tmp_path: Path) -> None:
    """Test function."""
    mock_remove_hooks = mocker.patch.object(pyrig, remove_pyrig_hooks.__name__)
    mock_uninstall = mocker.patch.object(pyrig, uninstall_pyrig.__name__)
    with chdir(tmp_path):
        remove_pyrig()
    mock_remove_hooks.assert_called_once()
    mock_uninstall.assert_called_once()


def test_remove_pyrig_hooks(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test function."""
    mock_install = mocker.patch.object(
        VersionControlHookManager,
        VersionControlHookManager.install_args.__name__,
    )
    with chdir(tmp_path):
        VersionControlHookManagerConfigFile.I.validate()
        file_content = VersionControlHookManagerConfigFile.I.path().read_text()
        assert "pyrig sync" in file_content

        remove_pyrig_hooks()
        mock_install.assert_called()

        assert (
            "pyrig sync" not in VersionControlHookManagerConfigFile.I.path().read_text()
        )

    VersionControlHookManagerConfigFile.I.configs.cache_clear()
    VersionControlHookManagerConfigFile.I.load.cache_clear()


def test_uninstall_pyrig(mocker: MockerFixture, tmp_path: Path) -> None:
    """Test function."""
    mock_remove_dev = mocker.patch.object(
        PackageManager,
        PackageManager.remove_group_dev_args.__name__,
        return_value=Args(),
    )
    mock_run = mocker.patch.object(Args, Args.run.__name__)
    with chdir(tmp_path):
        uninstall_pyrig()
    mock_run.assert_called_once()
    mock_remove_dev.assert_called_once()
    args = mock_remove_dev.call_args.args
    assert set(args) == {
        "pyrig",
        "pyrig-codecov",
        "pyrig-pypi",
        "pyrig-resources",
        "pyrig-fixtures",
        "pyrig-overrides",
        "pyrig-env",
    }

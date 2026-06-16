"""test module."""

import platform
from collections.abc import Callable

from pyrig.rig.configs.pyproject import PyprojectConfigFile
from pyrig.rig.tools.version_control.remote import (
    RemoteVersionController,
)


def test_on_linux_and_latest_python_version(
    *, on_linux_and_latest_python_version: bool
) -> None:
    """Test function."""
    current_platform = platform.system()
    current_version = platform.python_version()
    latest_version = PyprojectConfigFile.I.latest_python_version("micro")
    if current_platform == "Linux" and current_version == str(latest_version):
        assert on_linux_and_latest_python_version is True
    else:
        assert on_linux_and_latest_python_version is False


def test_on_platform(on_platform: Callable[[str], bool]) -> None:
    """Test function."""
    current_platform = platform.system()
    assert on_platform(current_platform) is True


def test_on_linux(*, on_linux: bool) -> None:
    """Test function."""
    current_platform = platform.system()
    if current_platform == "Linux":
        assert on_linux is True
    else:
        assert on_linux is False


def test_on_python_version(on_python_version: Callable[[str], bool]) -> None:
    """Test function."""
    current_version = platform.python_version()
    assert on_python_version(current_version) is True


def test_on_latest_python_version(*, on_latest_python_version: bool) -> None:
    """Test function."""
    latest_version = PyprojectConfigFile.I.latest_python_version("micro")
    current_version = platform.python_version()
    if current_version == str(latest_version):
        assert on_latest_python_version is True
    else:
        assert on_latest_python_version is False


def test_on_linux_and_latest_python_version_or_not_in_ci(
    *, on_linux_and_latest_python_version_or_not_in_ci: bool
) -> None:
    """Test function."""
    in_ci = RemoteVersionController.I.running_in_ci()
    current_platform = platform.system()
    latest_version = PyprojectConfigFile.I.latest_python_version("micro")
    current_version = platform.python_version()
    if (
        current_platform == "Linux" and current_version == str(latest_version)
    ) or not in_ci:
        assert on_linux_and_latest_python_version_or_not_in_ci is True
    else:
        assert on_linux_and_latest_python_version_or_not_in_ci is False

"""test module.

We do not test the autouse fixtures directly.
They are tests themselves and are hard to test due to being session scoped and autouse.
"""

import pytest
from pytest_mock import MockerFixture

from pyrig.core.introspection.inspection import unwrapped_obj
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.configs.markdown.readme import ReadmeConfigFile
from pyrig.rig.tests import fixtures
from pyrig.rig.tests.fixtures.autouse.session import (
    all_config_files_correct,
    no_namespace_packages,
    no_unstaged_changes_in_ci,
)
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.packages import find_namespace_packages


def test_no_unstaged_changes_in_ci(mocker: MockerFixture) -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(no_unstaged_changes_in_ci)

    # mock the RemoteVersionController.I.running_in_ci method to return True
    in_ci_mock = mocker.patch.object(
        RemoteVersionController,
        RemoteVersionController.running_in_ci.__name__,
        return_value=True,
    )
    has_diff_mock = mocker.patch.object(
        VersionController,
        VersionController.has_unstaged_diff.__name__,
        return_value=False,
    )
    tuple(unwrapped_func())

    in_ci_mock.assert_called_once()
    has_diff_mock.assert_called()

    has_diff_mock.return_value = True
    with pytest.raises(AssertionError, match=r"Found unstaged changes during tests."):
        tuple(unwrapped_func())


def test_all_config_files_correct(mocker: MockerFixture) -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(all_config_files_correct)
    incorrect_mock = mocker.patch.object(
        ConfigFile,
        ConfigFile.incorrect_subclasses.__name__,
        return_value=[ReadmeConfigFile],
    )
    running_in_ci_mock = mocker.patch.object(
        RemoteVersionController,
        RemoteVersionController.running_in_ci.__name__,
        return_value=True,
    )
    with pytest.raises(AssertionError, match=r"Found incorrect ConfigFiles."):
        unwrapped_func()

    incorrect_mock.assert_called_once()
    running_in_ci_mock.assert_called_once()


def test_no_namespace_packages(mocker: MockerFixture) -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(no_namespace_packages)

    find_mock = mocker.patch(
        no_namespace_packages.__module__ + "." + find_namespace_packages.__name__,
        return_value=[fixtures.__name__],
    )
    with pytest.raises(AssertionError, match=r"Found namespace packages."):
        unwrapped_func()

    find_mock.assert_called_once()


def test_all_modules_tested(mocker: MockerFixture) -> None:
    """Test function."""


def test_all_dependencies_updated() -> None:
    """Test function."""


def test_no_dev_deps_in_source_code() -> None:
    """Test function."""


def test_package_manager_updated() -> None:
    """Test function."""

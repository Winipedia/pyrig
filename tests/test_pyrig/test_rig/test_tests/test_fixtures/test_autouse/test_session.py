"""test module."""

import re
from subprocess import CompletedProcess  # nosec B404

import pytest
from pytest_mock import MockerFixture

from pyrig.core.introspection.inspection import unwrapped_obj
from pyrig.core.requests import internet_is_available
from pyrig.core.subprocesses import Args
from pyrig.rig.configs.markdown.readme import ReadmeConfigFile
from pyrig.rig.tests import fixtures
from pyrig.rig.tests.fixtures.autouse import session
from pyrig.rig.tests.fixtures.autouse.session import (
    all_config_files_correct,
    all_dependencies_updated,
    all_modules_tested,
    no_dev_deps_in_source_code,
    no_namespace_packages,
    no_unstaged_changes_in_ci,
    package_manager_updated,
)
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.package_manager import PackageManager
from pyrig.rig.tools.remote_version_controller import RemoteVersionController
from pyrig.rig.tools.version_controller import VersionController
from pyrig.rig.utils.packages import find_namespace_packages
from pyrig.rig.utils.paths import package_name_as_root_path


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
        ReadmeConfigFile,
        ReadmeConfigFile.is_correct.__name__,
        return_value=False,
    )

    with pytest.raises(
        AssertionError,
        match=rf"(?s){re.escape('Found incorrect ConfigFiles.')}.*{re.escape(str(ReadmeConfigFile.I.path()))}",  # noqa: E501
    ):
        unwrapped_func()

    incorrect_mock.assert_called_once()


def test_no_namespace_packages(mocker: MockerFixture) -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(no_namespace_packages)

    find_mock = mocker.patch(
        no_namespace_packages.__module__ + "." + find_namespace_packages.__name__,
        return_value=iter([fixtures.__name__]),
    )
    expected_path = package_name_as_root_path(fixtures.__name__) / "__init__.py"
    with pytest.raises(
        AssertionError,
        match=rf"(?s){re.escape('Found namespace packages.')}.*{re.escape(str(expected_path))}",  # noqa: E501
    ):
        unwrapped_func()

    find_mock.assert_called_once()


def test_all_modules_tested(mocker: MockerFixture) -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(all_modules_tested)

    subclass = MirrorTestConfigFile.generate_subclass(session)
    incorrect_mock = mocker.patch.object(
        MirrorTestConfigFile,
        MirrorTestConfigFile.incorrect_subclasses.__name__,
        return_value=iter([subclass]),
    )
    expected_path = subclass().path()
    with pytest.raises(
        AssertionError,
        match=rf"(?s){re.escape('Found incorrect test modules.')}.*{re.escape(str(expected_path))}",  # noqa: E501
    ):
        unwrapped_func()

    incorrect_mock.assert_called_once()


def test_all_dependencies_updated(
    mocker: MockerFixture, standard_output_error_template: str
) -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(all_dependencies_updated)
    internet_available_mock = mocker.patch(
        all_dependencies_updated.__module__ + "." + internet_is_available.__name__,
        return_value=not internet_is_available(),
    )

    unwrapped_func(standard_output_error_template=standard_output_error_template)

    internet_available_mock.assert_called_once()


def test_no_dev_deps_in_source_code(
    mocker: MockerFixture,
    tmp_path_factory: pytest.TempPathFactory,
    standard_output_error_template: str,
) -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(no_dev_deps_in_source_code)
    internet_available_mock = mocker.patch(
        no_dev_deps_in_source_code.__module__ + "." + internet_is_available.__name__,
        return_value=not internet_is_available(),
    )
    unwrapped_func(
        tmp_path_factory=tmp_path_factory,
        standard_output_error_template=standard_output_error_template,
    )
    internet_available_mock.assert_called_once()


def test_package_manager_updated(
    mocker: MockerFixture, standard_output_error_template: str
) -> None:
    """Test function."""
    unwrapped_func = unwrapped_obj(package_manager_updated)

    internet_available_mock = mocker.patch(
        package_manager_updated.__module__ + "." + internet_is_available.__name__,
        return_value=not internet_is_available(),
    )
    unwrapped_func(standard_output_error_template=standard_output_error_template)
    internet_available_mock.assert_called_once()

    internet_available_mock.return_value = True
    ci_mock = mocker.patch.object(
        RemoteVersionController,
        RemoteVersionController.running_in_ci.__name__,
        return_value=True,
    )
    unwrapped_func(standard_output_error_template=standard_output_error_template)
    ci_mock.assert_called_once()

    # mock ci to be false so it gets executed in ci as well
    ci_mock.return_value = False

    # make Args.run to return a non-zero exit code
    # to simulate an outdated package manager
    run_mock = mocker.patch.object(
        Args,
        Args.run.__name__,
        return_value=CompletedProcess(args=(), returncode=1, stdout="", stderr=""),
    )

    with pytest.raises(
        AssertionError, match=re.escape(rf"The {PackageManager.I} is not up to date")
    ):
        unwrapped_func(standard_output_error_template=standard_output_error_template)

    run_mock.assert_called_once()

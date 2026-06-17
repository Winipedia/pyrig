"""test module."""

import re

import pytest
from pytest_mock import MockerFixture

from pyrig.core.introspection.inspection import unwrapped_obj
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.tests import fixtures
from pyrig.rig.tests.fixtures.autouse import session
from pyrig.rig.tests.fixtures.autouse.session import (
    all_config_files_correct,
    all_modules_tested,
    no_namespace_packages,
)
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.utils.packages import find_namespace_packages
from pyrig.rig.utils.paths import package_name_as_root_path


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
        MirrorTestConfigFile.discard_correct_subclasses.__name__,
        return_value=iter([subclass]),
    )
    expected_path = subclass().path()
    with pytest.raises(
        AssertionError,
        match=rf"(?s){re.escape('Found incorrect test modules.')}.*{re.escape(str(expected_path))}",  # noqa: E501
    ):
        unwrapped_func()

    incorrect_mock.assert_called_once()

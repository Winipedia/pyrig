"""Session-scoped autouse fixtures for project-wide validation and setup.

These fixtures run automatically once per test session to enforce project
structure, code quality, and development environment standards across every
test run.
"""

import logging

import pytest

from pyrig.core.iterate import iterator_has_items
from pyrig.core.strings import (
    make_summary_error_msg,
)
from pyrig.rig.cli.subcommands import sync
from pyrig.rig.configs.base.config_file import ConfigFile
from pyrig.rig.tests.mirror_test import MirrorTestConfigFile
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.utils.packages import (
    find_namespace_packages,
)
from pyrig.rig.utils.paths import package_name_as_root_path

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def all_config_files_correct() -> None:
    """Fail if any version-controlled config files are incorrect.

    Checks all config files that are tracked by version control. Git-ignored
    files (such as ``.env`` and ``.scratch``) are excluded because they are
    not committed and are expected to be managed manually.

    Raises:
        AssertionError: If any version-controlled config files are incorrect,
            listing the affected paths.
    """
    has_incorrect_config_files, incorrect_config_files = iterator_has_items(
        ConfigFile.discard_correct_subclasses(
            ConfigFile.version_controlled_subclasses()
        )
    )

    msg = f"""Found incorrect {ConfigFile.__name__}s.
Please run the following command to fix any incorrect config files:
    '{Pyrigger.I.cmd_args(cmd=sync)}'

{make_summary_error_msg(cf().path() for cf in incorrect_config_files)}
"""
    assert not has_incorrect_config_files, msg


@pytest.fixture(scope="session", autouse=True)
def no_namespace_packages() -> None:
    """Fail if any packages are missing an ``__init__.py`` file.

    A namespace package is a Python package directory that lacks an
    ``__init__.py`` file. While Python supports them, this project requires
    explicit ``__init__.py`` files everywhere to keep package discovery
    predictable.

    Raises:
        AssertionError: If any namespace packages are found, listing the
            paths of the missing ``__init__.py`` files.
    """
    has_namespace_packages, namespace_packages = iterator_has_items(
        find_namespace_packages()
    )

    msg = f"""Found namespace packages.
Namespace packages are packages that do not have an __init__.py file.
All packages should have an __init__.py file to ensure predictable package discovery.
Please run the following command to create __init__.py files for any namespace packages:
    '{Pyrigger.I.cmd_args(cmd=sync)}'

{make_summary_error_msg(package_name_as_root_path(package_name) / "__init__.py" for package_name in namespace_packages)}
"""  # noqa: E501
    assert not has_namespace_packages, msg


@pytest.fixture(scope="session", autouse=True)
def all_modules_tested() -> None:
    """Fail if any source module lacks a fully mirrored test module.

    Enforces a one-to-one mirror between the source package tree and the test
    package tree. The leaf subclass ``MirrorTestConfigFile.L`` is discovered at
    runtime via the cross-package subclass discovery mechanism.

    Raises:
        AssertionError: If any source modules lack a fully mirrored test
            module (either missing entirely or missing test coverage for one
            or more functions, classes, or methods), listing the affected paths.
    """
    has_incorrect_subclasses, incorrect_subclasses = iterator_has_items(
        MirrorTestConfigFile.L.discard_correct_subclasses(
            MirrorTestConfigFile.L.concrete_subclasses()
        )
    )

    msg = f"""Found incorrect test modules.
It is enforced that all source code has a corresponding mirrored test.

Please run the following command to generate test skeletons for any missing tests:
    '{Pyrigger.I.cmd_args(cmd=sync)}'

{make_summary_error_msg(sc().path() for sc in incorrect_subclasses)}
"""
    assert not has_incorrect_subclasses, msg

"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path
from typing import Any

import pyrig_runtime
import pytest
import requests
from packaging.version import Version
from pyrig_runtime.core.dependencies.distribution import (
    distribution_requirement_as_module_name,
)
from pytest_mock import MockerFixture

from pyrig.rig.configs.community.license import LicenseConfigFile
from pyrig.rig.configs.docs.builder import DocsBuilderConfigFile
from pyrig.rig.configs.pyproject import (
    PyprojectConfigFile,
)
from pyrig.rig.configs.readme import ReadmeConfigFile
from pyrig.rig.tools.base.tool import Tool
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger
from pyrig.rig.tools.version_control.controller import VersionController


@pytest.fixture
def my_test_pyproject_config_file(
    config_file_factory: Callable[
        [type[PyprojectConfigFile]],
        type[PyprojectConfigFile],
    ],
) -> type[PyprojectConfigFile]:
    """Create a test pyproject config file class with tmp_path."""

    class MyTestPyprojectConfigFile(config_file_factory(PyprojectConfigFile)):  # ty: ignore[unsupported-base]
        """Test pyproject config file with tmp_path override."""

    return MyTestPyprojectConfigFile


class TestPyprojectConfigFile:
    """Test class."""

    def test_remote_latest_python_version(
        self,
        *,
        on_linux_and_latest_python_version_or_not_in_ci: bool,
    ) -> None:
        """Test method."""
        if not on_linux_and_latest_python_version_or_not_in_ci:
            return
        latest_version = requests.get(
            "https://endoflife.date/api/python.json",
            timeout=(3, 10),
        ).json()[0]["latest"]
        assert isinstance(latest_version, str)
        assert len(latest_version) > 0
        assert "." in latest_version
        assert latest_version == PyprojectConfigFile.I.latest_python_version_str()
        assert Version(latest_version) == PyprojectConfigFile.I.latest_python_version(
            level="micro",
        )

    def test_stem(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.I.stem() == "pyproject"

    def test_priority(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.I.priority() < LicenseConfigFile.I.priority()
        assert PyprojectConfigFile.I.priority() < ReadmeConfigFile.I.priority()
        assert PyprojectConfigFile.I.priority() > DocsBuilderConfigFile.I.priority()

    def test_requires_python(self) -> None:
        """Test method."""
        requires_python = PyprojectConfigFile.I.requires_python()
        assert isinstance(requires_python, str), (
            f"Expected str, got {type(requires_python)}"
        )

    def test_project_version(self) -> None:
        """Test method."""
        version = PyprojectConfigFile.I.project_version()
        assert isinstance(version, str), f"Expected str, got {type(version)}"

    def test_project_description(self) -> None:
        """Test method."""
        description = PyprojectConfigFile.I.project_description()
        assert isinstance(description, str), "Expected description to be a string"

    def test_parent_path(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        tmp_path: Path,
    ) -> None:
        """Test method."""
        with chdir(tmp_path):
            expected = Path()
            actual = my_test_pyproject_config_file().parent_path()
            assert actual == expected, f"Expected {expected}, got {actual}"

    def test__configs(self) -> None:
        """Test method."""
        # pyproject get configs internally uses load which makes it a special case
        # where the file must exist before calling configs
        configs = PyprojectConfigFile().configs()
        assert "project" in configs
        assert "build-system" in configs
        assert "tool" in configs

        assert configs["project"]["authors"][0]["name"] == "Winipedia"

        assert "classifiers" not in configs["project"]
        assert "keywords" not in configs["project"]

    def test_dependencies(self) -> None:
        """Test method."""
        # dependencies may raise if dependencies key doesn't exist
        # This is expected behavior for the test config
        deps = [
            distribution_requirement_as_module_name(dep)
            for dep in PyprojectConfigFile.I.dependencies()
        ]
        assert deps == [
            "inquirerpy",
            "packaging",
            pyrig_runtime.__name__,
            "ruamel_yaml",
            "ruamel_yaml_clib",
            "spdx_matcher",
            "tomli_w",
            "typer",
        ]

    def test_dev_dependencies(self) -> None:
        """Test method."""
        dev_deps = PyprojectConfigFile.I.dev_dependencies()
        assert isinstance(dev_deps, list)

    def test_latest_possible_python_version(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        # make sure repo owner is cached before entering non git folder tmp
        assert VersionController.I.repo_owner()
        assert VersionController.I.repo_owner()
        # avoid depending on a configured git user.email (absent in CI)
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="fallback@example.com",
        )
        my_test_pyproject_config_file().validate()
        email_mock.assert_called()
        config = my_test_pyproject_config_file().load()
        config["project"]["requires-python"] = ">=3.8, <3.12"
        my_test_pyproject_config_file().dump(config)
        latest_version = (
            my_test_pyproject_config_file().latest_possible_python_version()
        )
        expected = Version("3.11")
        assert latest_version == expected, f"Expected {expected}, got {latest_version}"
        config["project"]["requires-python"] = ">=3.8, <=3.12"
        my_test_pyproject_config_file().dump(config)
        latest_version = (
            my_test_pyproject_config_file().latest_possible_python_version()
        )
        expected = Version("3.12")
        assert latest_version == expected, f"Expected {expected}, got {latest_version}"
        config["project"]["requires-python"] = ">=3.8, <3.11, ==3.10.*"
        my_test_pyproject_config_file().dump(config)
        latest_version = (
            my_test_pyproject_config_file().latest_possible_python_version()
        )
        expected = Version("3.10")
        assert latest_version == expected, f"Expected {expected}, got {latest_version}"
        config["project"]["requires-python"] = ">=3.8"
        my_test_pyproject_config_file().dump(config)
        latest_version = (
            my_test_pyproject_config_file().latest_possible_python_version()
        )
        assert latest_version > Version("3.13"), (
            "Expected latest_possible_python_version to return 3.x"
        )

    def test_supported_python_versions(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        # make sure repo owner is cached before entering non git folder tmp
        assert VersionController.I.repo_owner()
        assert VersionController.I.repo_owner()
        # avoid depending on a configured git user.email (absent in CI)
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="fallback@example.com",
        )
        my_test_pyproject_config_file().validate()
        email_mock.assert_called()
        config = my_test_pyproject_config_file().load()
        config["project"]["requires-python"] = ">=3.8, <3.12"
        my_test_pyproject_config_file().dump(config)
        supported_versions = my_test_pyproject_config_file().supported_python_versions()
        actual = [str(v) for v in supported_versions]
        expected = ["3.8", "3.9", "3.10", "3.11"]
        assert actual == expected, f"Expected {expected}, got {actual}"

        config["project"]["requires-python"] = ">=3.2, <=4.6"
        my_test_pyproject_config_file().dump(config)
        supported_versions = my_test_pyproject_config_file().supported_python_versions()
        actual = [str(v) for v in supported_versions]
        expected = [
            "3.2",
            "3.3",
            "3.4",
            "3.5",
            "3.6",
            "4.2",
            "4.3",
            "4.4",
            "4.5",
            "4.6",
        ]
        assert actual == expected, f"Expected {expected}, got {actual}"

    def test_first_supported_python_version(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        # make sure repo owner is cached before entering non git folder tmp
        assert VersionController.I.repo_owner()
        assert VersionController.I.repo_owner()
        # avoid depending on a configured git user.email (absent in CI)
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="fallback@example.com",
        )
        my_test_pyproject_config_file().validate()
        email_mock.assert_called()
        config = my_test_pyproject_config_file().load()
        config["project"]["requires-python"] = ">=3.8, <3.12"
        my_test_pyproject_config_file().dump(config)
        first_version = str(
            my_test_pyproject_config_file().first_supported_python_version(),
        )
        assert first_version == "3.8", (
            "Expected first_supported_python_version to return 3.8"
        )
        config["project"]["requires-python"] = "<=3.12, >3.8"
        my_test_pyproject_config_file().dump(config)
        first_version = str(
            my_test_pyproject_config_file().first_supported_python_version(),
        )
        assert first_version == "3.8.1", (
            "Expected first_supported_python_version to return 3.8.1"
        )

        # mock requires_python to return an version without lower bound
        requires_mock = mocker.patch.object(
            PyprojectConfigFile,
            PyprojectConfigFile.requires_python.__name__,
            return_value="<3.8",
        )
        with pytest.raises(LookupError):
            my_test_pyproject_config_file().first_supported_python_version()

        requires_mock.assert_called_once()

    def test_latest_python_version(self) -> None:
        """Test method."""
        latest_version = PyprojectConfigFile().latest_python_version()
        assert isinstance(latest_version, Version)
        assert latest_version > Version("3.13")

    def test_latest_python_version_str(self) -> None:
        """Test method."""
        latest_version_str = PyprojectConfigFile.I.latest_python_version_str()
        assert isinstance(latest_version_str, str)
        assert len(latest_version_str) > 0
        assert "." in latest_version_str
        assert Version(
            latest_version_str,
        ) == PyprojectConfigFile.I.latest_python_version(level="micro")

    def test_tool_configs(self) -> None:
        """Test method."""
        assert isinstance(PyprojectConfigFile.I.tool_configs(), dict)
        assert (
            PyprojectConfigFile.I._configs()["tool"]  # noqa: SLF001
            == PyprojectConfigFile.I.tool_configs()
        )
        assert len(PyprojectConfigFile.I.tool_configs()) > 0

    def test_url_configs(self) -> None:
        """Test method."""
        assert isinstance(PyprojectConfigFile.I.url_configs(), dict)
        urls = PyprojectConfigFile.I.url_configs()
        assert "Homepage" in urls
        assert "Source" in urls
        assert "Changelog" in urls
        assert "Documentation" in urls
        assert "Issues" in urls

    def test_validate(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        mock_add = mocker.patch.object(
            PyprojectConfigFile,
            PyprojectConfigFile.add_additional_dependencies.__name__,
        )
        # avoid depending on a configured git user.email (absent in CI)
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="fallback@example.com",
        )
        my_test_pyproject_config_file().validate()
        mock_add.assert_called_once()
        email_mock.assert_called()

    def test_add_additional_dependencies(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        my_test_pyproject_config_file().dump(
            {
                "project": {"dependencies": ["existing-runtime-dep"]},
                "dependency-groups": {"dev": ["existing-dev-dep"]},
            },
        )
        runtime_deps_mock = mocker.patch.object(
            Pyrigger,
            Pyrigger.runtime_dependencies.__name__,
            return_value=["existing-runtime-dep", "new-runtime-dep"],
        )
        dev_deps_mock = mocker.patch.object(
            Tool,
            Tool.subclasses_dev_dependencies.__name__,
            return_value=["existing-dev-dep", "new-dev-dep"],
        )
        add_args_mock = mocker.patch.object(
            PackageManager,
            PackageManager.add_args.__name__,
            return_value=mocker.Mock(),
        )
        add_group_dev_args_mock = mocker.patch.object(
            PackageManager,
            PackageManager.add_group_dev_args.__name__,
            return_value=mocker.Mock(),
        )
        install_deps_mock = mocker.patch.object(
            PackageManager,
            PackageManager.install_dependencies.__name__,
            return_value=mocker.Mock(),
        )

        added = my_test_pyproject_config_file().add_additional_dependencies()

        assert added == ("new-runtime-dep", "new-dev-dep")
        add_args_mock.assert_called_once_with("new-runtime-dep")
        add_args_mock.return_value.run.assert_called_once()
        add_group_dev_args_mock.assert_called_once_with("new-dev-dep")
        add_group_dev_args_mock.return_value.run.assert_called_once()
        install_deps_mock.return_value.run.assert_called_once()

        # cache was cleared and the config re-dumped; since add_args/
        # add_group_dev_args are mocked (no real `uv add`), the file content
        # itself is unchanged and still reflects what was there before
        assert my_test_pyproject_config_file().dependencies() == [
            "existing-runtime-dep",
        ]
        assert my_test_pyproject_config_file().dev_dependencies() == [
            "existing-dev-dep",
        ]

        # nothing missing this time -> no add calls, no cache clear/re-dump
        add_args_mock.reset_mock()
        add_group_dev_args_mock.reset_mock()
        install_deps_mock.reset_mock()
        runtime_deps_mock.return_value = ["existing-runtime-dep"]
        dev_deps_mock.return_value = ["existing-dev-dep"]

        added_again = my_test_pyproject_config_file().add_additional_dependencies()

        assert added_again == ()
        add_args_mock.assert_not_called()
        add_group_dev_args_mock.assert_not_called()
        install_deps_mock.assert_not_called()

    def test_removable(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.I.removable() is False

    def test_merge_configs(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        mock_merge_build_system_requires = mocker.patch.object(
            PyprojectConfigFile,
            PyprojectConfigFile.merge_build_system_requires.__name__,
        )
        PyprojectConfigFile.I.merge_configs()
        mock_merge_build_system_requires.assert_called_once()

    def test_merge_build_system_requires(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
    ) -> None:
        """Test method."""
        configs: dict[str, Any] = {"build-system": {"requires": ["stale-requirement"]}}

        my_test_pyproject_config_file().merge_build_system_requires(configs)

        assert configs["build-system"]["requires"] == (
            PackageManager.I.build_system_requires()
        )

    def test_tool_section(self) -> None:
        """Test method."""
        assert isinstance(PyprojectConfigFile.I.tool_section(), dict)

    def test_authors_configs(self) -> None:
        """Test method."""
        authors = PyprojectConfigFile.I.authors_configs()
        assert {
            "name": VersionController.I.repo_owner(),
            "email": PyprojectConfigFile.I.maintainer_email(),
        } in authors

    def test_maintainer_email(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.I.maintainer_email() == "winipedia@gmx.de"

    def test_maintainer_email_fallback(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        mocker: MockerFixture,
    ) -> None:
        """Test method."""
        email_mock = mocker.patch.object(
            VersionController,
            VersionController.email.__name__,
            return_value="fallback@example.com",
        )
        my_test_pyproject_config_file().dump({"project": {}})
        assert my_test_pyproject_config_file().maintainer_email() == (
            "fallback@example.com"
        )
        email_mock.assert_called_once()

    def test_maintainers_configs(self) -> None:
        """Test method."""
        for author in PyprojectConfigFile.I.authors_configs():
            assert author in PyprojectConfigFile.I.maintainers_configs()

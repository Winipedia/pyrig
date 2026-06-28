"""module."""

from collections.abc import Callable
from contextlib import chdir
from pathlib import Path

import pyrig_runtime
import pytest
from packaging.version import Version
from pyrig_runtime.core.strings import dependency_requirement_as_package_name
from pytest_mock import MockerFixture

from pyrig.rig.configs.license import LicenseConfigFile
from pyrig.rig.configs.pyproject import (
    PyprojectConfigFile,
)
from pyrig.rig.tools.version_control.version_controller import VersionController


@pytest.fixture
def my_test_pyproject_config_file(
    config_file_factory: Callable[
        [type[PyprojectConfigFile]], type[PyprojectConfigFile]
    ],
) -> type[PyprojectConfigFile]:
    """Create a test pyproject config file class with tmp_path."""

    class MyTestPyprojectConfigFile(config_file_factory(PyprojectConfigFile)):  # ty: ignore[unsupported-base]
        """Test pyproject config file with tmp_path override."""

    return MyTestPyprojectConfigFile


class TestPyprojectConfigFile:
    """Test class."""

    def test_remote_latest_python_version(
        self, *, on_linux_and_latest_python_version_or_not_in_ci: bool
    ) -> None:
        """Test method."""
        if not on_linux_and_latest_python_version_or_not_in_ci:
            return
        assert isinstance(PyprojectConfigFile.I.remote_latest_python_version(), str)
        assert len(PyprojectConfigFile.I.remote_latest_python_version()) > 0
        assert "." in PyprojectConfigFile.I.remote_latest_python_version()
        assert (
            PyprojectConfigFile.I.local_latest_python_version()
            == PyprojectConfigFile.I.remote_latest_python_version()
        )

    def test_local_latest_python_version(self) -> None:
        """Test method."""
        assert isinstance(PyprojectConfigFile.I.local_latest_python_version(), str)
        assert len(PyprojectConfigFile.I.local_latest_python_version()) > 0
        assert "." in PyprojectConfigFile.I.local_latest_python_version()

    def test_additional_dependencies(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.I.additional_dependencies() == ["pyrig-runtime"]

    def test_additional_dev_dependencies(self) -> None:
        """Test method."""
        deps = PyprojectConfigFile.I.additional_dev_dependencies()
        assert "pyrig" in deps
        assert "ruff" in deps

    def test_stem(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.I.stem() == "pyproject"

    def test_priority(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.I.priority() < LicenseConfigFile.I.priority()

    def test_detect_project_license(self) -> None:
        """Test method."""
        license_id = PyprojectConfigFile.I.detect_project_license()
        assert license_id == "MIT"

    def test_detect_project_licence_from_content(self) -> None:
        """Test method."""
        with pytest.raises(LookupError):
            _license_id = PyprojectConfigFile.I.detect_project_licence_from_content(
                "No license here"
            )

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

    def test_merge_additional_dependencies(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method."""
        dependencies = ["dep1", "dep1", "dep3[dev]"]
        additional = ["dep3", "dep2"]
        deps_versions = my_test_pyproject_config_file().merge_additional_dependencies(
            dependencies, additional
        )
        assert deps_versions == ["dep1", "dep2", "dep3[dev]"]

    def test_dependencies(self) -> None:
        """Test method."""
        # dependencies may raise if dependencies key doesn't exist
        # This is expected behavior for the test config
        deps = [
            dependency_requirement_as_package_name(dep)
            for dep in PyprojectConfigFile.I.dependencies()
        ]
        assert deps == [
            "inquirerpy",
            "packaging",
            pyrig_runtime.__name__,
            "pyyaml",
            "requests",
            "spdx_matcher",
            "tomlkit",
            "typer",
        ]

    def test_dev_dependencies(self) -> None:
        """Test method."""
        dev_deps = PyprojectConfigFile.I.dev_dependencies()
        assert isinstance(dev_deps, list)

    def test_latest_possible_python_version(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method."""
        # make sure repo owner is cached before entering non git folder tmp
        assert VersionController.I.repo_owner()
        assert VersionController.I.repo_owner()
        my_test_pyproject_config_file().validate()
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
    ) -> None:
        """Test method."""
        # make sure repo owner is cached before entering non git folder tmp
        assert VersionController.I.repo_owner()
        assert VersionController.I.repo_owner()
        my_test_pyproject_config_file().validate()
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
        my_test_pyproject_config_file().validate()
        config = my_test_pyproject_config_file().load()
        config["project"]["requires-python"] = ">=3.8, <3.12"
        my_test_pyproject_config_file().dump(config)
        first_version = str(
            my_test_pyproject_config_file().first_supported_python_version()
        )
        assert first_version == "3.8", (
            "Expected first_supported_python_version to return 3.8"
        )
        config["project"]["requires-python"] = "<=3.12, >3.8"
        my_test_pyproject_config_file().dump(config)
        first_version = str(
            my_test_pyproject_config_file().first_supported_python_version()
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

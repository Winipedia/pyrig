"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest
from packaging.version import Version
from pytest_mock import MockFixture

from pyrig.dev.configs.pyproject import (
    PyprojectConfigFile,
)
from pyrig.dev.configs.python.configs_init import ConfigsInitConfigFile
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_pyproject_config_file(
    config_file_factory: Callable[
        [type[PyprojectConfigFile]], type[PyprojectConfigFile]
    ],
) -> type[PyprojectConfigFile]:
    """Create a test pyproject config file class with tmp_path."""

    class MyTestPyprojectConfigFile(config_file_factory(PyprojectConfigFile)):  # type: ignore [misc]
        """Test pyproject config file with tmp_path override."""

    return MyTestPyprojectConfigFile


class TestPyprojectConfigFile:
    """Test class."""

    def test_get_priority(self) -> None:
        """Test method."""
        assert PyprojectConfigFile.get_priority() > ConfigsInitConfigFile.get_priority()

    def test_detect_project_licence(self) -> None:
        """Test method."""
        license_id = PyprojectConfigFile.detect_project_licence()
        assert license_id == "MIT", f"Expected 'MIT', got '{license_id}'"

    def test_get_latest_python_version(self) -> None:
        """Test method."""
        latest_version = PyprojectConfigFile.get_latest_python_version()
        assert isinstance(latest_version, Version), (
            f"Expected Version, got {type(latest_version)}"
        )

    def test_get_project_requires_python(self) -> None:
        """Test method."""
        requires_python = PyprojectConfigFile.get_project_requires_python()
        assert isinstance(requires_python, str), (
            f"Expected str, got {type(requires_python)}"
        )

    def test_get_project_version(self) -> None:
        """Test method."""
        version = PyprojectConfigFile.get_project_version()
        assert isinstance(version, str), f"Expected str, got {type(version)}"

    def test_make_python_version_classifiers(self) -> None:
        """Test method."""
        classifiers = PyprojectConfigFile.make_python_version_classifiers()
        assert isinstance(classifiers, list), f"Expected list, got {type(classifiers)}"
        for classifier in classifiers:
            assert isinstance(classifier, str), f"Expected str, got {type(classifier)}"

    def test_remove_version_from_dep(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method."""
        dep = "dep (>=1.0.0,<2.0.0)"
        new_dep = my_test_pyproject_config_file.remove_version_from_dep(dep)
        assert new_dep == "dep", f"Expected {new_dep}, got {dep}"

    def test_get_project_description(self) -> None:
        """Test method for get_project_description."""
        description = PyprojectConfigFile.get_project_description()
        assert_with_msg(
            isinstance(description, str),
            "Expected description to be a string",
        )

    def test_is_correct(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for is_correct."""
        my_test_pyproject_config_file()
        is_correct = my_test_pyproject_config_file.is_correct()
        assert_with_msg(
            is_correct,
            "Expected config to be correct after initialization",
        )

    def test__dump(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method for dump."""
        my_test_pyproject_config_file()
        # spy on remove_wrong_dependencies
        spy = mocker.spy(
            my_test_pyproject_config_file,
            my_test_pyproject_config_file.remove_wrong_dependencies.__name__,
        )
        config = my_test_pyproject_config_file.get_configs()
        my_test_pyproject_config_file.dump(config)
        spy.assert_called_once_with(config)

    def test_get_parent_path(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_parent_path."""
        expected = Path()
        actual = my_test_pyproject_config_file.get_parent_path()
        assert_with_msg(actual == expected, f"Expected {expected}, got {actual}")

    def test_get_configs(self) -> None:
        """Test method for get_configs."""
        # pyproject get configs internally uses load which makes it a special case
        # where the file must exist before calling get_configs
        configs = PyprojectConfigFile.get_configs()
        assert_with_msg(
            "project" in configs,
            "Expected 'project' key in configs",
        )
        assert_with_msg(
            "build-system" in configs,
            "Expected 'build-system' key in configs",
        )
        assert_with_msg(
            "tool" in configs,
            "Expected 'tool' key in configs",
        )

    def test_get_package_name(self) -> None:
        """Test method for get_package_name."""
        package_name = PyprojectConfigFile.get_package_name()
        assert_with_msg(
            len(package_name) > 0,
            "Expected package name to be non-empty",
        )

    def test_get_project_name(self) -> None:
        """Test method for get_project_name."""
        project_name = PyprojectConfigFile.get_project_name()
        assert_with_msg(
            len(project_name) > 0,
            "Expected project name to be non-empty",
        )

    def test_make_dependency_versions(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for make_dependency_to_version_dict."""
        dependencies = ["dep1", "dep1"]
        deps_versions = my_test_pyproject_config_file.make_dependency_versions(
            dependencies
        )
        assert deps_versions == ["dep1"]

    def test_remove_wrong_dependencies(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for remove_wrong_dependencies."""
        my_test_pyproject_config_file()
        config = my_test_pyproject_config_file.get_configs()
        # add wrong dependencies to config
        config["project"]["dependencies"] = [
            "wrong>=1.0.0,<2.0.0",
            "wrong>=1.0.0,<2.0.0",
        ]
        my_test_pyproject_config_file.remove_wrong_dependencies(config)
        assert config["project"]["dependencies"] == ["wrong>=1.0.0,<2.0.0"]

    def test_get_all_dependencies(self) -> None:
        """Test method for get_all_dependencies."""
        # get_all_dependencies should return a set (union of deps and dev_deps)
        all_deps = PyprojectConfigFile.get_all_dependencies()
        assert isinstance(all_deps, list), f"Expected list, got {type(all_deps)}"

    def test_get_dependencies(self) -> None:
        """Test method for get_dependencies."""
        # get_dependencies may raise if dependencies key doesn't exist
        # This is expected behavior for the test config
        deps = PyprojectConfigFile.get_dependencies()
        assert isinstance(deps, list), f"Expected list, got {type(deps)}"

    def test_get_dev_dependencies(self) -> None:
        """Test method for get_dev_dependencies."""
        dev_deps = PyprojectConfigFile.get_dev_dependencies()
        assert isinstance(dev_deps, list), f"Expected list, got {type(dev_deps)}"

    def test_get_standard_dev_dependencies(self) -> None:
        """Test method for get_standard_dev_dependencies."""
        standard_dev_deps = PyprojectConfigFile.get_standard_dev_dependencies()
        assert isinstance(standard_dev_deps, list), (
            f"Expected list, got {type(standard_dev_deps)}"
        )

    def test_get_latest_possible_python_version(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_latest_possible_python_version."""
        my_test_pyproject_config_file()
        config = my_test_pyproject_config_file.load()
        config["project"]["requires-python"] = ">=3.8, <3.12"
        my_test_pyproject_config_file.dump(config)
        latest_version = (
            my_test_pyproject_config_file.get_latest_possible_python_version()
        )
        expected = Version("3.11")
        assert_with_msg(
            latest_version == expected,
            f"Expected {expected}, got {latest_version}",
        )
        config["project"]["requires-python"] = ">=3.8, <=3.12"
        my_test_pyproject_config_file.dump(config)
        latest_version = (
            my_test_pyproject_config_file.get_latest_possible_python_version()
        )
        expected = Version("3.12")
        assert_with_msg(
            latest_version == expected,
            f"Expected {expected}, got {latest_version}",
        )
        config["project"]["requires-python"] = ">=3.8, <3.11, ==3.10.*"
        my_test_pyproject_config_file.dump(config)
        latest_version = (
            my_test_pyproject_config_file.get_latest_possible_python_version()
        )
        expected = Version("3.10")
        assert_with_msg(
            latest_version == expected,
            f"Expected {expected}, got {latest_version}",
        )
        config["project"]["requires-python"] = ">=3.8"
        my_test_pyproject_config_file.dump(config)
        latest_version = (
            my_test_pyproject_config_file.get_latest_possible_python_version()
        )
        assert_with_msg(
            latest_version > Version("3.13"),
            "Expected get_latest_possible_python_version to return 3.x",
        )

    def test_fetch_latest_python_version(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for fetch_latest_python_version."""
        latest_version = my_test_pyproject_config_file.fetch_latest_python_version()
        assert_with_msg(
            Version(latest_version) >= Version("3.13"),
            "Expected fetch_latest_python_version to return a version >= 3.11",
        )

    def test_get_supported_python_versions(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_supported_python_versions."""
        my_test_pyproject_config_file()
        config = my_test_pyproject_config_file.load()
        config["project"]["requires-python"] = ">=3.8, <3.12"
        my_test_pyproject_config_file.dump(config)
        supported_versions = (
            my_test_pyproject_config_file.get_supported_python_versions()
        )
        actual = [str(v) for v in supported_versions]
        expected = ["3.8", "3.9", "3.10", "3.11"]
        assert_with_msg(
            actual == expected,
            f"Expected {expected}, got {actual}",
        )

        config["project"]["requires-python"] = ">=3.2, <=4.6"
        my_test_pyproject_config_file.dump(config)
        supported_versions = (
            my_test_pyproject_config_file.get_supported_python_versions()
        )
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
        assert_with_msg(
            actual == expected,
            f"Expected {expected}, got {actual}",
        )

    def test_get_first_supported_python_version(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_first_supported_python_version."""
        my_test_pyproject_config_file()
        config = my_test_pyproject_config_file.load()
        config["project"]["requires-python"] = ">=3.8, <3.12"
        my_test_pyproject_config_file.dump(config)
        first_version = str(
            my_test_pyproject_config_file.get_first_supported_python_version()
        )
        assert_with_msg(
            first_version == "3.8",
            "Expected get_first_supported_python_version to return 3.8",
        )
        config["project"]["requires-python"] = "<=3.12, >3.8"
        my_test_pyproject_config_file.dump(config)
        first_version = str(
            my_test_pyproject_config_file.get_first_supported_python_version()
        )
        assert_with_msg(
            first_version == "3.8.1",
            "Expected get_first_supported_python_version to return 3.8.1",
        )

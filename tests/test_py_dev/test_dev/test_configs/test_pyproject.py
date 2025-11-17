"""module."""

from collections.abc import Callable
from pathlib import Path

import pytest
from packaging.version import Version
from pytest_mock import MockFixture

from py_dev.dev.configs import pyproject
from py_dev.dev.configs.pyproject import (
    PyprojectConfigFile,
)
from py_dev.utils.modules.module import make_obj_importpath
from py_dev.utils.testing.assertions import assert_with_msg


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
    """Test class for PyprojectConfigFile."""

    def test_get_project_description(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_project_description."""
        my_test_pyproject_config_file()
        description = my_test_pyproject_config_file.get_project_description()
        assert_with_msg(
            isinstance(description, str),
            "Expected description to be a string",
        )

    def test_get_project_name_from_pkg_name(self) -> None:
        """Test method for get_project_name_from_pkg_name."""
        pkg_name = "py_dev"
        project_name = PyprojectConfigFile.get_project_name_from_pkg_name(pkg_name)
        assert_with_msg(
            project_name == "py-dev",
            "Expected project name to be py-dev",
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

    def test_dump(
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

    def test_get_configs(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_configs."""
        # pyproject get configs internally uses load which makes it a special case
        # where the file must exist before calling get_configs
        my_test_pyproject_config_file()  # to create file
        configs = my_test_pyproject_config_file.get_configs()
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

    def test_get_project_name_from_cwd(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_repository_name."""
        my_test_pyproject_config_file()
        repository_name = my_test_pyproject_config_file.get_project_name_from_cwd()
        assert_with_msg(
            len(repository_name) > 0,
            "Expected repository name to be non-empty",
        )

    def test_get_package_name(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_package_name."""
        my_test_pyproject_config_file()
        package_name = my_test_pyproject_config_file.get_package_name()
        assert_with_msg(
            len(package_name) > 0,
            "Expected package name to be non-empty",
        )

    def test_get_pkg_name_from_cwd(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_pkg_name_from_cwd."""
        my_test_pyproject_config_file()
        pkg_name = my_test_pyproject_config_file.get_pkg_name_from_cwd()
        assert_with_msg(
            len(pkg_name) > 0,
            "Expected package name to be non-empty",
        )

    def test_get_project_name(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_project_name."""
        my_test_pyproject_config_file()
        project_name = my_test_pyproject_config_file.get_project_name()
        assert_with_msg(
            len(project_name) > 0,
            "Expected project name to be non-empty",
        )

    def test_get_pkg_name_from_project_name(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_pkg_name_from_project_name."""
        my_test_pyproject_config_file()
        pkg_name = my_test_pyproject_config_file.get_pkg_name_from_project_name(
            "py-dev"
        )
        assert_with_msg(
            pkg_name == "py_dev",
            "Expected package name to be py_dev",
        )

    def test_make_dependency_to_version_dict(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for make_dependency_to_version_dict."""
        my_test_pyproject_config_file()
        dependencies: dict[str, str | dict[str, str]] = {
            "dep1": "*",
            "dep2": ">=1.0.0,<2.0.0",
        }
        dep_to_version_dict = (
            my_test_pyproject_config_file.make_dependency_to_version_dict(dependencies)
        )
        assert_with_msg(
            isinstance(dep_to_version_dict, dict),
            "Expected dep_to_version_dict to be equal to dependencies",
        )

    def test_remove_wrong_dependencies(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for remove_wrong_dependencies."""
        my_test_pyproject_config_file()
        config = my_test_pyproject_config_file.get_configs()
        # add wrong dependencies to config
        config["project"]["dependencies"] = ["wrong (>=1.0.0,<2.0.0)"]
        config["tool"]["poetry"]["dev-dependencies"] = {"wrong": "*"}
        cleaned_config = my_test_pyproject_config_file.remove_wrong_dependencies(config)
        # assert wrong sections are removed
        assert_with_msg(
            "dependencies" not in cleaned_config["project"],
            "Expected dev-dependencies section to be deleted",
        )
        assert_with_msg(
            "dev-dependencies" not in cleaned_config["tool"]["poetry"],
            "Expected dev-dependencies section to be deleted",
        )

    def test_get_all_dependencies(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_all_dependencies."""
        my_test_pyproject_config_file()
        # get_all_dependencies should return a set (union of deps and dev_deps)
        all_deps = my_test_pyproject_config_file.get_all_dependencies()
        assert_with_msg(
            isinstance(all_deps, dict),
            "Expected get_all_dependencies to return a set",
        )

    def test_get_dependencies(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_dependencies."""
        my_test_pyproject_config_file()
        # get_dependencies may raise if dependencies key doesn't exist
        # This is expected behavior for the test config
        deps = my_test_pyproject_config_file.get_dependencies()
        assert_with_msg(
            isinstance(deps, dict),
            "Expected get_dependencies to return a set",
        )

    def test_get_dev_dependencies(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_dev_dependencies."""
        my_test_pyproject_config_file()
        dev_deps = my_test_pyproject_config_file.get_dev_dependencies()
        assert_with_msg(
            isinstance(dev_deps, dict),
            "Expected get_dev_dependencies to return a set",
        )

    def test_get_authors(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_authors."""
        my_test_pyproject_config_file()
        config = my_test_pyproject_config_file.load()
        # assert authors rn is empty list
        assert_with_msg(
            my_test_pyproject_config_file.get_authors() == [],
            "Expected get_authors to return an empty list",
        )
        config["project"]["authors"] = [
            {"name": "Test Author", "email": "test@example.com"}
        ]
        my_test_pyproject_config_file.dump(config)
        authors = my_test_pyproject_config_file.get_authors()
        assert_with_msg(
            authors == [{"name": "Test Author", "email": "test@example.com"}],
            "Expected get_authors to return a list with one author",
        )

    def test_get_main_author(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_main_author."""
        my_test_pyproject_config_file()
        config = my_test_pyproject_config_file.load()
        # assert authors rn is empty list
        with pytest.raises(IndexError, match=r"list index out of range"):
            my_test_pyproject_config_file.get_main_author()
        config["project"]["authors"] = [
            {"name": "Test Author", "email": "test@example.com"}
        ]
        my_test_pyproject_config_file.dump(config)
        main_author = my_test_pyproject_config_file.get_main_author()
        assert_with_msg(
            main_author == {"name": "Test Author", "email": "test@example.com"},
            "Expected get_main_author to return the first author",
        )

    def test_get_main_author_name(
        self, my_test_pyproject_config_file: type[PyprojectConfigFile]
    ) -> None:
        """Test method for get_main_author_name."""
        my_test_pyproject_config_file()
        config = my_test_pyproject_config_file.load()
        # assert authors rn is empty list
        with pytest.raises(IndexError, match=r"list index out of range"):
            my_test_pyproject_config_file.get_main_author_name()
        config["project"]["authors"] = [
            {"name": "Test Author", "email": "test@example.com"}
        ]
        my_test_pyproject_config_file.dump(config)
        main_author_name = my_test_pyproject_config_file.get_main_author_name()
        assert_with_msg(
            main_author_name == "Test Author",
            "Expected get_main_author_name to return the first author name",
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
        my_test_pyproject_config_file()
        latest_version = my_test_pyproject_config_file.fetch_latest_python_version()
        assert_with_msg(
            latest_version >= Version("3.13"),
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

    def test_update_dependencies(
        self,
        my_test_pyproject_config_file: type[PyprojectConfigFile],
        mocker: MockFixture,
    ) -> None:
        """Test method for update_dependencies."""
        my_test_pyproject_config_file()
        mock_run = mocker.patch(make_obj_importpath(pyproject) + ".run_subprocess")
        my_test_pyproject_config_file.update_dependencies()
        mock_run.assert_called()

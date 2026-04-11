"""module."""

from collections.abc import Callable

import pytest

from pyrig.rig.configs.testing.project_tester import ProjectTesterConfigFile


@pytest.fixture
def my_test_conftest_config_file(
    config_file_factory: Callable[
        [type[ProjectTesterConfigFile]], type[ProjectTesterConfigFile]
    ],
) -> type[ProjectTesterConfigFile]:
    """Create a test conftest config file class with tmp_path."""

    class MyTestProjectTesterConfigFile(config_file_factory(ProjectTesterConfigFile)):  # ty: ignore[unsupported-base]
        """Test conftest config file with tmp_path override."""

    return MyTestProjectTesterConfigFile


class TestProjectTesterConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert ProjectTesterConfigFile.I.stem() == "conftest"

    def test_is_correct(self) -> None:
        """Test method."""
        assert ProjectTesterConfigFile.I.is_correct()

    def test_lines(
        self, my_test_conftest_config_file: type[ProjectTesterConfigFile]
    ) -> None:
        """Test method."""
        lines = my_test_conftest_config_file().lines()
        content_str = "\n".join(lines)
        assert "pytest_plugins" in content_str, (
            "Expected 'pytest_plugins' in conftest content"
        )

"""module."""

import platform
from collections.abc import Callable
from pathlib import Path

import pytest

from py_dev.dev.artifacts.builder.builder import PydevBuilder
from py_dev.utils.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_py_dev_builder(
    builder_factory: Callable[[type[PydevBuilder]], type[PydevBuilder]],
) -> type[PydevBuilder]:
    """Create a test py_dev build class."""

    class MyTestPydevBuild(builder_factory(PydevBuilder)):  # type: ignore [misc]
        """Test py_dev build class."""

        @classmethod
        def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
            """Build the project."""
            paths = [temp_artifacts_dir / "build.txt"]
            for path in paths:
                path.write_text("Hello World!")

    return MyTestPydevBuild


class TestPydevBuilder:
    """Test class for PydevBuilder."""

    def test_create_artifacts(self, my_test_py_dev_builder: type[PydevBuilder]) -> None:
        """Test method for get_artifacts."""
        my_build = my_test_py_dev_builder()
        artifacts = my_build.get_artifacts()
        assert_with_msg(
            artifacts[0].name == f"build-{platform.system()}.txt",
            "Expected artifact to be built",
        )

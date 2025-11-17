"""module."""

import platform
from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.artifacts.builder.builder import PydevBuilder
from pyrig.utils.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_pyrig_builder(
    builder_factory: Callable[[type[PydevBuilder]], type[PydevBuilder]],
) -> type[PydevBuilder]:
    """Create a test pyrigbuild class."""

    class MyTestPydevBuild(builder_factory(PydevBuilder)):  # type: ignore [misc]
        """Test pyrigbuild class."""

        @classmethod
        def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
            """Build the project."""
            paths = [temp_artifacts_dir / "build.txt"]
            for path in paths:
                path.write_text("Hello World!")

    return MyTestPydevBuild


class TestPydevBuilder:
    """Test class for PydevBuilder."""

    def test_create_artifacts(self, my_test_pyrig_builder: type[PydevBuilder]) -> None:
        """Test method for get_artifacts."""
        my_build = my_test_pyrig_builder()
        artifacts = my_build.get_artifacts()
        assert_with_msg(
            artifacts[0].name == f"build-{platform.system()}.txt",
            "Expected artifact to be built",
        )

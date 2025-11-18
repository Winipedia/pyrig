"""module."""

import platform
from collections.abc import Callable
from pathlib import Path

import pytest

from pyrig.dev.artifacts.builder.builder import PyrigBuilder
from pyrig.src.testing.assertions import assert_with_msg


@pytest.fixture
def my_test_pyrig_builder(
    builder_factory: Callable[[type[PyrigBuilder]], type[PyrigBuilder]],
) -> type[PyrigBuilder]:
    """Create a test pyrigbuild class."""

    class MyTestPyrigBuild(builder_factory(PyrigBuilder)):  # type: ignore [misc]
        """Test pyrigbuild class."""

        @classmethod
        def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
            """Build the project."""
            paths = [temp_artifacts_dir / "build.txt"]
            for path in paths:
                path.write_text("Hello World!")

    return MyTestPyrigBuild


class TestPyrigBuilder:
    """Test class."""

    def test_create_artifacts(self, my_test_pyrig_builder: type[PyrigBuilder]) -> None:
        """Test method for get_artifacts."""
        my_build = my_test_pyrig_builder()
        artifacts = my_build.get_artifacts()
        assert_with_msg(
            artifacts[0].name == f"build-{platform.system()}.txt",
            "Expected artifact to be built",
        )

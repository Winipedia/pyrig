"""Test module."""

from pyrig.dev.artifacts.builder import builder
from pyrig.dev.configs.python.builder import BuilderConfigFile
from pyrig.src.testing.assertions import assert_with_msg


class TestBuilderConfigFile:
    """Test class."""

    def test_get_content_str(self) -> None:
        """Test method for get_content_str."""
        content_str = BuilderConfigFile.get_content_str()
        assert_with_msg(
            len(content_str) > 0,
            "Expected non-empty string",
        )

    def test_get_src_module(self) -> None:
        """Test method for get_src_module."""
        module = BuilderConfigFile.get_src_module()
        assert module == builder

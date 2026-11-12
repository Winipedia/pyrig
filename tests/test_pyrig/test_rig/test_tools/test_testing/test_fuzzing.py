"""Test module."""

from pyrig.rig.tools.testing.fuzzing import FuzzTester


class TestFuzzTester:
    """Test class."""

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert FuzzTester().dev_dependencies() == ("hypothesis", "hypofuzz")

    def test_group(self) -> None:
        """Test method."""
        assert FuzzTester().group() == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            FuzzTester().image_url()
            == "https://img.shields.io/badge/fuzzing-hypothesis-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert FuzzTester().link_url() == "https://hypothesis.readthedocs.io/en/latest/"

    def test_name(self) -> None:
        """Test method."""
        assert FuzzTester().name() == "hypothesis"

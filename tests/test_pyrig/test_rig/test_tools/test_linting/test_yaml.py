"""module."""

from pyrig.rig.tools.linting.yaml import YAMLLinter


class TestYAMLLinter:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert YAMLLinter.I.image_url() == "https://img.shields.io/badge/YAML-ryl-red"

    def test_link_url(self) -> None:
        """Test method."""
        assert YAMLLinter.I.link_url() == "https://github.com/owenlamont/ryl"

    def test_group(self) -> None:
        """Test method."""
        result = YAMLLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = YAMLLinter.I.name()
        assert result == "ryl"

    def test_check_args(self) -> None:
        """Test method."""
        result = YAMLLinter.I.check_args()
        assert result == ("ryl", "check", ".", "-d", "'extends: default'")

    def test_check_fix_args(self) -> None:
        """Test method."""
        result = YAMLLinter.I.check_fix_args()
        assert result == ("ryl", "check", ".", "-d", "'extends: default'", "--fix")

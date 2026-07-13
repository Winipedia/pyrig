"""module."""

from pyrig.rig.tools.formatting.json import JSONFormatter


class TestJSONFormatter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = JSONFormatter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            JSONFormatter.I.image_url()
            == "https://img.shields.io/badge/JSON-pretty--format--json-orange"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            JSONFormatter.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = JSONFormatter.I.name()
        assert result == "pretty-format-json"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = JSONFormatter.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_types(self) -> None:
        """Test method."""
        assert JSONFormatter.I.types() == ["json"]

    def test_format_args(self) -> None:
        """Test method."""
        result = JSONFormatter.I.format_args()
        assert result == (
            "pretty-format-json",
            "--autofix",
            "--no-ensure-ascii",
            "--no-sort-keys",
        )

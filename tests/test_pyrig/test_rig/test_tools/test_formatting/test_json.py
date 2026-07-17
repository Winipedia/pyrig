"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.formatting.json import JSONFormatter
from pyrig.rig.tools.packages.manager import PackageManager


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

    def test_format_args(self) -> None:
        """Test method."""
        result = JSONFormatter.I.format_args()
        assert result == ("pretty-format-json",)

    def test_format_hook(self) -> None:
        """Test method."""
        # JSON formatting runs after the sequential text-fixing chain
        hook = JSONFormatter.I.format_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["json"]
        assert hook["args"] == ["--autofix", "--no-ensure-ascii", "--no-sort-keys"]

    def test_format_json(self) -> None:
        """Test method."""
        base_args = JSONFormatter.I.format_args()
        assert JSONFormatter.I.format_json() == PackageManager.I.run_args(*base_args)

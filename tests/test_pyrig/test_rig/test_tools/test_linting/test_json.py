"""module."""

from pyrig.rig.tools.formatting.json import JSONFormatter
from pyrig.rig.tools.linting.json import JSONLinter


class TestJSONLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = JSONLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            JSONLinter.I.image_url()
            == "https://img.shields.io/badge/JSON-check--json-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            JSONLinter.I.link_url() == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = JSONLinter.I.name()
        assert result == "check-json"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = JSONLinter.I.dev_dependencies()
        assert result == ()

    def test_check_args(self) -> None:
        """Test method."""
        result = JSONLinter.I.check_args()
        assert result == ("check-json",)

    def test_check_hook(self) -> None:
        """Test method."""
        # JSON syntax checking runs after JSON formatting
        hook = JSONLinter.I.check_hook()
        format_hook = JSONFormatter.I.format_hook()
        assert hook["priority"] > format_hook["priority"]

    def test_check_json(self) -> None:
        """Test method."""
        assert JSONLinter.I.check_json() == ()

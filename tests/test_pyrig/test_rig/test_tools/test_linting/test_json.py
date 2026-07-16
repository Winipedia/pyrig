"""module."""

from pyrig.rig.tools.linting.json import JSONLinter
from pyrig.rig.tools.typing.checker import TypeChecker


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
        assert result == ("pre-commit-hooks",)

    def test_lint_args(self) -> None:
        """Test method."""
        result = JSONLinter.I.lint_args()
        assert result == ("check-json",)

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert JSONLinter.I.version_control_hooks() == (JSONLinter.I.lint_hook(),)

    def test_lint_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = JSONLinter.I.lint_hook()
        types_hook = TypeChecker.I.check_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types"] == ["json"]

    def test_lint_json(self) -> None:
        """Test method."""
        assert JSONLinter.I.lint_json() == JSONLinter.I.lint_args()

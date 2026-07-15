"""module."""

from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.typing.checker import TypeChecker


class TestTypeChecker:
    """Test class."""

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            TypeChecker.I.image_url()
            == "https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert TypeChecker.I.link_url() == "https://github.com/astral-sh/ty"

    def test_group(self) -> None:
        """Test method."""
        result = TypeChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_name(self) -> None:
        """Test method."""
        result = TypeChecker.I.name()
        assert result == "ty"

    def test_check_args(self) -> None:
        """Test method."""
        result = TypeChecker.I.check_args()
        assert result == ("ty", "check")

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert TypeChecker.I.version_control_hooks() == (
            TypeChecker.I.check_types_hook(),
        )

    def test_check_types_hook(self) -> None:
        """Test method."""
        # type checking runs after Python formatting, anchoring the checks tier
        hook = TypeChecker.I.check_types_hook()
        format_hook = PythonLinter.I.format_python_hook()
        assert hook["priority"] > format_hook["priority"]
        assert hook["types"] == ["python"]
        assert hook["pass_filenames"] is False

    def test_check_types(self) -> None:
        """Test method."""
        assert TypeChecker.I.check_types() == TypeChecker.I.check_args()

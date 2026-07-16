"""module."""

from pyrig.rig.tools.security.checker import SecurityChecker
from pyrig.rig.tools.typing.checker import TypeChecker


class TestSecurityChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = SecurityChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            SecurityChecker.I.image_url()
            == "https://img.shields.io/badge/security-bandit-yellow.svg"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert SecurityChecker.I.link_url() == "https://github.com/PyCQA/bandit"

    def test_name(self) -> None:
        """Test method."""
        result = SecurityChecker.I.name()
        assert result == "bandit"

    def test_check_args(self) -> None:
        """Test method."""
        result = SecurityChecker.I.check_args("flag1", "flag2")
        assert result == ("bandit", "flag1", "flag2")

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert SecurityChecker.I.version_control_hooks() == (
            SecurityChecker.I.check_security_hook(),
        )

    def test_check_security_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = SecurityChecker.I.check_security_hook()
        types_hook = TypeChecker.I.check_types_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types"] == ["python"]

    def test_check_security(self) -> None:
        """Test method."""
        assert SecurityChecker.I.check_security() == SecurityChecker.I.check_args()

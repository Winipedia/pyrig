"""module."""

from pytest_mock import MockerFixture

from pyrig.rig.tools.linting.python import PythonLinter
from pyrig.rig.tools.linting.security import SecurityLinter
from pyrig.rig.tools.package_manager import PackageManager


class TestSecurityLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = SecurityLinter.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            SecurityLinter.I.image_url()
            == "https://img.shields.io/badge/security-bandit-yellow.svg"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert SecurityLinter.I.link_url() == "https://github.com/PyCQA/bandit"

    def test_name(self) -> None:
        """Test method."""
        result = SecurityLinter.I.name()
        assert result == "bandit"

    def test_extension(self, mocker: MockerFixture) -> None:
        """Test method."""
        # Delegates to PythonLinter rather than coincidentally returning
        # the same literal, so patch it to prove that.
        mock = mocker.patch.object(
            PythonLinter,
            PythonLinter.extension.__name__,
            return_value="mocked-extension",
        )
        assert SecurityLinter.I.extension() == "mocked-extension"
        mock.assert_called_once()

    def test_regex(self) -> None:
        """Test method."""
        assert SecurityLinter.I.regex() == (
            rf"^{PackageManager.I.package_root().as_posix()}/.*\.pyi?$"
        )

    def test_check_args(self) -> None:
        """Test method."""
        result = SecurityLinter.I.check_args("flag1", "flag2")
        assert result == ("bandit", "flag1", "flag2")

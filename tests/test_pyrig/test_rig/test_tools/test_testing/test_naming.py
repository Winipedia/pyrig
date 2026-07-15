"""module."""

from pyrig.rig.tools.testing.naming import TestNamingChecker
from pyrig.rig.tools.testing.project import ProjectTester
from pyrig.rig.tools.typing.checker import TypeChecker


class TestTestNamingChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = TestNamingChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            TestNamingChecker.I.image_url()
            == "https://img.shields.io/badge/test--naming-name--tests--test-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            TestNamingChecker.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = TestNamingChecker.I.name()
        assert result == "name-tests-test"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = TestNamingChecker.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_check_args(self) -> None:
        """Test method."""
        result = TestNamingChecker.I.check_args()
        assert result == ("name-tests-test",)

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert TestNamingChecker.I.version_control_hooks() == (
            TestNamingChecker.I.check_test_naming_hook(),
        )

    def test_check_test_naming_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = TestNamingChecker.I.check_test_naming_hook()
        types_hook = TypeChecker.I.check_types_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types"] == ["python"]
        assert hook["files"] == f"^{ProjectTester.I.package_root().as_posix()}/"
        assert hook["args"] == ["--pytest-test-first"]

    def test_check_test_naming(self) -> None:
        """Test method."""
        assert (
            TestNamingChecker.I.check_test_naming() == TestNamingChecker.I.check_args()
        )

"""module."""

from pyrig.rig.tools.testing.naming import ModuleTestNamingChecker
from pyrig.rig.tools.testing.project import ProjectTester
from pyrig.rig.tools.typing.checker import TypeChecker


class TestModuleTestNamingChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        result = ModuleTestNamingChecker.I.group()
        assert isinstance(result, str)
        assert result == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            ModuleTestNamingChecker.I.image_url()
            == "https://img.shields.io/badge/test--naming-name--tests--test-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert (
            ModuleTestNamingChecker.I.link_url()
            == "https://github.com/pre-commit/pre-commit-hooks"
        )

    def test_name(self) -> None:
        """Test method."""
        result = ModuleTestNamingChecker.I.name()
        assert result == "name-tests-test"

    def test_dev_dependencies(self) -> None:
        """Test method."""
        result = ModuleTestNamingChecker.I.dev_dependencies()
        assert result == ("pre-commit-hooks",)

    def test_check_args(self) -> None:
        """Test method."""
        result = ModuleTestNamingChecker.I.check_args()
        assert result == ("name-tests-test",)

    def test_check_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = ModuleTestNamingChecker.I.check_hook()
        types_hook = TypeChecker.I.check_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types"] == ["python"]
        assert hook["files"] == f"^{ProjectTester.I.package_root().as_posix()}/"
        assert hook["args"] == ["--pytest-test-first"]

    def test_check_test_naming(self) -> None:
        """Test method."""
        assert (
            ModuleTestNamingChecker.I.check_test_naming()
            == ModuleTestNamingChecker.I.check_args()
        )

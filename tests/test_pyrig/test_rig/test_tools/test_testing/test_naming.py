"""module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.testing.naming import ModuleTestNamingChecker
from pyrig.rig.tools.testing.project import ProjectTester


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
        # test naming runs after the general text-fixing chain
        hook = ModuleTestNamingChecker.I.check_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["python"]
        assert hook["files"] == f"^{ProjectTester.I.package_root().as_posix()}/"
        assert hook["args"] == ["--pytest-test-first"]

    def test_check_test_naming(self) -> None:
        """Test method."""
        base_args = ModuleTestNamingChecker.I.check_args()
        assert (
            ModuleTestNamingChecker.I.check_test_naming()
            == PackageManager.I.run_args(*base_args)
        )

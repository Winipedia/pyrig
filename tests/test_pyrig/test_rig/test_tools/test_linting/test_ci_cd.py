"""Test module."""

from pyrig.rig.tools.linting.ci_cd import CICDLinter


class TestCICDLinter:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        assert CICDLinter.I.group() == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            CICDLinter.I.image_url()
            == "https://img.shields.io/badge/CI/CD-actionlint-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert CICDLinter.I.link_url() == "https://github.com/rhysd/actionlint"

    def test_name(self) -> None:
        """Test method."""
        assert CICDLinter.I.name() == "actionlint"

    def test_check_args(self) -> None:
        """Test method."""
        assert CICDLinter.I.check_args() == ("actionlint",)

    def test_check_hook(self) -> None:
        """Test method."""
        hook = CICDLinter.I.check_hook()
        assert isinstance(hook, dict)
        assert hook["types"] == ["yaml"]

    def test_dev_dependencies(self) -> None:
        """Test method."""
        assert CICDLinter.I.dev_dependencies() == (
            "actionlint-py",
            "pyflakes",
            "shellcheck-py",
        )

    def test_lint_ci_cd(self) -> None:
        """Test method."""
        assert CICDLinter.I.lint_ci_cd() == ("uv", "run", "actionlint")

    def test_ci_cd_files_pattern(self) -> None:
        """Test method."""
        assert CICDLinter.I.ci_cd_files_pattern() == r"^\.github/workflows/"

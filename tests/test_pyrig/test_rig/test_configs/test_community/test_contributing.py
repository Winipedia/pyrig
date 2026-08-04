"""module."""

from pathlib import Path

from pyrig.rig.configs.community.contributing import ContributingConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


class TestContributingConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.stem()
        assert result == "CONTRIBUTING"

    def test_parent_path(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.parent_path()
        assert result == Path()

    def test_content(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.content()
        assert result.startswith("# Contributing")
        assert ContributingConfigFile.I.welcome_section() in result
        assert ContributingConfigFile.I.security_notice_section() in result
        assert ContributingConfigFile.I.code_of_conduct_section() in result
        assert ContributingConfigFile.I.ways_to_contribute_section() in result
        assert ContributingConfigFile.I.development_workflow_section() in result
        assert ContributingConfigFile.I.pull_request_section() in result

    def test_welcome_section(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.welcome_section()
        project_name = PackageManager.I.project_name()
        assert f"contribution to {project_name}" in result

    def test_security_notice_section(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.security_notice_section()
        assert result.startswith(">")
        assert "[SECURITY.md](SECURITY.md)" in result

    def test_code_of_conduct_section(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.code_of_conduct_section()
        assert result.startswith("## Code of Conduct")
        assert "[Code of Conduct](CODE_OF_CONDUCT.md)" in result

    def test_ways_to_contribute_section(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.ways_to_contribute_section()
        assert result.startswith("## Ways to Contribute")
        assert "https://github.com/Winipedia/pyrig/issues" in result
        assert "**Bugs**" in result
        assert "**Features**" in result
        assert "**Questions**" in result

    def test_development_workflow_section(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.development_workflow_section()
        assert result.startswith("## Development Workflow")
        assert "`uv sync`" in result
        assert "`uv run prek install`" in result

    def test_pull_request_section(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.pull_request_section()
        assert result.startswith("## Pull Requests")
        assert (
            "https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml"
            in result
        )

"""module."""

from pathlib import Path

from pyrig.rig.configs.community.contributing import ContributingConfigFile
from pyrig.rig.tools.packages.manager import PackageManager


class TestContributingConfigFile:
    """Test class."""

    def test_content(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.content()
        assert result.startswith("# Contributing")
        assert ContributingConfigFile.I.section_welcome() in result
        assert ContributingConfigFile.I.section_security_notice() in result
        assert ContributingConfigFile.I.section_code_of_conduct() in result
        assert ContributingConfigFile.I.section_governance() in result
        assert ContributingConfigFile.I.section_ways_to_contribute() in result
        assert ContributingConfigFile.I.section_development_workflow() in result
        assert ContributingConfigFile.I.section_pull_request() in result

    def test_parent_path(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.parent_path()
        assert result == Path()

    def test_section_code_of_conduct(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.section_code_of_conduct()
        assert result.startswith("## Code of Conduct")
        assert "[Code of Conduct](CODE_OF_CONDUCT.md)" in result

    def test_section_development_workflow(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.section_development_workflow()
        assert result.startswith("## Development Workflow")
        assert "`uv sync`" in result
        assert "`uv run prek install`" in result

    def test_section_governance(self) -> None:
        """Test the default governance statement."""
        assert ContributingConfigFile.I.section_governance() == (
            "## Governance\n\nThe project maintainers make all final decisions."
        )

    def test_section_pull_request(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.section_pull_request()
        assert result.startswith("## Pull Requests")
        assert (
            "https://github.com/Winipedia/pyrig/actions/workflows/health-check.yml"
            in result
        )

    def test_section_security_notice(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.section_security_notice()
        assert result.startswith(">")
        assert "[SECURITY.md](SECURITY.md)" in result

    def test_section_ways_to_contribute(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.section_ways_to_contribute()
        assert result.startswith("## Ways to Contribute")
        assert "https://github.com/Winipedia/pyrig/issues" in result
        assert "**Bugs**" in result
        assert "**Features**" in result
        assert "**Questions**" in result

    def test_section_welcome(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.section_welcome()
        project_name = PackageManager.I.project_name()
        assert f"contribution to {project_name}" in result

    def test_stem(self) -> None:
        """Test method."""
        result = ContributingConfigFile.I.stem()
        assert result == "CONTRIBUTING"

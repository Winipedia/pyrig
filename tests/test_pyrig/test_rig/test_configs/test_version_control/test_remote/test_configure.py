"""Tests for ConfigureRepositoryConfigFile."""

from pathlib import Path

from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class TestConfigureRepositoryConfigFile:
    """Test class."""

    def test_repository_function(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.repository_function() == "repository"

    def test_rulesets_function(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.rulesets_function() == "rulesets"

    def test_vulnerability_reporting_function(self) -> None:
        """Test method."""
        assert (
            ConfigureRepositoryConfigFile.I.vulnerability_reporting_function()
            == "vulnerability_reporting"
        )

    def test_release_immutability_function(self) -> None:
        """Test method."""
        assert (
            ConfigureRepositoryConfigFile.I.release_immutability_function()
            == "release_immutability"
        )

    def test_fork_pr_contributor_approval_function(self) -> None:
        """Test method."""
        assert (
            ConfigureRepositoryConfigFile.I.fork_pr_contributor_approval_function()
            == "fork_pr_contributor_approval"
        )

    def test_parent_path(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.parent_path() == Path(".github")

    def test_stem(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.stem() == "configure"

    def test_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        content = script.script()
        assert script.repo_variable() in content
        assert script.repository_function() in content
        assert script.rulesets_function() in content
        assert script.vulnerability_reporting_function() in content
        assert script.release_immutability_function() in content
        assert script.fork_pr_contributor_approval_function() in content
        assert "gh api" in content
        # the footer must come last so the functions are defined before it runs
        assert content.rstrip("\n").endswith(script.footer_content())

    def test_footer_content(self) -> None:
        """Test method."""
        result = ConfigureRepositoryConfigFile.I.footer_content()
        assert "declare -F" in result
        assert "for step in" in result

    def test_global_content(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.global_content()
        repo = RemoteVersionController.I.repository()
        assert result == f'{script.repo_variable()}="{repo}"'

    def test_repo_variable(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.repo_variable() == "repo"

    def test_repository_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.repository_script()
        assert result.startswith(f"{script.repository_function()}() {{")
        assert "${repo}" in result

    def test_rulesets_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.rulesets_script()
        assert result.startswith(f"{script.rulesets_function()}() {{")
        assert "${repo}" in result
        assert 'gh api "${endpoint}" \\' in result
        assert 'url="${endpoint}${id:+/${id}}"' in result
        assert 'gh api "${url}"' in result
        assert "[[ -z" in result

    def test_vulnerability_reporting_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.vulnerability_reporting_script()
        assert result.startswith(
            f"{script.vulnerability_reporting_function()}() {{",
        )
        assert "${repo}" in result
        assert "private-vulnerability-reporting" in result
        assert "--method=PUT" in result

    def test_release_immutability_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.release_immutability_script()
        assert result.startswith(
            f"{script.release_immutability_function()}() {{",
        )
        assert "${repo}" in result
        assert "immutable-releases" in result
        assert "--method=PUT" in result

    def test_fork_pr_contributor_approval_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.fork_pr_contributor_approval_script()
        assert result.startswith(
            f"{script.fork_pr_contributor_approval_function()}() {{",
        )
        assert "${repo}" in result
        assert "fork-pr-contributor-approval" in result
        assert "--method=PUT" in result

    def test_scripts_content(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        assert script.scripts_content() == "\n\n".join(script.scripts())

    def test_scripts(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I

        for s in (
            script.repository_script(),
            script.rulesets_script(),
            script.vulnerability_reporting_script(),
            script.release_immutability_script(),
            script.fork_pr_contributor_approval_script(),
        ):
            assert s in script.scripts()

"""module."""

from pathlib import Path

from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)


class TestConfigureRepositoryConfigFile:
    """Test class."""

    def test_dependency_alerts_func(self) -> None:
        """Test method."""
        assert (
            ConfigureRepositoryConfigFile.I.dependency_alerts_func()
            == "dependency_alerts"
        )

    def test_dependency_alerts_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.dependency_alerts_script()
        assert result.startswith(
            f"{script.dependency_alerts_func()}() {{",
        )
        assert "${GITHUB_REPOSITORY}" in result
        assert "vulnerability-alerts" in result
        assert "--method=PUT" in result

    def test_dependency_security_updates_func(self) -> None:
        """Test method."""
        assert (
            ConfigureRepositoryConfigFile.I.dependency_security_updates_func()
            == "dependency_security_updates"
        )

    def test_dependency_security_updates_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.dependency_security_updates_script()
        assert result.startswith(
            f"{script.dependency_security_updates_func()}() {{",
        )
        assert "${GITHUB_REPOSITORY}" in result
        assert "automated-security-fixes" in result
        assert "--method=PUT" in result

    def test_footer_content(self) -> None:
        """Test method."""
        result = ConfigureRepositoryConfigFile.I.footer_content()
        assert "declare -F" in result
        assert "for step in" in result

    def test_parent_path(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.parent_path() == Path(".github")

    def test_release_immutability_func(self) -> None:
        """Test method."""
        assert (
            ConfigureRepositoryConfigFile.I.release_immutability_func()
            == "release_immutability"
        )

    def test_release_immutability_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.release_immutability_script()
        assert result.startswith(
            f"{script.release_immutability_func()}() {{",
        )
        assert "${GITHUB_REPOSITORY}" in result
        assert "immutable-releases" in result
        assert "--method=PUT" in result

    def test_repo_func(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.repo_func() == "repository"

    def test_repo_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.repo_script()
        assert result.startswith(f"{script.repo_func()}() {{")
        assert "${GITHUB_REPOSITORY}" in result

    def test_repo_variable(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.repo_variable() == "GITHUB_REPOSITORY"

    def test_required_env_vars(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.required_env_vars() == (
            "GH_TOKEN",
            "GITHUB_REPOSITORY",
        )

    def test_rulesets_func(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.rulesets_func() == "rulesets"

    def test_rulesets_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.rulesets_script()
        assert result.startswith(f"{script.rulesets_func()}() {{")
        assert "${GITHUB_REPOSITORY}" in result
        assert 'gh api "${endpoint}" \\' in result
        assert 'url="${endpoint}${id:+/${id}}"' in result
        assert 'gh api "${url}"' in result
        assert "[[ -z" in result

    def test_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        content = script.script()
        assert script.repo_variable() in content
        assert content.startswith(f"{script.scripts_content()}\n\n")
        assert script.content() == f"{script.global_content()}\n\n{content}"
        assert ': "${GITHUB_REPOSITORY:?}"' in script.global_content()
        assert ': "${GH_TOKEN:?}"' in script.global_content()
        assert script.repo_func() in content
        assert script.rulesets_func() in content
        assert script.dependency_alerts_func() in content
        assert script.dependency_security_updates_func() in content
        assert script.release_immutability_func() in content
        assert "gh api" in content
        # the footer must come last so the functions are defined before it runs
        assert content.rstrip("\n").endswith(script.footer_content())

    def test_scripts(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I

        for s in (
            script.repo_script(),
            script.rulesets_script(),
            script.dependency_alerts_script(),
            script.dependency_security_updates_script(),
            script.release_immutability_script(),
        ):
            assert s in script.scripts()

    def test_scripts_content(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        assert script.scripts_content() == "\n\n".join(sorted(script.scripts()))

    def test_stem(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.stem() == "configure"

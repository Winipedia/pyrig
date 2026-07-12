"""Tests for ConfigureRepositoryConfigFile."""

from pathlib import Path

from pyrig.rig.configs.version_control.remote.configure import (
    ConfigureRepositoryConfigFile,
)
from pyrig.rig.tools.version_control.remote import RemoteVersionController


class TestConfigureRepositoryConfigFile:
    """Test class."""

    def test_apply_repository_settings_function(self) -> None:
        """Test method."""
        assert (
            ConfigureRepositoryConfigFile.I.apply_repository_settings_function()
            == "settings"
        )

    def test_apply_rulesets_function(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.apply_rulesets_function() == "rulesets"

    def test_parent_path(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.parent_path() == Path(".github")

    def test_stem(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.stem() == "configure"

    def test_lines(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        content = "\n".join(script.lines())
        assert content == "\n".join(
            [
                *script.split_lines(script.global_content()),
                "",
                *script.split_lines(script.apply_repository_settings_script()),
                "",
                *script.split_lines(script.apply_rulesets_script()),
                "",
                script.dispatch(),
            ],
        )

    def test_dispatch(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.dispatch() == '"$@"'

    def test_global_content(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.global_content()
        repo = RemoteVersionController.I.repository()
        assert result == f'{script.repo_variable()}="{repo}"'

    def test_repo_variable(self) -> None:
        """Test method."""
        assert ConfigureRepositoryConfigFile.I.repo_variable() == "repo"

    def test_apply_repository_settings_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.apply_repository_settings_script()
        assert result.startswith(f"{script.apply_repository_settings_function()}() {{")
        assert "$repo" in result

    def test_apply_rulesets_script(self) -> None:
        """Test method."""
        script = ConfigureRepositoryConfigFile.I
        result = script.apply_rulesets_script()
        assert result.startswith(f"{script.apply_rulesets_function()}() {{")
        assert "$repo" in result
        assert 'gh api "$endpoint" |' in result
        assert 'gh api "$endpoint${id:+/$id}"' in result

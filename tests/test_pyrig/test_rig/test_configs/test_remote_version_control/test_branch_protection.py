"""module."""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pyrig.rig.configs.dot_env import DotEnvConfigFile
from pyrig.rig.configs.remote_version_control.branch_protection import (
    BranchProtectionConfigFile,
)


class TestBranchProtectionConfigFile:
    """Test class."""

    def test_repo_token(self, mocker: MockerFixture) -> None:
        """Test method."""
        fake_token = "ghp_fakeTokenForTestingPurposesOnly"  # noqa: S105  # nosec: B105
        token = BranchProtectionConfigFile.I.repo_token()
        assert isinstance(token, str)
        assert token != fake_token

        # mock os.getenv to return the fake token for testing
        env_mock = mocker.patch("os.getenv", return_value=fake_token)
        token = BranchProtectionConfigFile.I.repo_token()
        assert token == fake_token
        env_mock.assert_called_with("REPO_TOKEN")

        # mock getenv to return None and
        # mock DotEnvConfigFile.load to return a dict with the fake token
        env_mock.return_value = None
        dotenv_mock = mocker.patch.object(
            DotEnvConfigFile,
            DotEnvConfigFile.load.__name__,
            return_value={"REPO_TOKEN": fake_token},
        )
        token = BranchProtectionConfigFile.I.repo_token()
        assert token == fake_token
        env_mock.assert_called_with("REPO_TOKEN")
        dotenv_mock.assert_called_once()

        # mock both to return None to test the error case
        env_mock.return_value = None
        dotenv_mock.return_value = {}
        with pytest.raises(LookupError):
            BranchProtectionConfigFile.I.repo_token()

    def test_protect_repo(self) -> None:
        """Test method."""
        BranchProtectionConfigFile.I.protect_repo()

    def test_create_or_update_branch_rulesets(self) -> None:
        """Test method."""
        BranchProtectionConfigFile.I.create_or_update_branch_rulesets()

    def test_set_secure_repo_settings(self) -> None:
        """Test method."""
        BranchProtectionConfigFile.I.set_secure_repo_settings()

    def test_parent_path(self) -> None:
        """Test method."""
        assert BranchProtectionConfigFile.I.parent_path() == Path()

    def test_stem(self) -> None:
        """Test method."""
        assert BranchProtectionConfigFile.I.stem() == "branch-protection"

    def test__configs(self) -> None:
        """Test method."""
        configs = BranchProtectionConfigFile.I.configs()
        assert isinstance(configs, list)
        for config in configs:
            assert isinstance(config, dict)

"""Test module."""

from pyrig.rig.tools.security.secrets import SecretsChecker
from pyrig.rig.tools.typing.checker import TypeChecker


class TestSecretsChecker:
    """Test class."""

    def test_group(self) -> None:
        """Test method."""
        assert SecretsChecker.I.group() == "code-quality"

    def test_image_url(self) -> None:
        """Test method."""
        assert (
            SecretsChecker.I.image_url()
            == "https://img.shields.io/badge/secrets-detect--secrets-blue"
        )

    def test_link_url(self) -> None:
        """Test method."""
        assert SecretsChecker.I.link_url() == "https://github.com/Yelp/detect-secrets"

    def test_name(self) -> None:
        """Test method."""
        assert SecretsChecker.I.name() == "detect-secrets"

    def test_check_args(self) -> None:
        """Test method."""
        assert SecretsChecker.I.check_args("arg1", "arg2") == (
            "detect-secrets-hook",
            "arg1",
            "arg2",
        )

    def test_version_control_hooks(self) -> None:
        """Test method."""
        assert SecretsChecker.I.version_control_hooks() == (
            SecretsChecker.I.check_secrets_hook(),
        )

    def test_check_secrets_hook(self) -> None:
        """Test method."""
        # ties into the checks tier rather than running after it
        hook = SecretsChecker.I.check_secrets_hook()
        types_hook = TypeChecker.I.check_types_hook()
        assert hook["priority"] == types_hook["priority"]
        assert hook["types"] == ["text"]

    def test_check_secrets(self) -> None:
        """Test method."""
        assert SecretsChecker.I.check_secrets() == SecretsChecker.I.check_args()

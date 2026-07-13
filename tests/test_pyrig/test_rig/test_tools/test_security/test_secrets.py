"""Test module."""

from pyrig.rig.tools.security.secrets import SecretsChecker


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

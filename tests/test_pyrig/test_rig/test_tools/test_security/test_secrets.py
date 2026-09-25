"""Test module."""

from pyrig.rig.tools.formatting.end_of_file import EndOfFileFormatter
from pyrig.rig.tools.packages.manager import PackageManager
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

    def test_check_hook(self) -> None:
        """Test method."""
        # secrets checking runs after the general text-fixing chain
        hook = SecretsChecker.I.check_hook()
        eof_hook = EndOfFileFormatter.I.format_hook()
        assert hook["priority"] > eof_hook["priority"]
        assert hook["types"] == ["text"]

    def test_check_secrets(self) -> None:
        """Test method."""
        base_args = SecretsChecker.I.check_args()
        assert SecretsChecker.I.check_secrets() == PackageManager.I.run_args(*base_args)

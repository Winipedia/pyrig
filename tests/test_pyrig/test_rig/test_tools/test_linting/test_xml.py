"""Tests for the XML syntax linter."""

from pyrig.rig.tools.linting.xml import XMLLinter
from pyrig.rig.tools.security.secrets import SecretsChecker


class TestXMLLinter:
    """Test the check-xml wrapper and built-in hook metadata."""

    def test_group(self) -> None:
        """Test the badge group."""
        assert XMLLinter.I.group() == "code-quality"

    def test_image_url(self) -> None:
        """Test the badge image URL."""
        assert (
            XMLLinter.I.image_url()
            == "https://img.shields.io/badge/XML-check--xml-blue"
        )

    def test_link_url(self) -> None:
        """Test the built-in hook documentation URL."""
        assert (
            XMLLinter.I.link_url()
            == "https://prek.j178.dev/reference/built-in-hooks/#check-xml"
        )

    def test_name(self) -> None:
        """Test the command name."""
        assert XMLLinter.I.name() == "check-xml"

    def test_dev_dependencies(self) -> None:
        """Test that prek supplies the hook without another dependency."""
        assert XMLLinter.I.dev_dependencies() == ()

    def test_check_args(self) -> None:
        """Test command construction and forwarding XML and SVG paths."""
        assert XMLLinter.I.check_args() == ("check-xml",)
        assert XMLLinter.I.check_args("document.xml", "image.svg") == (
            "check-xml",
            "document.xml",
            "image.svg",
        )

    def test_check_hook(self) -> None:
        """Test the complete hook metadata and read-only check priority."""
        assert XMLLinter.I.check_hook() == {
            "repo": "builtin",
            "id": "check-xml",
            "stages": ["pre-commit"],
            "groups": ["all"],
            "priority": SecretsChecker.I.check_hook()["priority"],
        }

    def test_check_xml(self) -> None:
        """Test that the hook requires no extra arguments."""
        assert XMLLinter.I.check_xml() == ()

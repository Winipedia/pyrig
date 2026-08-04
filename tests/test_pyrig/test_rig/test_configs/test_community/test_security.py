"""module."""

from pathlib import Path

from pyrig.rig.configs.community.security import SecurityConfigFile


class TestSecurityConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.stem()
        assert result == "SECURITY"

    def test_parent_path(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.parent_path()
        assert result == Path()

    def test_content(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.content()
        assert result.startswith("# Security Policy")
        assert SecurityConfigFile.I.supported_versions_section() in result
        assert SecurityConfigFile.I.reporting_section() in result
        assert SecurityConfigFile.I.expectations_section() in result
        assert SecurityConfigFile.I.safe_harbor_section() in result

    def test_supported_versions_section(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.supported_versions_section()
        assert result.startswith("## Supported Versions")
        assert "latest released version" in result

    def test_reporting_section(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.reporting_section()
        assert result.startswith("## Reporting a Vulnerability")
        assert "https://github.com/Winipedia/pyrig/security/advisories/new" in result
        assert "report to that project directly" in result
        assert "special configuration" in result
        assert "Full paths of any source files" in result
        assert "@" not in result

    def test_expectations_section(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.expectations_section()
        assert result.startswith("## What to Expect")
        assert "as soon as possible" in result
        assert "credit" not in result.lower()
        assert "keep you updated" not in result.lower()
        assert "coordinate" not in result.lower()
        assert "business day" not in result.lower()

    def test_safe_harbor_section(self) -> None:
        """Test method."""
        result = SecurityConfigFile.I.safe_harbor_section()
        assert result.startswith("## Safe Harbor")

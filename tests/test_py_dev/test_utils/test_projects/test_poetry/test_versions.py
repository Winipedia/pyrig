"""module."""

from packaging.version import Version

from py_dev.utils.projects.poetry.versions import VersionConstraint
from py_dev.utils.testing.assertions import assert_with_msg


class TestVersionConstraint:
    """Test class for VersionConstraint."""

    def test___init__(self) -> None:
        """Test method for __init__."""
        constraint = ">=3.8, <3.12"
        version_constraint = VersionConstraint(constraint)
        assert_with_msg(
            version_constraint.constraint == constraint,
            f"Expected {constraint}, got {version_constraint.constraint}",
        )

    def test_get_lower_inclusive(self) -> None:
        """Test method for get_lower_inclusive."""
        constraint = ">=3.8, <3.12"
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.get_lower_inclusive()
        expected = "3.8"
        assert_with_msg(
            str(lower) == expected,
            f"Expected {expected}, got {lower}",
        )

        constraint = ">3.8, <3.12"
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.get_lower_inclusive()
        expected = "3.8.1"
        assert_with_msg(
            str(lower) == expected,
            f"Expected {expected}, got {lower}",
        )

        constraint = "<3.12"
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.get_lower_inclusive()
        assert_with_msg(
            lower is None,
            f"Expected None, got {lower}",
        )
        lower = version_constraint.get_lower_inclusive("3.8")
        expected = "3.8"
        assert_with_msg(
            str(lower) == expected,
            f"Expected {expected}, got {lower}",
        )

    def test_get_upper_exclusive(self) -> None:
        """Test method for get_upper_exclusive."""
        constraint = ">=3.8, <3.12"
        version_constraint = VersionConstraint(constraint)
        upper = version_constraint.get_upper_exclusive()
        expected = "3.12"
        assert_with_msg(
            str(upper) == expected,
            f"Expected {expected}, got {upper}",
        )
        constraint = ">=3.8, <=3.12"
        version_constraint = VersionConstraint(constraint)
        upper = version_constraint.get_upper_exclusive()
        expected = "3.12.1"
        assert_with_msg(
            str(upper) == expected,
            f"Expected {expected}, got {upper}",
        )

        constraint = ">=3.8"
        version_constraint = VersionConstraint(constraint)
        upper = version_constraint.get_upper_exclusive()
        assert_with_msg(
            upper is None,
            f"Expected None, got {upper}",
        )
        upper = version_constraint.get_upper_exclusive("3.12")
        expected = "3.12"
        assert_with_msg(
            str(upper) == expected,
            f"Expected {expected}, got {upper}",
        )

    def test_get_upper_inclusive(self) -> None:
        """Test method for get_upper_inclusive."""
        constraint = ">=3.8, <3.12"
        version_constraint = VersionConstraint(constraint)
        upper = version_constraint.get_upper_inclusive()
        expected = "3.11"
        assert_with_msg(
            str(upper) == expected,
            f"Expected {expected}, got {upper}",
        )
        constraint = ">=3.8, <=3.12"
        version_constraint = VersionConstraint(constraint)
        upper = version_constraint.get_upper_inclusive()
        expected = "3.12.0"
        assert_with_msg(
            str(upper) == expected,
            f"Expected {expected}, got {upper}",
        )
        constraint = ">=3.8, <3.12.1"
        version_constraint = VersionConstraint(constraint)
        upper = version_constraint.get_upper_inclusive()
        expected = "3.12.0"
        assert_with_msg(
            str(upper) == expected,
            f"Expected {expected}, got {upper}",
        )

        constraint = ">=3.8"
        version_constraint = VersionConstraint(constraint)
        upper = version_constraint.get_upper_inclusive()
        assert_with_msg(
            upper is None,
            f"Expected None, got {upper}",
        )

        constraint = ">=2.8, <3.12.0"
        version_constraint = VersionConstraint(constraint)
        upper = version_constraint.get_upper_inclusive()
        expected = "3.11"
        assert_with_msg(
            str(upper) == expected,
            f"Expected {expected}, got {upper}",
        )

    def test_get_version_range(self) -> None:
        """Test method for get_version_range."""
        constraint = ">=3, <3.12"
        version_constraint = VersionConstraint(constraint)
        versions = version_constraint.get_version_range(level="major")
        expected = [Version("3")]
        assert_with_msg(
            versions == expected,
            f"Expected {expected}, got {versions}",
        )
        versions = version_constraint.get_version_range(level="minor")
        expected = [
            Version(x)
            for x in [
                "3.0",
                "3.1",
                "3.2",
                "3.3",
                "3.4",
                "3.5",
                "3.6",
                "3.7",
                "3.8",
                "3.9",
                "3.10",
                "3.11",
            ]
        ]
        assert_with_msg(
            versions == expected,
            f"Expected {expected}, got {versions}",
        )
        constraint = ">=3.8.2, <3.9.6"
        version_constraint = VersionConstraint(constraint)
        versions = version_constraint.get_version_range(level="micro")
        expected = [
            Version(x)
            for x in [
                "3.8.2",
                "3.8.3",
                "3.8.4",
                "3.8.5",
                "3.9.2",
                "3.9.3",
                "3.9.4",
                "3.9.5",
            ]
        ]
        assert_with_msg(
            versions == expected,
            f"Expected {expected}, got {versions}",
        )

        constraint = ">=3.12"
        version_constraint = VersionConstraint(constraint)
        versions = version_constraint.get_version_range(
            level="minor", upper_default="3.14.0"
        )
        expected = [Version(x) for x in ["3.12", "3.13", "3.14"]]
        assert_with_msg(
            versions == expected,
            f"Expected {expected}, got {versions}",
        )

        # what if the micro or minor is smaller in lower than upper
        # but the minor or major is larger
        constraint = ">=3.12, <4.1"
        version_constraint = VersionConstraint(constraint)
        versions = version_constraint.get_version_range(level="minor")
        expected = [
            Version(x)
            for x in [
                "3.12",
                "3.13",
                "3.14",
                "3.15",
                "3.16",
                "3.17",
                "3.18",
                "3.19",
                "3.20",
                "3.21",
                "3.22",
                "3.23",
                "3.24",
                "4.0",
            ]
        ]
        assert_with_msg(
            versions == expected,
            f"Expected {expected}, got {versions}",
        )

        constraint = ">=3.11.7, <3.12.2"
        version_constraint = VersionConstraint(constraint)
        versions = version_constraint.get_version_range(level="micro")
        expected = [
            Version(x)
            for x in [
                "3.11.7",
                "3.11.8",
                "3.11.9",
                "3.11.10",
                "3.11.11",
                "3.11.12",
                "3.11.13",
                "3.12.0",
                "3.12.1",
            ]
        ]
        assert_with_msg(
            versions == expected,
            f"Expected {expected}, got {versions}",
        )

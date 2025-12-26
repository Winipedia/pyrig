"""Version parsing and constraint utilities.

This module provides utilities for working with Python version specifiers
and constraints. It wraps the `packaging` library to provide convenient
methods for extracting version bounds and generating version ranges.

The main class `VersionConstraint` parses PEP 440 version specifiers
(e.g., ">=3.8,<3.12") and provides methods to:
    - Get inclusive/exclusive lower and upper bounds
    - Generate lists of versions within a constraint
    - Adjust version precision (major/minor/micro)

Example:
    >>> from pyrig.src.project.versions import VersionConstraint
    >>> vc = VersionConstraint(">=3.8,<3.12")
    >>> vc.get_lower_inclusive()
    <Version('3.8')>
    >>> vc.get_version_range(level="minor")
    [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]
"""

from typing import Literal

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def adjust_version_to_level(
    version: Version, level: Literal["major", "minor", "micro"]
) -> Version:
    """Truncate a version to the specified precision level.

    Args:
        version: The version to adjust.
        level: The precision level to truncate to.

    Returns:
        A new Version with components beyond the level removed.

    Example:
        >>> adjust_version_to_level(Version("3.11.5"), "minor")
        <Version('3.11')>
    """
    if level == "major":
        return Version(f"{version.major}")
    if level == "minor":
        return Version(f"{version.major}.{version.minor}")
    return version


class VersionConstraint:
    """Parser and analyzer for PEP 440 version constraints.

    Parses version specifier strings (e.g., ">=3.8,<3.12") and provides
    methods to extract bounds and generate version ranges. Handles both
    inclusive and exclusive bounds, converting between them as needed.

    Attributes:
        constraint: The original constraint string.
        spec: The cleaned specifier string (quotes stripped).
        sset: The parsed SpecifierSet from the packaging library.
        lower_inclusive: The effective lower bound (inclusive).
        upper_exclusive: The effective upper bound (exclusive).

    Example:
        >>> vc = VersionConstraint(">=3.8,<3.12")
        >>> vc.get_lower_inclusive()
        <Version('3.8')>
        >>> vc.get_upper_exclusive()
        <Version('3.12')>
    """

    def __init__(self, constraint: str) -> None:
        """Initialize a VersionConstraint from a specifier string.

        Args:
            constraint: A PEP 440 version specifier string (e.g., ">=3.8,<3.12").
        """
        self.constraint = constraint
        self.spec = self.constraint.strip().strip('"').strip("'")
        self.sset = SpecifierSet(self.spec)

        self.lowers_inclusive = [
            Version(s.version) for s in self.sset if s.operator == ">="
        ]
        self.lowers_exclusive = [
            Version(s.version) for s in self.sset if s.operator == ">"
        ]
        # increment the last number of exclusive, so
        # >3.4.1 to >=3.4.2; <3.4.0 to <=3.4.1; 3.0.0 to <=3.0.1
        self.lowers_exclusive_to_inclusive = [
            Version(f"{v.major}.{v.minor}.{v.micro + 1}") for v in self.lowers_exclusive
        ]
        self.lowers_inclusive = (
            self.lowers_inclusive + self.lowers_exclusive_to_inclusive
        )

        self.uppers_inclusive = [
            Version(s.version) for s in self.sset if s.operator == "<="
        ]
        self.uppers_exclusive = [
            Version(s.version) for s in self.sset if s.operator == "<"
        ]

        # increment the last number of inclusive, so
        # <=3.4.1 to <3.4.2; >=3.4.0 to >3.4.1; 3.0.0 to >3.0.1
        self.uppers_inclusive_to_exclusive = [
            Version(f"{v.major}.{v.minor}.{v.micro + 1}") for v in self.uppers_inclusive
        ]
        self.uppers_exclusive = (
            self.uppers_inclusive_to_exclusive + self.uppers_exclusive
        )

        self.upper_exclusive = (
            min(self.uppers_exclusive) if self.uppers_exclusive else None
        )
        self.lower_inclusive = (
            max(self.lowers_inclusive) if self.lowers_inclusive else None
        )

    def get_lower_inclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the inclusive lower bound of the version constraint.

        Converts exclusive lower bounds to inclusive equivalents by incrementing
        the micro version. For example, ">3.7.0" becomes ">=3.7.1".

        Args:
            default: Default version to return if no lower bound is specified
                in the constraint. Can be a string or Version object.

        Returns:
            The inclusive lower bound as a Version object, or None if no lower
            bound exists and no default is provided.

        Example:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_lower_inclusive()
            <Version('3.8')>

            >>> vc = VersionConstraint(">3.7.5,<3.12")
            >>> vc.get_lower_inclusive()
            <Version('3.7.6')>

            >>> vc = VersionConstraint("<3.12")
            >>> vc.get_lower_inclusive(default="3.8")
            <Version('3.8')>
        """
        default = str(default) if default else None
        if self.lower_inclusive is None:
            return Version(default) if default else None

        return self.lower_inclusive

    def get_upper_exclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the exclusive upper bound of the version constraint.

        Converts inclusive upper bounds to exclusive equivalents by incrementing
        the micro version. For example, "<=3.11.5" becomes "<3.11.6".

        Args:
            default: Default version to return if no upper bound is specified
                in the constraint. Can be a string or Version object.

        Returns:
            The exclusive upper bound as a Version object, or None if no upper
            bound exists and no default is provided.

        Example:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_upper_exclusive()
            <Version('3.12')>

            >>> vc = VersionConstraint(">=3.8,<=3.11.5")
            >>> vc.get_upper_exclusive()
            <Version('3.11.6')>

            >>> vc = VersionConstraint(">=3.8")
            >>> vc.get_upper_exclusive(default="4.0")
            <Version('4.0')>
        """
        default = str(default) if default else None
        if self.upper_exclusive is None:
            return Version(default) if default else None

        return self.upper_exclusive

    def get_upper_inclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the inclusive upper bound of the version constraint.

        Converts exclusive upper bounds to inclusive equivalents by decrementing
        the appropriate version component. For example, "<3.12.0" becomes "<=3.11".

        Args:
            default: Default version to return if no upper bound is specified
                in the constraint. Can be a string or Version object. The default
                is automatically incremented by one micro version to convert it
                to an exclusive bound internally.

        Returns:
            The inclusive upper bound as a Version object, or None if no upper
            bound exists and no default is provided.

        Example:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_upper_inclusive()
            <Version('3.11')>

            >>> vc = VersionConstraint(">=3.8,<=3.11.5")
            >>> vc.get_upper_inclusive()
            <Version('3.11.5')>

            >>> vc = VersionConstraint(">=3.8,<3.12.0")
            >>> vc.get_upper_inclusive()
            <Version('3.11')>
        """
        # increment the default by 1 micro to make it exclusive
        if default:
            default = Version(str(default))
            default = Version(f"{default.major}.{default.minor}.{default.micro + 1}")
        upper_exclusive = self.get_upper_exclusive(default)
        if upper_exclusive is None:
            return None

        if upper_exclusive.micro != 0:
            return Version(
                f"{upper_exclusive.major}.{upper_exclusive.minor}.{upper_exclusive.micro - 1}"  # noqa: E501
            )
        if upper_exclusive.minor != 0:
            return Version(f"{upper_exclusive.major}.{upper_exclusive.minor - 1}")
        return Version(f"{upper_exclusive.major - 1}")

    def get_version_range(
        self,
        level: Literal["major", "minor", "micro"] = "major",
        lower_default: str | Version | None = None,
        upper_default: str | Version | None = None,
    ) -> list[Version]:
        """Generate a list of versions within the constraint at the specified precision.

        Creates a list of all versions that satisfy the constraint, incrementing
        at the specified level (major, minor, or micro). This is useful for
        generating test matrices or listing supported versions.

        Args:
            level: The precision level for version increments:
                - "major": Increment major version (e.g., 3, 4, 5)
                - "minor": Increment minor version (e.g., 3.8, 3.9, 3.10)
                - "micro": Increment micro version (e.g., 3.8.1, 3.8.2, 3.8.3)
            lower_default: Default lower bound if the constraint doesn't specify one.
                Can be a string or Version object.
            upper_default: Default upper bound if the constraint doesn't specify one.
                Can be a string or Version object.

        Returns:
            List of Version objects satisfying the constraint, sorted in ascending
            order. Only versions that pass the constraint's `contains()` check are
            included.

        Raises:
            ValueError: If no lower or upper bound can be determined (either from
                the constraint or defaults).

        Example:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_version_range(level="minor")
            [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]

            >>> vc = VersionConstraint(">=3.8,<4.0")
            >>> vc.get_version_range(level="major")
            [<Version('3')>]

            >>> vc = VersionConstraint(">=3.10.1,<=3.10.3")
            >>> vc.get_version_range(level="micro")
            [<Version('3.10.1')>, <Version('3.10.2')>, <Version('3.10.3')>]
        """
        lower = self.get_lower_inclusive(lower_default)
        upper = self.get_upper_inclusive(upper_default)

        if lower is None or upper is None:
            msg = "No lower or upper bound. Please specify default values."
            raise ValueError(msg)

        major_level, minor_level, micro_level = range(3)
        level_int = {"major": major_level, "minor": minor_level, "micro": micro_level}[
            level
        ]
        lower_as_list = [lower.major, lower.minor, lower.micro]
        upper_as_list = [upper.major, upper.minor, upper.micro]

        versions: list[list[int]] = []
        for major in range(lower_as_list[major_level], upper_as_list[major_level] + 1):
            version = [major]

            minor_lower_og, minor_upper_og = (
                lower_as_list[minor_level],
                upper_as_list[minor_level],
            )
            diff = minor_upper_og - minor_lower_og
            minor_lower = minor_lower_og if diff >= 0 else 0
            minor_upper = minor_upper_og if diff >= 0 else minor_lower_og + abs(diff)
            for minor in range(
                minor_lower,
                minor_upper + 1,
            ):
                # pop the minor if one already exists
                if len(version) > minor_level:
                    version.pop()

                version.append(minor)

                micro_lower_og, micro_upper_og = (
                    lower_as_list[micro_level],
                    upper_as_list[micro_level],
                )
                diff = micro_upper_og - micro_lower_og
                micro_lower = micro_lower_og if diff >= 0 else 0
                micro_upper = (
                    micro_upper_og if diff >= 0 else micro_lower_og + abs(diff)
                )
                for micro in range(
                    micro_lower,
                    micro_upper + 1,
                ):
                    version.append(micro)
                    versions.append(version[: level_int + 1])
                    version.pop()
        version_versions = sorted({Version(".".join(map(str, v))) for v in versions})
        return [v for v in version_versions if self.sset.contains(v)]

"""Version constraint parsing and range generation utilities.

Utilities for working with PEP 440 version specifiers. Wraps the packaging library
to provide convenient methods for extracting version bounds and generating ranges.

VersionConstraint parses PEP 440 specifier strings (e.g., ">=3.8,<3.12") to:
- Extract inclusive and exclusive lower and upper bounds
- Generate lists of versions within a constraint
- Adjust version precision (major/minor/micro)

Functions:
    adjust_version_to_level: Truncate version to specific precision level

Classes:
    VersionConstraint: Parser and analyzer for PEP 440 version constraints

Examples:
    Parse and extract bounds::

        >>> vc = VersionConstraint(">=3.8,<3.12")
        >>> vc.get_lower_inclusive()
        <Version('3.8')>

    Generate version range::

        >>> vc.get_version_range(level="minor")
        [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]

See Also:
    packaging.specifiers: PEP 440 version specifier implementation
"""

from typing import Literal

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def adjust_version_to_level(
    version: Version, level: Literal["major", "minor", "micro"]
) -> Version:
    """Truncate a version to the specified precision level.

    Removes components beyond the specified level. E.g., "3.11.5" to "minor" -> "3.11".

    Args:
        version: Version to truncate (packaging.version.Version).
        level: Precision level:
            - "major": Keep only major (e.g., "3.11.5" -> "3")
            - "minor": Keep major and minor (e.g., "3.11.5" -> "3.11")
            - "micro": Return version unchanged (e.g., "3.11.5" -> "3.11.5")

    Returns:
        New Version object with components beyond level removed. For "micro" level,
        returns the original Version object unchanged (including any pre-release,
        post-release, dev, or local identifiers).

    Examples:
        >>> adjust_version_to_level(Version("3.11.5"), "major")
        <Version('3')>
        >>> adjust_version_to_level(Version("3.11.5"), "minor")
        <Version('3.11')>

    Note:
        For "major" and "minor" levels, pre-release, post-release, dev, and local
        identifiers are removed. For "micro" level, the version is returned unchanged.
    """
    if level == "major":
        return Version(f"{version.major}")
    if level == "minor":
        return Version(f"{version.major}.{version.minor}")
    return version


class VersionConstraint:
    """Parser and analyzer for PEP 440 version constraints.

    Parses specifier strings (e.g., ">=3.8,<3.12") to extract bounds and generate
    version ranges. Converts between inclusive and exclusive bounds by
    incrementing/decrementing micro version.

    Examples: ">3.7.0" -> ">=3.7.1", "<=3.11.5" -> "<3.11.6"

    Attributes:
        constraint (str): Original constraint string.
        spec (str): Cleaned specifier (quotes/whitespace stripped).
        sset (SpecifierSet): Parsed SpecifierSet from packaging library.
        lowers_inclusive (list[Version]): All lower bounds in inclusive form.
        lowers_exclusive (list[Version]): All lower bounds in exclusive form.
        lowers_exclusive_to_inclusive (list[Version]): Exclusive lower bounds
            converted to inclusive by incrementing micro.
        uppers_inclusive (list[Version]): All upper bounds in inclusive form.
        uppers_exclusive (list[Version]): All upper bounds in exclusive form.
        uppers_inclusive_to_exclusive (list[Version]): Inclusive upper bounds
            converted to exclusive by incrementing micro.
        lower_inclusive (Version | None): Effective lower bound (max of all lowers).
        upper_exclusive (Version | None): Effective upper bound (min of all uppers).

    Examples:
        Parse and extract bounds::

            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_lower_inclusive()
            <Version('3.8')>

        Generate version range::

            >>> vc.get_version_range(level="minor")
            [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]

    Note:
        Assumes non-negative integer version components. Converts bounds by
        incrementing/decrementing micro version.
    """

    def __init__(self, constraint: str) -> None:
        """Initialize a VersionConstraint from a PEP 440 specifier string.

        Parses constraint and computes all inclusive and exclusive bounds.
        Supports multiple specifiers separated by commas (e.g., ">=3.8,<3.12").

        Args:
            constraint: PEP 440 version specifier string. Examples: ">=3.8,<3.12",
                ">3.7,<=3.11", ">=3.8", "<4.0". Can be quoted or unquoted.
                Quotes and whitespace automatically stripped.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> print(vc.lower_inclusive)
            3.8
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

        Returns effective lower bound in inclusive form (>=). Exclusive bounds (>)
        converted by incrementing micro version (e.g., ">3.7.0" -> ">=3.7.1").
        Multiple bounds return maximum (most restrictive).

        Args:
            default: Default version if no lower bound specified. Can be string
                (e.g., "3.8") or Version object. None if no bound and no default.

        Returns:
            Inclusive lower bound as Version, or None if no bound and no default.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_lower_inclusive()
            <Version('3.8')>
            >>> vc = VersionConstraint(">3.7.5,<3.12")
            >>> vc.get_lower_inclusive()  # >3.7.5 becomes >=3.7.6
            <Version('3.7.6')>

        Note:
            Conversion increments micro version: ">3.7.0" -> ">=3.7.1", not ">=3.8.0".
        """
        default = str(default) if default else None
        if self.lower_inclusive is None:
            return Version(default) if default else None

        return self.lower_inclusive

    def get_upper_exclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the exclusive upper bound of the version constraint.

        Returns effective upper bound in exclusive form (<). Inclusive bounds (<=)
        converted by incrementing micro version (e.g., "<=3.11.5" -> "<3.11.6").
        Multiple bounds return minimum (most restrictive).

        Args:
            default: Default version if no upper bound specified. Can be string
                (e.g., "4.0") or Version object. None if no bound and no default.

        Returns:
            Exclusive upper bound as Version, or None if no bound and no default.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_upper_exclusive()
            <Version('3.12')>
            >>> vc = VersionConstraint(">=3.8,<=3.11.5")
            >>> vc.get_upper_exclusive()  # <=3.11.5 becomes <3.11.6
            <Version('3.11.6')>

        Note:
            Conversion increments micro version: "<=3.11.5" -> "<3.11.6", not "<3.12.0".
        """
        default = str(default) if default else None
        if self.upper_exclusive is None:
            return Version(default) if default else None

        return self.upper_exclusive

    def get_upper_inclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the inclusive upper bound of the version constraint.

        Returns effective upper bound in inclusive form (<=). Exclusive bounds (<)
        converted by decrementing appropriate component:
        - micro > 0: Decrement micro ("<3.12.5" -> "<=3.12.4")
        - micro == 0, minor > 0: Decrement minor ("<3.12.0" -> "<=3.11")
        - micro == 0, minor == 0: Decrement major ("<4.0.0" -> "<=3")

        Args:
            default: Default version if no upper bound specified. Can be string or
                Version. Incremented by one micro before processing.

        Returns:
            Inclusive upper bound as Version, or None if no bound and no default.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12.5")
            >>> vc.get_upper_inclusive()  # <3.12.5 becomes <=3.12.4
            <Version('3.12.4')>
            >>> vc = VersionConstraint(">=3.8,<3.12.0")
            >>> vc.get_upper_inclusive()  # <3.12.0 becomes <=3.11
            <Version('3.11')>

        Note:
            Default incremented by one micro before use: "4.0" -> "4.0.1" -> "<=4.0.0".
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
        """Generate a list of versions within the constraint at specified precision.

        Creates list of all versions satisfying the constraint, incrementing at
        specified level. Useful for test matrices, listing supported versions, or
        iterating over ranges.

        Generates all possible versions between bounds at precision level, then
        filters to only include versions satisfying the original constraint.

        Args:
            level: Precision level for increments. Defaults to "major".
                - "major": Increment major (e.g., 3, 4, 5)
                - "minor": Increment minor (e.g., 3.8, 3.9, 3.10)
                - "micro": Increment micro (e.g., 3.8.1, 3.8.2, 3.8.3)
            lower_default: Default lower bound if constraint doesn't specify one.
                String or Version. Raises ValueError if None and no constraint bound.
            upper_default: Default upper bound if constraint doesn't specify one.
                String or Version. Raises ValueError if None and no constraint bound.

        Returns:
            List of Version objects satisfying constraint, sorted ascending. May be
            empty if no versions satisfy constraint.

        Raises:
            ValueError: If no lower or upper bound can be determined.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_version_range(level="minor")
            [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]
            >>> vc = VersionConstraint(">=3.10.1,<=3.10.3")
            >>> vc.get_version_range(level="micro")
            [<Version('3.10.1')>, <Version('3.10.2')>, <Version('3.10.3')>]

        Note:
            Generates all version combinations between bounds, then filters using
            constraint's contains() method. Handles complex constraints properly.
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

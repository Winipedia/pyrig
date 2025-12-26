"""Version constraint parsing and range generation utilities.

This module provides utilities for working with PEP 440 version specifiers and
constraints. It wraps the packaging library to provide convenient methods for
extracting version bounds and generating version ranges.

The main class VersionConstraint parses PEP 440 version specifier strings
(e.g., ">=3.8,<3.12") and provides methods to:

- Extract inclusive and exclusive lower and upper bounds
- Generate lists of versions within a constraint
- Adjust version precision (major/minor/micro)

Functions:
    adjust_version_to_level: Truncate a version to a specific precision level

Classes:
    VersionConstraint: Parser and analyzer for PEP 440 version constraints

Examples:
    Parse a version constraint and extract bounds::

        >>> from pyrig.dev.utils.versions import VersionConstraint
        >>> vc = VersionConstraint(">=3.8,<3.12")
        >>> vc.get_lower_inclusive()
        <Version('3.8')>
        >>> vc.get_upper_exclusive()
        <Version('3.12')>

    Generate a version range::

        >>> vc = VersionConstraint(">=3.8,<3.12")
        >>> versions = vc.get_version_range(level="minor")
        >>> print(versions)
        [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]

    Adjust version precision::

        >>> from pyrig.dev.utils.versions import adjust_version_to_level
        >>> from packaging.version import Version
        >>> adjust_version_to_level(Version("3.11.5"), "minor")
        <Version('3.11')>

See Also:
    packaging.specifiers: PEP 440 version specifier implementation
    packaging.version: PEP 440 version parsing and comparison
"""

from typing import Literal

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def adjust_version_to_level(
    version: Version, level: Literal["major", "minor", "micro"]
) -> Version:
    """Truncate a version to the specified precision level.

    Removes version components beyond the specified level. For example, truncating
    "3.11.5" to "minor" level produces "3.11", removing the micro component.

    Args:
        version: The version to truncate. Can be any packaging.version.Version object.
        level: The precision level to truncate to:

            - "major": Keep only major version (e.g., "3.11.5" -> "3")
            - "minor": Keep major and minor (e.g., "3.11.5" -> "3.11")
            - "micro": Keep all components (e.g., "3.11.5" -> "3.11.5", no change)

    Returns:
        A new Version object with components beyond the specified level removed.
        The original version object is not modified.

    Examples:
        Truncate to major version::

            >>> from pyrig.dev.utils.versions import adjust_version_to_level
            >>> from packaging.version import Version
            >>> adjust_version_to_level(Version("3.11.5"), "major")
            <Version('3')>

        Truncate to minor version::

            >>> adjust_version_to_level(Version("3.11.5"), "minor")
            <Version('3.11')>

        Micro level returns the version unchanged::

            >>> adjust_version_to_level(Version("3.11.5"), "micro")
            <Version('3.11.5')>

    Note:
        This function only handles the major, minor, and micro components. Pre-release,
        post-release, dev, and local version identifiers are always removed.
    """
    if level == "major":
        return Version(f"{version.major}")
    if level == "minor":
        return Version(f"{version.major}.{version.minor}")
    return version


class VersionConstraint:
    """Parser and analyzer for PEP 440 version constraints.

    Parses version specifier strings (e.g., ">=3.8,<3.12") and provides methods
    to extract bounds and generate version ranges. Handles both inclusive and
    exclusive bounds, converting between them as needed.

    The class automatically normalizes all bounds to both inclusive and exclusive
    forms by incrementing/decrementing the micro version component. For example:

    - ">3.7.0" is converted to ">=3.7.1" (exclusive to inclusive)
    - "<=3.11.5" is converted to "<3.11.6" (inclusive to exclusive)

    Attributes:
        constraint (str): The original constraint string as provided to __init__.
        spec (str): The cleaned specifier string with quotes and whitespace stripped.
        sset (SpecifierSet): The parsed SpecifierSet from the packaging library.
        lowers_inclusive (list[Version]): All lower bounds converted to inclusive form.
        lowers_exclusive (list[Version]): All lower bounds in exclusive form.
        lowers_exclusive_to_inclusive (list[Version]): Exclusive lower bounds converted
            to inclusive by incrementing micro version.
        uppers_inclusive (list[Version]): All upper bounds in inclusive form.
        uppers_exclusive (list[Version]): All upper bounds converted to exclusive form.
        uppers_inclusive_to_exclusive (list[Version]): Inclusive upper bounds converted
            to exclusive by incrementing micro version.
        lower_inclusive (Version | None): The effective lower bound (inclusive), which
            is the maximum of all lower bounds.
        upper_exclusive (Version | None): The effective upper bound (exclusive), which
            is the minimum of all upper bounds.

    Examples:
        Parse a version constraint and extract bounds::

            >>> from pyrig.dev.utils.versions import VersionConstraint
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.get_lower_inclusive()
            <Version('3.8')>
            >>> vc.get_upper_exclusive()
            <Version('3.12')>

        Generate a version range::

            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> versions = vc.get_version_range(level="minor")
            >>> print(versions)
            [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>]

        Handle exclusive bounds::

            >>> vc = VersionConstraint(">3.7.5,<=3.11.2")
            >>> vc.get_lower_inclusive()  # >3.7.5 becomes >=3.7.6
            <Version('3.7.6')>
            >>> vc.get_upper_exclusive()  # <=3.11.2 becomes <3.11.3
            <Version('3.11.3')>

    Note:
        The class assumes all version components are non-negative integers. It
        handles conversion between inclusive and exclusive bounds by incrementing
        or decrementing the micro version component.
    """

    def __init__(self, constraint: str) -> None:
        """Initialize a VersionConstraint from a PEP 440 specifier string.

        Parses the constraint string and computes all inclusive and exclusive
        bounds. The constraint string can contain multiple specifiers separated
        by commas (e.g., ">=3.8,<3.12").

        Args:
            constraint: A PEP 440 version specifier string. Examples:

                - ">=3.8,<3.12" (inclusive lower, exclusive upper)
                - ">3.7,<=3.11" (exclusive lower, inclusive upper)
                - ">=3.8" (only lower bound)
                - "<4.0" (only upper bound)

                The string can be quoted or unquoted. Quotes and surrounding
                whitespace are automatically stripped.

        Examples:
            Create a version constraint::

                >>> from pyrig.dev.utils.versions import VersionConstraint
                >>> vc = VersionConstraint(">=3.8,<3.12")
                >>> print(vc.lower_inclusive)
                3.8
                >>> print(vc.upper_exclusive)
                3.12

            Handle quoted constraints::

                >>> vc = VersionConstraint('">=3.8,<3.12"')
                >>> print(vc.spec)
                >=3.8,<3.12
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

        Returns the effective lower bound in inclusive form (>=). If the constraint
        specifies an exclusive lower bound (>), it is automatically converted to
        inclusive by incrementing the micro version. For example, ">3.7.0" becomes
        ">=3.7.1".

        If multiple lower bounds are specified, returns the maximum (most restrictive)
        bound.

        Args:
            default: Default version to return if no lower bound is specified in the
                constraint. Can be a string (e.g., "3.8") or a Version object. If
                None and no lower bound exists, returns None.

        Returns:
            The inclusive lower bound as a Version object, or None if no lower bound
            exists and no default is provided. If a default is provided and no lower
            bound exists in the constraint, returns the default as a Version object.

        Examples:
            Get inclusive lower bound from inclusive constraint::

                >>> from pyrig.dev.utils.versions import VersionConstraint
                >>> vc = VersionConstraint(">=3.8,<3.12")
                >>> vc.get_lower_inclusive()
                <Version('3.8')>

            Get inclusive lower bound from exclusive constraint::

                >>> vc = VersionConstraint(">3.7.5,<3.12")
                >>> vc.get_lower_inclusive()  # >3.7.5 becomes >=3.7.6
                <Version('3.7.6')>

            Use default when no lower bound exists::

                >>> vc = VersionConstraint("<3.12")
                >>> vc.get_lower_inclusive(default="3.8")
                <Version('3.8')>

            Return None when no lower bound and no default::

                >>> vc = VersionConstraint("<3.12")
                >>> vc.get_lower_inclusive()
                None

        Note:
            The conversion from exclusive to inclusive is done by incrementing the
            micro version component. This means ">3.7.0" becomes ">=3.7.1", not
            ">=3.8.0".
        """
        default = str(default) if default else None
        if self.lower_inclusive is None:
            return Version(default) if default else None

        return self.lower_inclusive

    def get_upper_exclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the exclusive upper bound of the version constraint.

        Returns the effective upper bound in exclusive form (<). If the constraint
        specifies an inclusive upper bound (<=), it is automatically converted to
        exclusive by incrementing the micro version. For example, "<=3.11.5" becomes
        "<3.11.6".

        If multiple upper bounds are specified, returns the minimum (most restrictive)
        bound.

        Args:
            default: Default version to return if no upper bound is specified in the
                constraint. Can be a string (e.g., "4.0") or a Version object. If
                None and no upper bound exists, returns None.

        Returns:
            The exclusive upper bound as a Version object, or None if no upper bound
            exists and no default is provided. If a default is provided and no upper
            bound exists in the constraint, returns the default as a Version object.

        Examples:
            Get exclusive upper bound from exclusive constraint::

                >>> from pyrig.dev.utils.versions import VersionConstraint
                >>> vc = VersionConstraint(">=3.8,<3.12")
                >>> vc.get_upper_exclusive()
                <Version('3.12')>

            Get exclusive upper bound from inclusive constraint::

                >>> vc = VersionConstraint(">=3.8,<=3.11.5")
                >>> vc.get_upper_exclusive()  # <=3.11.5 becomes <3.11.6
                <Version('3.11.6')>

            Use default when no upper bound exists::

                >>> vc = VersionConstraint(">=3.8")
                >>> vc.get_upper_exclusive(default="4.0")
                <Version('4.0')>

            Return None when no upper bound and no default::

                >>> vc = VersionConstraint(">=3.8")
                >>> vc.get_upper_exclusive()
                None

        Note:
            The conversion from inclusive to exclusive is done by incrementing the
            micro version component. This means "<=3.11.5" becomes "<3.11.6", not
            "<3.12.0".
        """
        default = str(default) if default else None
        if self.upper_exclusive is None:
            return Version(default) if default else None

        return self.upper_exclusive

    def get_upper_inclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the inclusive upper bound of the version constraint.

        Returns the effective upper bound in inclusive form (<=). If the constraint
        specifies an exclusive upper bound (<), it is automatically converted to
        inclusive by decrementing the appropriate version component.

        The decrementing logic works as follows:

        - If micro > 0: Decrement micro (e.g., "<3.12.5" -> "<=3.12.4")
        - If micro == 0 and minor > 0: Decrement minor (e.g., "<3.12.0" -> "<=3.11")
        - If micro == 0 and minor == 0: Decrement major (e.g., "<4.0.0" -> "<=3")

        Args:
            default: Default version to return if no upper bound is specified in the
                constraint. Can be a string (e.g., "4.0") or a Version object. The
                default is automatically incremented by one micro version to convert
                it to an exclusive bound internally before processing.

        Returns:
            The inclusive upper bound as a Version object, or None if no upper bound
            exists and no default is provided. If a default is provided and no upper
            bound exists in the constraint, returns the default converted to inclusive
            form.

        Examples:
            Get inclusive upper bound from exclusive constraint with non-zero micro::

                >>> from pyrig.dev.utils.versions import VersionConstraint
                >>> vc = VersionConstraint(">=3.8,<3.12.5")
                >>> vc.get_upper_inclusive()  # <3.12.5 becomes <=3.12.4
                <Version('3.12.4')>

            Get inclusive upper bound from exclusive constraint with zero micro::

                >>> vc = VersionConstraint(">=3.8,<3.12.0")
                >>> vc.get_upper_inclusive()  # <3.12.0 becomes <=3.11
                <Version('3.11')>

            Get inclusive upper bound from inclusive constraint::

                >>> vc = VersionConstraint(">=3.8,<=3.11.5")
                >>> vc.get_upper_inclusive()
                <Version('3.11.5')>

            Use default when no upper bound exists::

                >>> vc = VersionConstraint(">=3.8")
                >>> vc.get_upper_inclusive(default="4.0")
                <Version('4.0')>

        Note:
            The default parameter is incremented by one micro version before being
            used, so a default of "4.0" is treated as "4.0.1" internally, which
            then converts to "<=4.0.0" in inclusive form.
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

        Creates a list of all versions that satisfy the constraint, incrementing at
        the specified level (major, minor, or micro). This is useful for generating
        test matrices, listing supported versions, or iterating over version ranges.

        The method generates all possible versions between the lower and upper bounds
        at the specified precision level, then filters them to only include versions
        that satisfy the original constraint.

        Args:
            level: The precision level for version increments. Defaults to "major".

                - "major": Increment major version (e.g., 3, 4, 5)
                - "minor": Increment minor version (e.g., 3.8, 3.9, 3.10)
                - "micro": Increment micro version (e.g., 3.8.1, 3.8.2, 3.8.3)

            lower_default: Default lower bound if the constraint doesn't specify one.
                Can be a string (e.g., "3.8") or a Version object. If None and the
                constraint has no lower bound, raises ValueError.
            upper_default: Default upper bound if the constraint doesn't specify one.
                Can be a string (e.g., "4.0") or a Version object. If None and the
                constraint has no upper bound, raises ValueError.

        Returns:
            A list of Version objects satisfying the constraint, sorted in ascending
            order. Only versions that pass the constraint's contains() check are
            included. The list may be empty if no versions satisfy the constraint.

        Raises:
            ValueError: If no lower or upper bound can be determined (either from
                the constraint or the provided defaults). The error message will be:
                "No lower or upper bound. Please specify default values."

        Examples:
            Generate minor version range::

                >>> from pyrig.dev.utils.versions import VersionConstraint
                >>> vc = VersionConstraint(">=3.8,<3.12")
                >>> vc.get_version_range(level="minor")
                [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>,
                 <Version('3.11')>]

            Generate major version range::

                >>> vc = VersionConstraint(">=3.8,<4.0")
                >>> vc.get_version_range(level="major")
                [<Version('3')>]

            Generate micro version range::

                >>> vc = VersionConstraint(">=3.10.1,<=3.10.3")
                >>> vc.get_version_range(level="micro")
                [<Version('3.10.1')>, <Version('3.10.2')>,
                 <Version('3.10.3')>]

            Use defaults for unbounded constraints::

                >>> vc = VersionConstraint(">=3.8")
                >>> vc.get_version_range(
                ...     level="minor",
                ...     upper_default="3.12"
                ... )
                [<Version('3.8')>, <Version('3.9')>, <Version('3.10')>,
                 <Version('3.11')>]

            Handle constraints with no matching versions::

                >>> vc = VersionConstraint(">=3.12,<3.8")
                >>> vc.get_version_range(level="minor")
                []

        Note:
            The method generates all possible version combinations between the bounds
            and then filters them using the constraint's contains() method. This
            ensures that complex constraints (e.g., ">=3.8,!=3.9.0,<3.12") are
            properly handled.
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

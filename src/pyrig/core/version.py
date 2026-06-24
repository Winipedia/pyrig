"""Version constraint parsing and range generation utilities.

Provides tools for working with PEP 440 version specifiers, including
extracting inclusive and exclusive bounds from a constraint string and
enumerating all versions within a range at a specified precision level.
"""

from typing import Literal

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def adjust_version_to_level(
    version: Version, level: Literal["major", "minor", "micro"]
) -> Version:
    """Truncate a version to the specified precision level.

    Args:
        version: The version to truncate.
        level: Precision level:
            - ``"major"``: Keep only the major component (e.g., ``"3.11.5"`` → ``"3"``).
            - ``"minor"``: Keep major and minor (e.g., ``"3.11.5"`` → ``"3.11"``).
            - ``"micro"``: Return the version unchanged.

    Returns:
        A new ``Version`` with components beyond the specified level removed.
        Pre-release and other suffixes are stripped for ``"major"`` and ``"minor"``.
        For ``"micro"``, the original ``Version`` object is returned as-is.

    Examples:
        >>> adjust_version_to_level(Version("3.11.5"), "major")
        <Version('3')>
        >>> adjust_version_to_level(Version("3.11.5"), "minor")
        <Version('3.11')>
        >>> adjust_version_to_level(Version("3.11.5"), "micro")
        <Version('3.11.5')>
    """
    if level == "major":
        return Version(f"{version.major}")
    if level == "minor":
        return Version(f"{version.major}.{version.minor}")
    return version


class VersionConstraint:
    """Parser and analyzer for PEP 440 version constraints.

    Parses a specifier string such as ``">=3.8,<3.12"`` and exposes the effective
    inclusive lower bound and exclusive upper bound, as well as a method to generate
    all versions within the range at a given precision.

    Internally all bounds are normalized to a consistent form:

    - Exclusive lower bounds (``>``) are converted to inclusive (``>=``) by
      incrementing the micro component: ``">3.7.0"`` → ``">=3.7.1"``.
    - Inclusive upper bounds (``<=``) are converted to exclusive (``<``) by
      incrementing the micro component: ``"<=3.11.5"`` → ``"<3.11.6"``.
    - When multiple lower or upper bounds are present, the most restrictive one
      is used (maximum lower, minimum upper).

    Attributes:
        constraint (str): The original constraint string as provided.
        spec (str): The constraint with surrounding quotes and whitespace stripped.
        sset (SpecifierSet): Parsed ``SpecifierSet`` from the ``packaging`` library.
        lowers_inclusive (tuple[Version, ...]): All lower bounds in inclusive form,
            including exclusive bounds converted via micro increment.
        lowers_exclusive (tuple[Version, ...]): Lower bounds originally written as
            exclusive (``>``), before conversion.
        lowers_exclusive_to_inclusive (tuple[Version, ...]): Exclusive lower bounds
            converted to inclusive by incrementing the micro component.
        uppers_inclusive (tuple[Version, ...]): Upper bounds originally written as
            inclusive (``<=``), before conversion.
        uppers_exclusive (tuple[Version, ...]): All upper bounds in exclusive form,
            including inclusive bounds converted via micro increment.
        uppers_inclusive_to_exclusive (tuple[Version, ...]): Inclusive upper bounds
            converted to exclusive by incrementing the micro component.
        lower_inclusive (Version | None): The effective inclusive lower bound
            (maximum of all normalized lower bounds), or ``None`` if unspecified.
        upper_exclusive (Version | None): The effective exclusive upper bound
            (minimum of all normalized upper bounds), or ``None`` if unspecified.

    Examples:
        >>> vc = VersionConstraint(">=3.8,<3.12")
        >>> vc.find_lower_inclusive()
        <Version('3.8')>
        >>> vc.version_range(level="minor")
        (<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>)
    """

    def __init__(self, constraint: str) -> None:
        """Initialize from a PEP 440 specifier string.

        Parses the constraint and precomputes all normalized inclusive and exclusive
        bounds. Supports multiple specifiers joined by commas (e.g., ``">=3.8,<3.12"``).
        Leading and trailing quotes and whitespace are stripped automatically.

        Args:
            constraint: A PEP 440 version specifier string. May be quoted or unquoted.
                Examples: ``">=3.8,<3.12"``, ``">3.7,<=3.11"``, ``">=3.8"``, ``"<4.0"``.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.lower_inclusive
            <Version('3.8')>
            >>> vc.upper_exclusive
            <Version('3.12')>
        """
        self.constraint = constraint
        self.spec = self.constraint.strip().strip('"').strip("'")
        self.sset = SpecifierSet(self.spec)

        self.lowers_inclusive = tuple(
            Version(s.version) for s in self.sset if s.operator == ">="
        )
        self.lowers_exclusive = tuple(
            Version(s.version) for s in self.sset if s.operator == ">"
        )
        # increment the last number of exclusive, so
        # >3.4.1 to >=3.4.2; <3.4.0 to <=3.4.1; 3.0.0 to <=3.0.1
        self.lowers_exclusive_to_inclusive = tuple(
            Version(f"{v.major}.{v.minor}.{v.micro + 1}") for v in self.lowers_exclusive
        )
        self.lowers_inclusive = (
            self.lowers_inclusive + self.lowers_exclusive_to_inclusive
        )

        self.uppers_inclusive = tuple(
            Version(s.version) for s in self.sset if s.operator == "<="
        )
        self.uppers_exclusive = tuple(
            Version(s.version) for s in self.sset if s.operator == "<"
        )

        # increment the last number of inclusive, so
        # <=3.4.1 to <3.4.2; >=3.4.0 to >3.4.1; 3.0.0 to >3.0.1
        self.uppers_inclusive_to_exclusive = tuple(
            Version(f"{v.major}.{v.minor}.{v.micro + 1}") for v in self.uppers_inclusive
        )
        self.uppers_exclusive = (
            self.uppers_inclusive_to_exclusive + self.uppers_exclusive
        )

        self.upper_exclusive = (
            min(self.uppers_exclusive) if self.uppers_exclusive else None
        )
        self.lower_inclusive = (
            max(self.lowers_inclusive) if self.lowers_inclusive else None
        )

    def version_range(
        self,
        level: Literal["major", "minor", "micro"] = "major",
        lower_default: str | Version | None = None,
        upper_default: str | Version | None = None,
    ) -> tuple[Version, ...]:
        """Enumerate all versions within the constraint at the specified precision.

        Generates every version between the effective lower and upper bounds,
        incrementing at the given precision level, then filters the candidates
        against the original specifier. This correctly handles complex constraints
        such as ``"!=3.9"`` or disjoint ranges.

        Args:
            level: Granularity of version increments. Defaults to ``"major"``.
                - ``"major"``: (e.g., ``3``, ``4``, ``5``).
                - ``"minor"``: (e.g., ``3.8``, ``3.9``, ``3.10``).
                - ``"micro"``: (e.g., ``3.8.1``, ``3.8.2``).
            lower_default: Fallback inclusive lower bound when the constraint
                provides none. Accepts a version string (e.g., ``"3.8"``)
                or a ``Version`` object.
            upper_default: Fallback inclusive upper bound when the constraint provides
                none. Accepts a version string or ``Version`` object.

        Returns:
            A tuple of ``Version`` objects satisfying the constraint, sorted ascending.
            May be empty if no versions satisfy the constraint.

        Raises:
            RuntimeError: If the constraint and defaults together fail to yield a
                lower bound, or fail to yield an upper bound.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.version_range(level="minor")
            (<Version('3.8')>, <Version('3.9')>, <Version('3.10')>, <Version('3.11')>)
            >>> vc = VersionConstraint(">=3.10.1,<=3.10.3")
            >>> vc.version_range(level="micro")
            (<Version('3.10.1')>, <Version('3.10.2')>, <Version('3.10.3')>)

        Note:
            Version candidates are generated from the component ranges of the
            inclusive bounds and then filtered by the original specifier set,
            so constraints like ``"!=3.9"`` or ``"~=3.8"`` are handled correctly.
        """
        lower = self.find_lower_inclusive(lower_default)
        upper = self.upper_inclusive(upper_default)

        if lower is None or upper is None:
            msg = "No lower or upper bound. Please specify default values."
            raise RuntimeError(msg)

        major_level, minor_level, micro_level = range(3)
        level_int = {"major": major_level, "minor": minor_level, "micro": micro_level}[
            level
        ]
        lower_as_tuple = (lower.major, lower.minor, lower.micro)
        upper_as_tuple = (upper.major, upper.minor, upper.micro)

        versions: list[list[int]] = []
        for major in range(
            lower_as_tuple[major_level], upper_as_tuple[major_level] + 1
        ):
            version = [major]

            minor_lower_og, minor_upper_og = (
                lower_as_tuple[minor_level],
                upper_as_tuple[minor_level],
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
                    lower_as_tuple[micro_level],
                    upper_as_tuple[micro_level],
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
        return tuple(v for v in version_versions if self.sset.contains(v))

    def upper_inclusive(self, default: str | Version | None = None) -> Version | None:
        """Get the inclusive upper bound of the constraint.

        Converts the exclusive upper bound (``<``) to an inclusive form (``<=``) by
        decrementing the appropriate version component:

        - ``micro > 0``: Decrement micro — ``"<3.12.5"`` → ``"<=3.12.4"``.
        - ``micro == 0`` and ``minor > 0``: Drop micro, decrement minor —
          ``"<3.12.0"`` → ``"<=3.11"``.
        - ``micro == 0`` and ``minor == 0``: Drop both, decrement major —
          ``"<4.0.0"`` → ``"<=3"``.

        Args:
            default: Inclusive upper bound to use when the constraint specifies no
                upper bound. Accepts a version string or ``Version`` object.

        Returns:
            The inclusive upper bound as a ``Version``, or ``None`` if no upper
            bound exists and no default was provided.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12.5")
            >>> vc.upper_inclusive()
            <Version('3.12.4')>
            >>> vc = VersionConstraint(">=3.8,<3.12.0")
            >>> vc.upper_inclusive()
            <Version('3.11')>
            >>> vc = VersionConstraint(">=2.8,<3.0.0")
            >>> vc.upper_inclusive()
            <Version('2')>
        """
        # increment the default by 1 micro to make it exclusive
        if default:
            default = Version(str(default))
            default = Version(f"{default.major}.{default.minor}.{default.micro + 1}")
        upper_exclusive = self.find_upper_exclusive(default)
        if upper_exclusive is None:
            return None

        major, minor, micro = (
            upper_exclusive.major,
            upper_exclusive.minor,
            upper_exclusive.micro,
        )
        if micro != 0:
            return Version(f"{major}.{minor}.{micro - 1}")
        if minor != 0:
            return Version(f"{major}.{minor - 1}")
        return Version(f"{major - 1}")

    def find_lower_inclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the effective inclusive lower bound of the constraint.

        Exclusive lower bounds (``>``) are converted to inclusive (``>=``) by
        incrementing the micro component: ``">3.7.0"`` → ``">=3.7.1"``. When
        multiple lower bounds are present, the most restrictive (maximum) is returned.

        Args:
            default: Inclusive lower bound to use when the constraint specifies none.
                Accepts a version string (e.g., ``"3.8"``) or a ``Version`` object.

        Returns:
            The inclusive lower bound as a ``Version``, or ``None`` if no lower
            bound exists and no default was provided.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.find_lower_inclusive()
            <Version('3.8')>
            >>> vc = VersionConstraint(">3.7.5,<3.12")
            >>> vc.find_lower_inclusive()
            <Version('3.7.6')>
            >>> vc = VersionConstraint("<3.12")
            >>> vc.find_lower_inclusive() is None
            True
            >>> vc.find_lower_inclusive("3.8")
            <Version('3.8')>
        """
        default = str(default) if default else None
        if self.lower_inclusive is None:
            return Version(default) if default else None

        return self.lower_inclusive

    def find_upper_exclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the effective exclusive upper bound of the constraint.

        Inclusive upper bounds (``<=``) are converted to exclusive (``<``) by
        incrementing the micro component: ``"<=3.11.5"`` → ``"<3.11.6"``. When
        multiple upper bounds are present, the most restrictive (minimum) is returned.

        Args:
            default: Exclusive upper bound to use when the constraint specifies none.
                Accepts a version string (e.g., ``"3.12"``) or a ``Version`` object.

        Returns:
            The exclusive upper bound as a ``Version``, or ``None`` if no upper
            bound exists and no default was provided.

        Examples:
            >>> vc = VersionConstraint(">=3.8,<3.12")
            >>> vc.find_upper_exclusive()
            <Version('3.12')>
            >>> vc = VersionConstraint(">=3.8,<=3.11.5")
            >>> vc.find_upper_exclusive()
            <Version('3.11.6')>
            >>> vc = VersionConstraint(">=3.8")
            >>> vc.find_upper_exclusive() is None
            True
            >>> vc.find_upper_exclusive("3.12")
            <Version('3.12')>
        """
        default = str(default) if default else None
        if self.upper_exclusive is None:
            return Version(default) if default else None

        return self.upper_exclusive

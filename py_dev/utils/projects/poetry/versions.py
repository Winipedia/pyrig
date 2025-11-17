"""Contains utilities for working with versions."""

from typing import Literal

from packaging.specifiers import SpecifierSet
from packaging.version import Version


class VersionConstraint:
    """Version class."""

    def __init__(self, constraint: str) -> None:
        """Initialize the version."""
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
        """Get the minimum version.

        Is given inclusive. E.g. >=3.8, <3.12 -> 3.8
        if >3.7, <3.12 -> 3.7.1

        E.g. >=3.8, <3.12 -> 3.8

        Args:
            default: The default value to return if there is no minimum version

        Returns:
            The minimum version
        """
        default = str(default) if default else None
        if self.lower_inclusive is None:
            return Version(default) if default else None

        return self.lower_inclusive

    def get_upper_exclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the maximum version.

        Is given exclusive. E.g. >=3.8, <3.12 -> 3.12
        if >=3.8, <=3.12 -> 3.12.1

        Args:
            default: The default value to return if there is no maximum version

        Returns:
            The maximum version
        """
        default = str(default) if default else None
        if self.upper_exclusive is None:
            return Version(default) if default else None

        return self.upper_exclusive

    def get_upper_inclusive(
        self, default: str | Version | None = None
    ) -> Version | None:
        """Get the maximum version.

        Is given inclusive. E.g. >=3.8, <3.12 -> 3.11
        if >=3.8, <=3.12 -> 3.12

        Args:
            default: The default value to return if there is no maximum version

        Returns:
            The maximum version
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
        """Get the version range.

        returns a range of versions according to the level

        E.g. >=3.8, <3.12; level=major -> 3
            >=3.8, <4.12; level=major -> 3, 4
        E.g. >=3.8, <=3.12; level=minor -> 3.8, 3.9, 3.10, 3.11, 3.12
        E.g. >=3.8.1, <=4.12.1; level=micro -> 3.8.1, 3.8.2, ... 4.12.1

        Args:
            level: The level of the version to return
            lower_default: The default lower bound if none is specified
            upper_default: The default upper bound if none is specified

        Returns:
            A list of versions
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

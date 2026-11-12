"""Wrapper around Hypothesis for fuzz testing."""

from typing import override

from pyrig.rig.tools.base.tool import Group, Tool


class FuzzTester(Tool):
    """Tool metadata and dependency for fuzz testing via Hypothesis."""

    @override
    def dev_dependencies(self) -> tuple[str, ...]:
        """Return `('hypothesis', 'hypofuzz')`."""
        return (*super().dev_dependencies(), "hypofuzz")

    @override
    def group(self) -> str:
        """Return `Group.CODE_QUALITY`."""
        return Group.CODE_QUALITY

    @override
    def image_url(self) -> str:
        """Return the fuzz-testing badge image URL."""
        return f"https://img.shields.io/badge/fuzzing-{self.shield_name()}-blue"

    @override
    def link_url(self) -> str:
        """Return the hypothesis documentation URL."""
        return "https://hypothesis.readthedocs.io/en/latest/"

    @override
    def name(self) -> str:
        """Return `'hypothesis'`."""
        return "hypothesis"

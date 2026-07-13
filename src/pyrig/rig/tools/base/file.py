"""Shared contract for tools a prek hook invokes with a scoped subset of files."""

from abc import abstractmethod

from pyrig.rig.tools.base.tool import Tool


class FileTool(Tool):
    """Abstract base for a `Tool` that a prek hook invokes with specific files."""

    @abstractmethod
    def types(self) -> list[str]:
        """Return the list of file types that this tool can process."""

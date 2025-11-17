"""Build script.

All subclasses of Builder in the builds package are automatically called.
"""

from pathlib import Path

from py_dev.dev.artifacts.builder.base.base import Builder


class PydevBuilder(Builder):
    """Build script for PyDev."""

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Build the project."""
        paths = [temp_artifacts_dir / "build.txt"]
        for path in paths:
            path.write_text("Hello World!")

"""Build artifacts for the project."""

from py_dev.dev.artifacts.builder.base.base import Builder


def build() -> None:
    """Build all artifacts."""
    Builder.init_all_non_abstract_subclasses()

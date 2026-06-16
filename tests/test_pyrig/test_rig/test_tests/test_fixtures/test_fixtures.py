"""test module."""

from pyrig.rig.tests.fixtures import fixtures


def test_standard_output_error_template(standard_output_error_template: str) -> None:
    """Test function."""
    assert "{stdout}" in standard_output_error_template
    assert "{stderr}" in standard_output_error_template


def test_module_docstring() -> None:
    """Test function."""
    assert (
        fixtures.__doc__
        == """Shared pytest fixtures for pyrig and all projects built with it.

Fixtures defined here or any other file in the same package
are automatically discovered by pytest and made available to any pytest suite
that inherits from this project.
"""
    )

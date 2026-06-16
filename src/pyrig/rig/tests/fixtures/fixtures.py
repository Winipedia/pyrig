"""Shared pytest fixtures for pyrig and all projects built with it.

Fixtures defined here or any other file in the same package
are automatically discovered by pytest and made available to any pytest suite
that inherits from this project.
"""

import pytest


@pytest.fixture(scope="session")
def standard_output_error_template() -> str:
    """Provide a format string for displaying combined stdout and stderr output.

    Contains ``{stdout}`` and ``{stderr}`` placeholders, useful for producing
    clear assertion failure messages that include full process output.

    Returns:
        Format string with ``{stdout}`` and ``{stderr}`` placeholders.
    """
    return """The standard output:
{stdout}
--------------------------------------------------------------------------------
The standard error:
{stderr}"""

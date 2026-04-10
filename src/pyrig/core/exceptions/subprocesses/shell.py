"""Exceptions related to subprocesses running in shell mode."""


class ShellModeForbiddenError(Exception):
    """Raised when a subprocess is attempted to be run in shell mode."""

    def __init__(self) -> None:
        """Initialize the exception with a standard message."""
        msg = "Shell mode is forbidden in subprocesses for security reasons."
        super().__init__(msg)

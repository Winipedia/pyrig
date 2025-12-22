"""Configuration management for copying module docstrings.

This module provides the CopyModuleOnlyDocstringConfigFile class for
creating files that contain only the docstring from a source module.
"""

from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile


class CopyModuleOnlyDocstringConfigFile(CopyModuleConfigFile):
    """Config file that copies only the docstring from a module.

    Useful for creating stub files that preserve documentation
    but allow users to provide their own implementation.
    """

    @classmethod
    def get_content_str(cls) -> str:
        """Extract only the docstring from the source module.

        Returns:
            The module docstring wrapped in triple quotes.
        """
        content = super().get_content_str()
        parts = content.split('"""', 2)
        return '"""' + parts[1] + '"""\n'

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the file contains the source docstring.

        Returns:
            True if the docstring is present in the file.
        """
        docstring = cls.get_content_str().strip()
        # remove the triple quotes from the docstring
        docstring = docstring[3:-3]
        return docstring in cls.get_file_content() or super().is_correct()

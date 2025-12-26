r"""Configuration management for plain text files.

This module provides the TextConfigFile class for managing plain text
configuration files that have required content but allow user extensions.

TextConfigFile is designed for files where:
- A specific header or initial content is required
- Users can add additional content after the required part
- Content validation is done via substring matching (not exact match)
- User additions are preserved when updating

Common use cases:
- Python source files with required imports/boilerplate
- README.md files with required project header
- License files with required text
- Any text file with required starting content

The key difference from structured formats (TOML, YAML, JSON):
- Validation uses substring matching instead of structure comparison
- Dumping appends existing content instead of replacing it
- Content is stored as a single string, not a structured dict

Example:
    >>> from pathlib import Path
    >>> from pyrig.dev.configs.base.text import TextConfigFile
    >>>
    >>> class LicenseFile(TextConfigFile):
    ...     @classmethod
    ...     def get_parent_path(cls) -> Path:
    ...         return Path()
    ...
    ...     @classmethod
    ...     def get_content_str(cls) -> str:
    ...         return "MIT License\n\nCopyright (c) 2024"
    ...
    ...     @classmethod
    ...     def get_filename(cls) -> str:
    ...         return "LICENSE"
    ...
    ...     @classmethod
    ...     def get_file_extension(cls) -> str:
    ...         return ""
"""

from abc import abstractmethod
from typing import Any

from pyrig.dev.configs.base.base import ConfigFile


class TextConfigFile(ConfigFile):
    r"""Abstract base class for plain text configuration files.

    TextConfigFile provides a content-based validation system for text files
    that require specific content but allow user extensions. Unlike structured
    formats (TOML, YAML, JSON), validation is done via substring matching.

    Key Features:
        - **Content-based validation**: Checks if required content is present
          anywhere in the file (substring match)
        - **Preserves user additions**: Appends existing content when updating
        - **Flexible structure**: No rigid format requirements
        - **Simple interface**: Just implement get_content_str()

    Validation Behavior:
        A file is considered correct if:
        - It's empty (user opted out), OR
        - The required content (from get_content_str()) is present anywhere
          in the file

    Dump Behavior:
        When dumping:
        1. If file has existing content, append it to the required content
        2. Write the combined content to the file
        3. This preserves user additions while ensuring required content exists

    Attributes:
        CONTENT_KEY: Dictionary key used to store file content. Always "content".

    Subclasses must implement:
        - `get_parent_path`: Directory containing the text file
        - `get_content_str`: Required content that must be present
        - `get_file_extension`: File extension (can be empty string)

    Example:
        >>> from pathlib import Path
        >>> from pyrig.dev.configs.base.text import TextConfigFile
        >>>
        >>> class MyTextFile(TextConfigFile):
        ...     @classmethod
        ...     def get_parent_path(cls) -> Path:
        ...         return Path()
        ...
        ...     @classmethod
        ...     def get_content_str(cls) -> str:
        ...         return "# Required Header\n\nThis must be present."
        ...
        ...     @classmethod
        ...     def get_file_extension(cls) -> str:
        ...         return "txt"

    See Also:
        pyrig.dev.configs.base.python.PythonConfigFile: For .py files
        pyrig.dev.configs.base.markdown.MarkdownConfigFile: For .md files
    """

    CONTENT_KEY = "content"

    @classmethod
    @abstractmethod
    def get_content_str(cls) -> str:
        r"""Get the required content for this file.

        Subclasses must implement this to define what content must be present
        in the file. The content will be validated using substring matching,
        so it doesn't need to be the entire file content - just the required
        part.

        Returns:
            The content string that must be present somewhere in the file.

        Example:
            Required header::

                @classmethod
                def get_content_str(cls) -> str:
                    return "# My Project\n\nProject description."

            Required imports::

                @classmethod
                def get_content_str(cls) -> str:
                    return "from typing import Any\nimport sys"
        """

    @classmethod
    def load(cls) -> dict[str, str]:
        r"""Load the text file content.

        Reads the entire file as UTF-8 text and wraps it in a dict under
        CONTENT_KEY. This dict structure is used for consistency with other
        ConfigFile subclasses.

        Returns:
            Dict with a single key (CONTENT_KEY) containing the full file
            content as a string.

        Example:
            Load a text file::

                # myfile.txt contains:
                # Line 1
                # Line 2

                config = MyTextConfigFile.load()
                # Returns: {"content": "Line 1\nLine 2\n"}
        """
        return {cls.CONTENT_KEY: cls.get_path().read_text(encoding="utf-8")}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        r"""Write content to the text file, preserving user additions.

        This method implements a special behavior to preserve user additions:
        1. Checks if the file has existing content
        2. If yes, appends the existing content to the new content
        3. Writes the combined content to the file

        This ensures that:
        - Required content is always present at the start
        - User additions are preserved at the end
        - The file is never truncated

        Args:
            config: Dict containing the content to write under CONTENT_KEY.
                Must be a dict, not a list.

        Raises:
            TypeError: If config is not a dict. TextConfigFile requires a dict
                with CONTENT_KEY.

        Example:
            Initial dump::

                config = {"content": "# Required Header\n"}
                MyTextConfigFile.dump(config)
                # File contains: "# Required Header\n"

            User adds content::

                # User manually edits file to add:
                # "# Required Header\n\nUser addition\n"

            Subsequent dump::

                config = {"content": "# Required Header\n"}
                MyTextConfigFile.dump(config)
                # File contains: "# Required Header\n\nUser addition\n"
                # User addition is preserved!

        Note:
            This behavior is different from structured formats (TOML, YAML)
            which merge configurations. TextConfigFile simply appends.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to text file."
            raise TypeError(msg)
        if cls.get_file_content().strip():
            config[cls.CONTENT_KEY] = (
                config[cls.CONTENT_KEY] + "\n" + cls.get_file_content()
            )
        cls.get_path().write_text(config[cls.CONTENT_KEY], encoding="utf-8")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        r"""Get the expected configuration structure.

        Returns a dict with the required content under CONTENT_KEY. This is
        used by the ConfigFile validation system to check if the file is
        correct.

        Returns:
            Dict with a single key (CONTENT_KEY) containing the required
            content from get_content_str().

        Example:
            Expected configuration::

                @classmethod
                def get_content_str(cls) -> str:
                    return "# Header\n"

                config = cls.get_configs()
                # Returns: {"content": "# Header\n"}
        """
        return {cls.CONTENT_KEY: cls.get_content_str()}

    @classmethod
    def is_correct(cls) -> bool:
        r"""Check if the text file contains the required content.

        Overrides the base ConfigFile.is_correct() to use substring matching
        instead of structure comparison. A file is correct if:
        - It's empty (user opted out), OR
        - The base validation passes (exact match), OR
        - The required content is present anywhere in the file (substring match)

        The substring matching is the key difference from structured formats.
        This allows users to add content before or after the required content.

        Returns:
            True if the required content is present anywhere in the file, or
            if the file is empty (opted out).

        Example:
            Required content::

                get_content_str() -> "# Header\n"

            Valid files::

                ""  # Empty (opted out)
                "# Header\n"  # Exact match
                "# Header\n\nExtra content"  # Required + extra
                "Prefix\n# Header\n"  # Prefix + required

            Invalid files::

                "# Different Header\n"  # Missing required content
                "Header"  # Missing newline (not exact substring)
        """
        return (
            super().is_correct()
            or cls.get_content_str().strip() in cls.load()[cls.CONTENT_KEY]
        )

    @classmethod
    def get_file_content(cls) -> str:
        r"""Get the current file content.

        Convenience method to get the file content as a string without the
        dict wrapper. Equivalent to cls.load()[cls.CONTENT_KEY].

        Returns:
            The full content of the file as a string.

        Example:
            Get file content::

                # myfile.txt contains:
                # Line 1
                # Line 2

                content = MyTextConfigFile.get_file_content()
                # Returns: "Line 1\nLine 2\n"
        """
        return cls.load()[cls.CONTENT_KEY]

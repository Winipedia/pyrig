"""Configuration base for files that contain only a copied module docstring.

Extends module-copying config infrastructure to restrict output to just
the docstring, rather than the full module source.
"""

from pyrig.core.introspection.modules import module_has_docstring
from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile


class CopyModuleOnlyDocstringConfigFile(CopyModuleConfigFile):
    """Base class for config files containing only a source module's docstring.

    Creates a Python file whose entire content is the triple-quoted docstring of
    a source module. Useful for scaffolding files like ``__init__.py`` that need
    a description without carrying over the full module source.

    This class overrides ``is_correct()`` to check whether the source module has a
    docstring, rather than comparing file content. As a result, ``validate()``
    skips regeneration as long as the source module has a docstring, regardless of
    what the file on disk currently contains.

    Subclasses must implement:
        - ``copy_module``: Return the source module whose docstring will be copied.
    """

    def lines(self) -> list[str]:
        """Return the source module's docstring as file content.

        The docstring is wrapped in triple quotes to form a valid Python
        module-level docstring. If the source module has no docstring,
        ``default_docstring()`` is used as the fallback.

        Returns:
            The triple-quoted docstring as a list of lines.
        """
        docstring = self.copy_module().__doc__ or self.default_docstring()
        return self.split_lines(f'"""{docstring}"""\n')

    def is_correct(self) -> bool:
        """Check if the source module has a docstring.

        Overrides the parent's content-based check. The file is considered correct
        when the source module has a docstring to provide. This means ``validate()``
        will not regenerate the file as long as the source module has a docstring,
        even if the file on disk is out of date.

        Returns:
            True if the source module has a docstring, False otherwise.
        """
        return module_has_docstring(self.copy_module())

    def default_docstring(self) -> str:
        """Return a placeholder docstring used when the source module has none.

        Returns:
            A generic placeholder string used as the module docstring.
        """
        return "Module description."

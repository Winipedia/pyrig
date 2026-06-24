"""Configuration base for files that contain only a copied module docstring.

Extends module-copying config infrastructure to restrict output to just
the docstring, rather than the full module source.
"""

from pyrig.core.introspection.modules import module_has_docstring
from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile


class CopyModuleDocstringConfigFile(CopyModuleConfigFile):
    """Base class for config files containing only a source module's docstring.

    Creates a Python file whose entire content is the triple-quoted docstring of
    a source module. Useful for scaffolding files like `__init__.py` that need
    a description without carrying over the full module source.

    Overrides `is_correct` to check only whether the source module has a
    docstring, rather than comparing file content. As a result, `validate`
    skips regeneration as long as the source module has a docstring, regardless of
    what the file on disk currently contains.

    Subclasses must implement:
        - `copy_module`: Return the source module whose docstring will be copied.
    """

    def lines(self) -> list[str]:
        """Return the source module's docstring as file content.

        The docstring is wrapped in triple quotes to form a valid Python
        module-level docstring. Double triple quotes are used by default;
        if the docstring itself already contains a double-triple-quote sequence,
        single triple quotes are used instead. If the source module has no
        docstring, the result of `default_docstring` is used as the fallback.

        Returns:
            The triple-quoted docstring split into individual lines, with a
            trailing empty string from the final newline.
        """
        docstring = self.copy_module().__doc__ or self.default_docstring()
        double_triple_quotes, single_triple_quotes = '"""', "'''"
        triple_quotes = (
            double_triple_quotes
            if double_triple_quotes not in docstring
            else single_triple_quotes
        )
        return self.split_lines(f"{triple_quotes}{docstring}{triple_quotes}\n")

    def is_correct(self) -> bool:
        """Check whether the source module has a docstring.

        Overrides the parent's content-based check. The file is considered correct
        when the source module has a docstring to provide. This means `validate`
        will not regenerate the file as long as the source module has a docstring,
        even if the file on disk is out of date.

        Returns:
            `True` if the source module has a docstring, `False` otherwise.
        """
        return module_has_docstring(self.copy_module())

    def default_docstring(self) -> str:
        """Return a placeholder docstring used when the source module has none.

        Returns:
            A generic placeholder string used as the module docstring.
        """
        return "Module description."

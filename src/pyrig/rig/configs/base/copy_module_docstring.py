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

    The file is considered correct whenever the source module has a docstring,
    regardless of what is currently on disk.

    Subclasses must implement:
        - `copy_module`: Return the source module whose docstring will be copied.
    """

    def is_correct(self) -> bool:
        """Return `True` if the source module has a docstring, `False` otherwise."""
        return module_has_docstring(self.copy_module())

    def lines(self) -> list[str]:
        """Return the source module's docstring as file content.

        The docstring is wrapped in triple quotes to form a valid Python
        module-level docstring. Double triple quotes are used unless the docstring
        already contains a double-triple-quote sequence, in which case single
        triple quotes are used instead. If the source module has no docstring,
        `default_docstring` provides the fallback content.

        Returns:
            Lines forming a valid Python module-level docstring.
        """
        docstring = self.copy_module().__doc__ or self.default_docstring()
        double_triple_quotes, single_triple_quotes = '"""', "'''"
        triple_quotes = (
            double_triple_quotes
            if double_triple_quotes not in docstring
            else single_triple_quotes
        )
        return self.split_lines(f"{triple_quotes}{docstring}{triple_quotes}\n")

    def default_docstring(self) -> str:
        """Return the default module docstring `"Module description."`."""
        return "Module description."

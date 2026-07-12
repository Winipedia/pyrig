"""Configuration base for files that contain only a copied module docstring.

Extends module-copying config infrastructure to restrict output to just
the docstring, rather than the full module source.
"""

import ast

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

    def content(self) -> str:
        """Return the source module's docstring as file content.

        Rendered via `ast.unparse`, which picks a quote style that avoids
        escaping when possible and falls back to escaping otherwise, so the
        result is always a valid Python module-level docstring regardless of
        what quote characters the docstring itself contains. If the source
        module has no docstring, `default_docstring` provides the fallback
        content.

        Returns:
            A valid Python module-level docstring.
        """
        docstring = self.copy_module().__doc__ or self.default_docstring()
        module = ast.Module(
            body=[ast.Expr(value=ast.Constant(value=docstring))],
            type_ignores=[],
        )
        return f"{ast.unparse(module)}\n"

    def is_correct(self) -> bool:
        """Return `True` if the source module has a docstring, `False` otherwise."""
        return module_has_docstring(self.copy_module())

    def default_docstring(self) -> str:
        """Return the default module docstring `"Module description."`."""
        return "Module description."

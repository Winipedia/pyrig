"""Config File subclass that creates the builds dir and a build.py."""

from pathlib import Path

from pyrig.dev.artifacts import builder
from pyrig.dev.configs.base.base import PythonPackageConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.utils.modules.module import to_path


class BuilderConfigFile(PythonPackageConfigFile):
    """Config File subclass that creates the dirs folder."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        src_package = PyprojectConfigFile.get_package_name()
        builds_package = cls.get_module_name_replacing_start_module(
            builder, src_package
        )
        return to_path(builds_package, is_package=True)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the content."""
        return '''"""Build script.

All subclasses of Builder in the builds package are automatically called.
"""
'''

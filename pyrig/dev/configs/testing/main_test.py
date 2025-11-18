"""Has the test for main in src."""

from pathlib import Path

from pyrig import main
from pyrig.dev.configs.base.base import PythonPackageConfigFile
from pyrig.src.modules.module import to_path
from pyrig.src.testing.convention import make_test_obj_importpath_from_obj


class MainTestConfigFile(PythonPackageConfigFile):
    """Config file for test_main.py."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return to_path(make_test_obj_importpath_from_obj(main), is_package=False).parent

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config."""
        return '''"""test module."""

from pyrig.src.modules.package import get_src_package
from pyrig.src.os.os import run_subprocess


def test_main() -> None:
    """Test func for main."""
    project_name = get_src_package().__name__
    stdout = run_subprocess(["poetry", "run", project_name, "--help"]).stdout.decode(
        "utf-8"
    )
    assert "main" in stdout.lower()
'''

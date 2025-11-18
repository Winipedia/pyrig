"""Build utilities for creating and managing project builds.

This module provides functions for building and managing project artifacts,
including creating build scripts, configuring build environments, and
handling build dependencies. These utilities help with the packaging and
distribution of project code.
"""

import os
import platform
import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image

import pyrig
from pyrig import main
from pyrig.dev import artifacts
from pyrig.dev.artifacts import builder
from pyrig.dev.configs.base.base import ConfigFile
from pyrig.dev.configs.pyproject import PyprojectConfigFile
from pyrig.src.modules.class_ import (
    get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep,
)
from pyrig.src.modules.module import (
    to_path,
)
from pyrig.src.modules.package import get_src_package


class Builder(ABC):
    """Base class for build scripts.

    Subclass this class and implement the get_artifacts method to create
    a build script for your project. The build method will be called
    automatically when the class is initialized. At the end of the file add
    if __name__ == "__main__":
        YourBuildClass()
    """

    ARTIFACTS_DIR_NAME = "dist"

    @classmethod
    @abstractmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Build the project.

        This method should create all artifacts in the given folder.

        Returns:
            None
        """

    @classmethod
    def __init__(cls) -> None:
        """Initialize the build script."""
        cls.build()

    @classmethod
    def get_artifacts_dir(cls) -> Path:
        """Get the artifacts directory."""
        return Path(cls.ARTIFACTS_DIR_NAME)

    @classmethod
    def build(cls) -> None:
        """Build the project.

        This method is called by the __init__ method.
        It takes all the files and renames them with -platform.system()
        and puts them in the artifacts folder.
        """
        with tempfile.TemporaryDirectory() as temp_build_dir:
            temp_dir_path = Path(temp_build_dir)
            temp_artifacts_dir = cls.get_temp_artifacts_path(temp_dir_path)
            cls.create_artifacts(temp_artifacts_dir)
            artifacts = cls.get_temp_artifacts(temp_artifacts_dir)
            cls.rename_artifacts(artifacts)

    @classmethod
    def rename_artifacts(cls, artifacts: list[Path]) -> None:
        """Rename the artifacts in a non temporary folder."""
        artifacts_dir = cls.get_artifacts_dir()
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        for artifact in artifacts:
            # rename the files with -platform.system()
            new_name = f"{artifact.stem}-{platform.system()}{artifact.suffix}"
            new_path = artifacts_dir / new_name
            shutil.move(str(artifact), str(new_path))

    @classmethod
    def get_temp_artifacts(cls, temp_artifacts_dir: Path) -> list[Path]:
        """Get the built artifacts."""
        paths = list(temp_artifacts_dir.glob("*"))
        if not paths:
            msg = f"Expected {temp_artifacts_dir} to contain files"
            raise FileNotFoundError(msg)
        return paths

    @classmethod
    def get_artifacts(cls) -> list[Path]:
        """Get the built artifacts."""
        return list(cls.get_artifacts_dir().glob("*"))

    @classmethod
    def get_temp_artifacts_path(cls, temp_dir: Path) -> Path:
        """Get the built artifacts."""
        path = temp_dir / cls.ARTIFACTS_DIR_NAME
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_non_abstract_subclasses(cls) -> list[type["Builder"]]:
        """Get all non-abstract subclasses of Builder."""
        return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
            cls, pyrig, builder
        )

    @classmethod
    def init_all_non_abstract_subclasses(cls) -> None:
        """Build all artifacts."""
        for builder_cls in cls.get_non_abstract_subclasses():
            builder_cls()

    @classmethod
    def get_app_name(cls) -> str:
        """Get the app name."""
        return PyprojectConfigFile.get_project_name()

    @classmethod
    def get_root_path(cls) -> Path:
        """Get the root path."""
        src_pkg = get_src_package()
        return to_path(src_pkg, is_package=True).resolve().parent

    @classmethod
    def get_main_path(cls) -> Path:
        """Get the main path."""
        return cls.get_src_pkg_path() / cls.get_main_path_from_src_pkg()

    @classmethod
    def get_src_pkg_path(cls) -> Path:
        """Get the src package path."""
        return cls.get_root_path() / PyprojectConfigFile.get_package_name()

    @classmethod
    def get_main_path_from_src_pkg(cls) -> Path:
        """Get the main path.

        The path to main from the src package.
        """
        return Path(main.__file__).relative_to(cls.get_src_pkg_path())


class PyInstallerBuilder(Builder):
    """Build the project with pyinstaller.

    Expects main.py in the src package.
    """

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Build the project with pyinstaller."""
        from PyInstaller.__main__ import run  # noqa: PLC0415

        options = cls.get_pyinstaller_options(temp_artifacts_dir)
        run(options)

    @classmethod
    @abstractmethod
    def get_add_datas(cls) -> list[tuple[Path, Path]]:
        """Get the add data paths.

        Returns:
            list[tuple[Path, Path]]: List of tuples with the source path
                and the destination path.
        """

    @classmethod
    def get_pyinstaller_options(cls, temp_artifacts_dir: Path) -> list[str]:
        """Get the pyinstaller options."""
        temp_dir = temp_artifacts_dir.parent

        options = [
            str(cls.get_main_path()),
            "--name",
            cls.get_app_name(),
            "--clean",
            "--noconfirm",
            "--onefile",
            "--noconsole",
            "--workpath",
            str(cls.get_temp_workpath(temp_dir)),
            "--specpath",
            str(cls.get_temp_specpath(temp_dir)),
            "--distpath",
            str(cls.get_temp_distpath(temp_dir)),
            "--icon",
            str(cls.get_app_icon_path(temp_dir)),
        ]
        for src, dest in cls.get_add_datas():
            options.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
        return options

    @classmethod
    def get_temp_distpath(cls, temp_dir: Path) -> Path:
        """Get the distpath option."""
        return cls.get_temp_artifacts_path(temp_dir)

    @classmethod
    def get_temp_workpath(cls, temp_dir: Path) -> Path:
        """Get the workpath option."""
        path = temp_dir / "workpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_temp_specpath(cls, temp_dir: Path) -> Path:
        """Get the specpath option."""
        path = temp_dir / "specpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_app_icon_path(cls, temp_dir: Path) -> Path:
        """Get the app icon path."""
        if platform.system() == "Windows":
            return cls.convert_png_to_format("ico", temp_dir)
        if platform.system() == "Darwin":
            return cls.convert_png_to_format("icns", temp_dir)
        return cls.convert_png_to_format("png", temp_dir)

    @classmethod
    def convert_png_to_format(cls, file_format: str, temp_dir_path: Path) -> Path:
        """Convert a png to a format."""
        output_path = temp_dir_path / f"icon.{file_format}"
        png_path = cls.get_app_icon_png_path()
        img = Image.open(png_path)
        img.save(output_path, format=file_format.upper())
        return output_path

    @classmethod
    def get_app_icon_png_path(cls) -> Path:
        """Get the app icon path.

        Default is under dev/artifacts folder as icon.png
        You can override this method to change the icon location.
        """
        artifacts_path = to_path(
            ConfigFile.get_module_name_replacing_start_module(
                artifacts, PyprojectConfigFile.get_package_name()
            ),
            is_package=True,
        )
        return cls.get_root_path() / artifacts_path / "icon.png"

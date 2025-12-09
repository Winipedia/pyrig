"""PyInstaller-based artifact builder.

This module provides the PyInstallerBuilder class for creating
standalone executables from pyrig projects using PyInstaller.
"""

import os
import platform
from abc import abstractmethod
from pathlib import Path
from types import ModuleType

from PIL import Image

import pyrig
from pyrig.dev.artifacts import resources
from pyrig.dev.artifacts.builders.base.base import Builder
from pyrig.src.modules.module import get_same_modules_from_deps_depen_on_dep


class PyInstallerBuilder(Builder):
    """Abstract builder for creating PyInstaller executables.

    Subclass this to create standalone executables from your project.
    The builder handles icon conversion, resource bundling, and
    platform-specific configuration.

    Subclasses must implement:
        - ``get_additional_resource_pkgs``: Return packages containing resources

    The builder automatically includes:
        - All resources from dev/artifacts/resources directories
        - Resources from all packages depending on pyrig
        - Platform-appropriate icon format (ico/icns/png)

    Example:
        class MyAppBuilder(PyInstallerBuilder):
            @classmethod
            def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                return [my_app.resources]
    """

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Build a PyInstaller executable.

        Args:
            temp_artifacts_dir: Directory where the executable will be created.
        """
        from PyInstaller.__main__ import run  # noqa: PLC0415

        options = cls.get_pyinstaller_options(temp_artifacts_dir)
        run(options)

    @classmethod
    @abstractmethod
    def get_additional_resource_pkgs(cls) -> list[ModuleType]:
        """Return packages containing additional resources to bundle.

        Override this method to specify packages whose contents should
        be included in the executable. All files in these packages will
        be bundled and accessible at runtime.

        Returns:
            List of module objects representing resource packages.

        Note:
            The dev/artifacts/resources package and resources from all
            pyrig-dependent packages are included automatically.
        """

    @classmethod
    def get_default_additional_resource_pkgs(cls) -> list[ModuleType]:
        """Get resource packages from all pyrig-dependent packages.

        Returns:
            List of resources modules from packages depending on pyrig.
        """
        return get_same_modules_from_deps_depen_on_dep(resources, pyrig)

    @classmethod
    def get_all_resource_pkgs(cls) -> list[ModuleType]:
        """Get all resource packages to bundle.

        Returns:
            Combined list of default and additional resource packages.
        """
        return [
            *cls.get_default_additional_resource_pkgs(),
            *cls.get_additional_resource_pkgs(),
        ]

    @classmethod
    def get_add_datas(cls) -> list[tuple[Path, Path]]:
        """Build the --add-data arguments for PyInstaller.

        Traverses all resource packages and creates source/destination
        path pairs for bundling.

        Returns:
            List of (source_path, destination_path) tuples.
        """
        add_datas: list[tuple[Path, Path]] = []
        resources_pkgs = cls.get_all_resource_pkgs()
        for pkg in resources_pkgs:
            pkg_path = Path(pkg.__path__[0])
            # get the root of the pkg, which will be
            # the path remove suufix get_resources_path_from_src_pkg
            pkg_root = Path(
                pkg_path.as_posix().removesuffix(
                    cls.get_resources_path_from_src_pkg().as_posix()
                )
            ).parent
            for path in [pkg_path, *pkg_path.rglob("*")]:
                if path.is_file():
                    continue
                dest = path.relative_to(pkg_root)
                add_datas.append((path, dest))
        return add_datas

    @classmethod
    def get_pyinstaller_options(cls, temp_artifacts_dir: Path) -> list[str]:
        """Build the complete PyInstaller command-line options.

        Args:
            temp_artifacts_dir: Directory for build output.

        Returns:
            List of command-line arguments for PyInstaller.
        """
        temp_dir = temp_artifacts_dir.parent

        options = [
            str(cls.get_call_main_path()),
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
        """Get the temporary distribution output path.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path to the dist subdirectory.
        """
        return cls.get_temp_artifacts_path(temp_dir)

    @classmethod
    def get_temp_workpath(cls, temp_dir: Path) -> Path:
        """Get the temporary work directory for PyInstaller.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path to the workpath subdirectory.
        """
        path = temp_dir / "workpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_temp_specpath(cls, temp_dir: Path) -> Path:
        """Get the temporary spec file directory.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path to the specpath subdirectory.
        """
        path = temp_dir / "specpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_app_icon_path(cls, temp_dir: Path) -> Path:
        """Get the platform-appropriate icon path.

        Converts the PNG icon to the appropriate format for the
        current platform (ico for Windows, icns for macOS).

        Args:
            temp_dir: Directory for the converted icon file.

        Returns:
            Path to the converted icon file.
        """
        if platform.system() == "Windows":
            return cls.convert_png_to_format("ico", temp_dir)
        if platform.system() == "Darwin":
            return cls.convert_png_to_format("icns", temp_dir)
        return cls.convert_png_to_format("png", temp_dir)

    @classmethod
    def convert_png_to_format(cls, file_format: str, temp_dir_path: Path) -> Path:
        """Convert the application icon PNG to another format.

        Args:
            file_format: Target format (ico, icns, or png).
            temp_dir_path: Directory for the output file.

        Returns:
            Path to the converted icon file.
        """
        output_path = temp_dir_path / f"icon.{file_format}"
        png_path = cls.get_app_icon_png_path()
        img = Image.open(png_path)
        img.save(output_path, format=file_format.upper())
        return output_path

    @classmethod
    def get_app_icon_png_path(cls) -> Path:
        """Get the path to the application icon PNG.

        Override this method to use a custom icon location.

        Returns:
            Path to icon.png in the resources directory.
        """
        return cls.get_resources_path() / "icon.png"

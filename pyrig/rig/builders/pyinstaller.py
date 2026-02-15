"""PyInstaller-based artifact builder for creating standalone executables.

Provides the `PyInstallerBuilder` abstract base class for creating platform-specific
standalone executables from pyrig projects using PyInstaller.

Extends the `BuilderConfigFile` base class with PyInstaller-specific functionality
including resource bundling, icon conversion, and PyInstaller configuration.
Features include single-file executables (`--onefile`), automatic resource bundling
from multiple packages, platform-specific icon conversion (PNG to ICO/ICNS),
multi-package resource discovery, and no console window (`--noconsole`).

Resources are collected from two sources: default resources (all `resources` modules
from packages depending on pyrig, discovered automatically) and additional resources
(packages specified by `additional_resource_packages()`). All resources are bundled
using PyInstaller's `--add-data` option and are accessible at runtime via
`importlib.resources` or `pyrig.src.resource`.

Icon conversion expects an `icon.png` file in the resources directory and converts
it to the appropriate format per platform (Windows: ICO, macOS: ICNS, Linux: PNG).

Example:
    Create a builder for your application:

        from types import ModuleType
        from pyrig.rig.builders.pyinstaller import PyInstallerBuilder
        from pyrig import resources

        class AppBuilder(PyInstallerBuilder):

            def additional_resource_packages(self) -> list[ModuleType]:
                return [resources]

    Build the executable:

        $ uv run pyrig build
"""

import os
import platform
from abc import abstractmethod
from pathlib import Path
from types import ModuleType

from PIL import Image
from PyInstaller.__main__ import run
from PyInstaller.utils.hooks import collect_data_files

import pyrig
from pyrig import resources
from pyrig.rig.builders.base.base import BuilderConfigFile
from pyrig.src.modules.package import discover_equivalent_modules_across_dependents


class PyInstallerBuilder(BuilderConfigFile):
    """Abstract builder for creating PyInstaller standalone executables.

    Extends `BuilderConfigFile` to provide PyInstaller-specific functionality for
    creating single-file executables. Handles PyInstaller configuration, resource
    bundling, and icon conversion.

    Creates executables with:

    - Single-file executable (`--onefile`)
    - No console window (`--noconsole`)
    - Platform-specific icon (ICO/ICNS/PNG)
    - All resources bundled and accessible at runtime
    - Clean build (`--clean`)

    Resources are automatically discovered from packages depending on pyrig, plus
    additional packages specified by `additional_resource_packages()`. Subclasses
    must implement `additional_resource_packages()` to return a list of additional
    resource packages.

    Example:
        Basic PyInstaller builder:

            from types import ModuleType
            from pyrig.rig.builders.pyinstaller import PyInstallerBuilder
            from pyrig import resources

            class AppBuilder(PyInstallerBuilder):

                def additional_resource_packages(self) -> list[ModuleType]:
                    return [resources]
    """

    def create_artifacts(self, temp_artifacts_dir: Path) -> None:
        """Build a PyInstaller executable.

        Constructs PyInstaller command-line options and invokes PyInstaller to
        create the executable.

        Args:
            temp_artifacts_dir: Temporary directory where the exe will be created.
        """
        options = self.pyinstaller_options(temp_artifacts_dir)
        run(options)

    @abstractmethod
    def additional_resource_packages(self) -> list[ModuleType]:
        """Return packages containing additional resources to bundle.

        Subclasses must implement this method to specify resource packages beyond
        the automatically discovered ones. All files in the specified packages will
        be included in the executable and accessible at runtime.

        Returns:
            List of module objects representing resource packages.

        Example:
            Subclass implementation:


                def additional_resource_packages(self) -> list[ModuleType]:
                    from pyrig import resources
                    return [resources]
        """

    def default_additional_resource_packages(self) -> list[ModuleType]:
        """Get resource packages from all pyrig-dependent packages.

        Automatically discovers all `resources` modules from packages that depend
        on pyrig, enabling multi-package applications to bundle resources from
        their entire dependency chain.

        Returns:
            List of module objects representing resources packages from all
            packages in the dependency chain.
        """
        return discover_equivalent_modules_across_dependents(resources, pyrig)

    def all_resource_packages(self) -> list[ModuleType]:
        """Get all resource packages to bundle in the executable.

        Combines auto-discovered resource packages with additional packages
        specified by the subclass.

        Returns:
            List of all resource packages to bundle.
        """
        return [
            *self.default_additional_resource_packages(),
            *self.additional_resource_packages(),
        ]

    def add_datas(self) -> list[tuple[str, str]]:
        """Build the --add-data arguments for PyInstaller.

        Collects all data files from all resource packages and formats them as
        PyInstaller --add-data arguments.

        Returns:
            List of (source_path, destination_path) tuples for PyInstaller's
            --add-data argument.
        """
        add_datas: list[tuple[str, str]] = []
        resources_packages = self.all_resource_packages()
        for package in resources_packages:
            package_datas = collect_data_files(package.__name__, include_py_files=True)
            add_datas.extend(package_datas)
        return add_datas

    def pyinstaller_options(self, temp_artifacts_dir: Path) -> list[str]:
        """Build the complete PyInstaller command-line options.

        Constructs the full list of command-line arguments for PyInstaller,
        including entry point, flags, paths, icon, and resource files.

        Args:
            temp_artifacts_dir: Temporary directory for the executable.

        Returns:
            List of command-line arguments for PyInstaller.
        """
        temp_dir = temp_artifacts_dir.parent

        options = [
            str(self.main_path()),
            "--name",
            self.app_name(),
            "--clean",
            "--noconfirm",
            "--onefile",
            "--noconsole",
            "--workpath",
            str(self.temp_workpath(temp_dir)),
            "--specpath",
            str(self.temp_specpath(temp_dir)),
            "--distpath",
            str(self.temp_distpath(temp_dir)),
            "--icon",
            str(self.app_icon_path(temp_dir)),
        ]
        for src, dest in self.add_datas():
            options.extend(["--add-data", f"{src}{os.pathsep}{dest}"])
        return options

    def temp_distpath(self, temp_dir: Path) -> Path:
        """Get the temporary distribution output path.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path where PyInstaller will write the executable.
        """
        return self.temp_artifacts_path(temp_dir)

    def temp_workpath(self, temp_dir: Path) -> Path:
        """Get the temporary work directory for PyInstaller.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path to the workpath subdirectory.
        """
        path = temp_dir / "workpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def temp_specpath(self, temp_dir: Path) -> Path:
        """Get the temporary spec file directory.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path to the specpath subdirectory.
        """
        path = temp_dir / "specpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def app_icon_path(self, temp_dir: Path) -> Path:
        """Get the platform-appropriate icon path.

        Converts the PNG icon to the appropriate format for the current platform:
        Windows (ICO), macOS (ICNS), or Linux (PNG).

        Args:
            temp_dir: Temporary directory for the converted icon.

        Returns:
            Path to the converted icon file.
        """
        if platform.system() == "Windows":
            return self.convert_png_to_format("ico", temp_dir)
        if platform.system() == "Darwin":
            return self.convert_png_to_format("icns", temp_dir)
        return self.convert_png_to_format("png", temp_dir)

    def convert_png_to_format(self, file_format: str, temp_dir_path: Path) -> Path:
        """Convert the application icon PNG to another format.

        Uses PIL/Pillow to convert the source PNG icon to the specified format
        (ico, icns, or png). Note that ICNS conversion may require specific icon
        sizes (e.g., 16x16, 32x32, 128x128, 256x256, 512x512) for best results.

        Args:
            file_format: Target format extension ("ico", "icns", or "png").
            temp_dir_path: Directory where the converted icon should be written.

        Returns:
            Path to the converted icon file.
        """
        output_path = temp_dir_path / f"icon.{file_format}"
        png_path = self.app_icon_png_path()
        img = Image.open(png_path)
        img.save(output_path, format=file_format.upper())
        return output_path

    def app_icon_png_path(self) -> Path:
        """Get the path to the application icon PNG.

        Returns the path to the source PNG icon file. Override this method to
        use a custom icon location.

        Returns:
            Absolute path to the PNG icon file (`<src_package>/resources/icon.png`).
        """
        return self.resources_path() / "icon.png"

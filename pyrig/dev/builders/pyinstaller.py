"""PyInstaller-based artifact builder for creating standalone executables.

Provides the `PyInstallerBuilder` abstract base class for creating platform-specific
standalone executables from pyrig projects using PyInstaller.

Extends the BuilderConfigFile base class with PyInstaller-specific functionality
including resource bundling, icon conversion, and PyInstaller configuration.

Key Features:
    - Single-file executables (`--onefile`)
    - Automatic resource bundling from multiple packages
    - Platform-specific icon conversion (PNG → ICO/ICNS)
    - Multi-package resource discovery
    - No console window (`--noconsole`)

Resource Bundling:
    Resources are collected from two sources:

    1. **Default resources** (automatic): All `resources` modules from packages
       depending on pyrig
    2. **Additional resources** (subclass-specified): Packages specified by
       `get_additional_resource_pkgs()`

    All resources are bundled using PyInstaller's `--add-data` option and are
    accessible at runtime via `importlib.resources` or `pyrig.src.resource`.

Icon Conversion:
    Expects an `icon.png` file in the resources directory and converts it to
    the appropriate format:
    - Windows: PNG → ICO
    - macOS: PNG → ICNS
    - Linux: PNG (no conversion)

Example:
    Create a builder for your application::

        from types import ModuleType
        from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
        import myapp.resources

        class MyAppBuilder(PyInstallerBuilder):
            @classmethod
            def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                return [myapp.resources]

    Build the executable::

        $ uv run pyrig build

See Also:
    pyrig.dev.builders.base.base.BuilderConfigFile: Base builder class
    pyrig.src.resource: Runtime resource access utilities
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
from pyrig.dev.builders.base.base import BuilderConfigFile
from pyrig.src.modules.package import discover_equivalent_modules_across_dependents


class PyInstallerBuilder(BuilderConfigFile):
    """Abstract builder for creating PyInstaller standalone executables.

    Extends the BuilderConfigFile base class to provide PyInstaller-specific
    functionality for creating single-file executables. Handles PyInstaller
    configuration, resource bundling, and icon conversion.

    Creates executables with:
        - Single-file executable (`--onefile`)
        - No console window (`--noconsole`)
        - Platform-specific icon (ICO/ICNS/PNG)
        - All resources bundled and accessible at runtime
        - Clean build (`--clean`)

    Resources are automatically discovered from packages depending on pyrig, plus
    additional packages specified by `get_additional_resource_pkgs()`.

    Subclasses must implement:
        get_additional_resource_pkgs: Return list of additional resource packages.

    Example:
        Basic PyInstaller builder::

            from types import ModuleType
            from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
            import myapp.resources

            class MyAppBuilder(PyInstallerBuilder):
                @classmethod
                def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                    return [myapp.resources]

    See Also:
        BuilderConfigFile: Base class providing build orchestration
        get_pyinstaller_options: PyInstaller configuration
    """

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Build a PyInstaller executable.

        Constructs PyInstaller command-line options and invokes PyInstaller to
        create the executable.

        Args:
            temp_artifacts_dir: Temporary directory where the exe will be created.
        """
        options = cls.get_pyinstaller_options(temp_artifacts_dir)
        run(options)

    @classmethod
    @abstractmethod
    def get_additional_resource_pkgs(cls) -> list[ModuleType]:
        """Return packages containing additional resources to bundle.

        Subclasses must implement this method to specify resource packages beyond
        the automatically discovered ones. All files in the specified packages will
        be included in the executable and accessible at runtime.

        Returns:
            List of module objects representing resource packages.

        Example:
            ::

                @classmethod
                def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                    import myapp.resources
                    import myapp.plugins.resources
                    return [myapp.resources, myapp.plugins.resources]
        """

    @classmethod
    def get_default_additional_resource_pkgs(cls) -> list[ModuleType]:
        """Get resource packages from all pyrig-dependent packages.

        Automatically discovers all `resources` modules from packages that depend
        on pyrig, enabling multi-package applications to bundle resources from
        their entire dependency chain.

        Returns:
            List of module objects representing resources packages from all
            packages in the dependency chain.
        """
        return discover_equivalent_modules_across_dependents(resources, pyrig)

    @classmethod
    def get_all_resource_pkgs(cls) -> list[ModuleType]:
        """Get all resource packages to bundle in the executable.

        Combines auto-discovered resource packages with additional packages
        specified by the subclass.

        Returns:
            List of all resource packages to bundle.
        """
        return [
            *cls.get_default_additional_resource_pkgs(),
            *cls.get_additional_resource_pkgs(),
        ]

    @classmethod
    def get_add_datas(cls) -> list[tuple[str, str]]:
        """Build the --add-data arguments for PyInstaller.

        Collects all data files from all resource packages and formats them as
        PyInstaller --add-data arguments.

        Returns:
            List of (source_path, destination_path) tuples for PyInstaller's
            --add-data argument.
        """
        add_datas: list[tuple[str, str]] = []
        resources_pkgs = cls.get_all_resource_pkgs()
        for pkg in resources_pkgs:
            pkg_datas = collect_data_files(pkg.__name__, include_py_files=True)
            add_datas.extend(pkg_datas)
        return add_datas

    @classmethod
    def get_pyinstaller_options(cls, temp_artifacts_dir: Path) -> list[str]:
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
        """Get the temporary distribution output path.

        Args:
            temp_dir: Parent temporary directory.

        Returns:
            Path where PyInstaller will write the executable.
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

        Converts the PNG icon to the appropriate format for the current platform:
        Windows (ICO), macOS (ICNS), or Linux (PNG).

        Args:
            temp_dir: Temporary directory for the converted icon.

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
        png_path = cls.get_app_icon_png_path()
        img = Image.open(png_path)
        img.save(output_path, format=file_format.upper())
        return output_path

    @classmethod
    def get_app_icon_png_path(cls) -> Path:
        """Get the path to the application icon PNG.

        Returns the path to the source PNG icon file. Override this method to
        use a custom icon location.

        Returns:
            Absolute path to the PNG icon file (`<src_pkg>/resources/icon.png`).
        """
        return cls.get_resources_path() / "icon.png"

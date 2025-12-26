"""PyInstaller-based artifact builder for creating standalone executables.

This module provides the `PyInstallerBuilder` abstract base class for creating
platform-specific standalone executables from pyrig projects using PyInstaller.

The PyInstallerBuilder extends the Builder base class with PyInstaller-specific
functionality, handling all aspects of executable creation including resource
bundling, icon conversion, and PyInstaller configuration.

Key Capabilities:
    - **Single-file executables**: Creates standalone executables via PyInstaller's
      `--onefile` option
    - **Automatic resource bundling**: Collects resources from multiple packages
      across the dependency chain
    - **Platform-specific icon conversion**: Converts PNG icons to ICO (Windows),
      ICNS (macOS), or copies PNG (Linux)
    - **Multi-package resource discovery**: Automatically finds and bundles
      `resources` modules from all packages depending on pyrig
    - **PyInstaller configuration**: Generates complete command-line options
      for PyInstaller
    - **No console window**: Uses `--noconsole` for GUI applications

Resource Bundling System:
    Resources are automatically collected from two sources:

    1. **Default resources** (automatic discovery):
       - Finds all `resources` modules in packages depending on pyrig
       - Uses `get_same_modules_from_deps_depen_on_dep()` for discovery
       - Example: If `myapp` depends on `pyrig`, both `pyrig.resources` and
         `myapp.resources` are included automatically

    2. **Additional resources** (subclass-specified):
       - Packages specified by `get_additional_resource_pkgs()` implementation
       - Allows bundling resources from non-standard locations
       - Example: Plugin resources, third-party package resources

    All resources are bundled using PyInstaller's `--add-data` option and are
    accessible at runtime via `importlib.resources` or `pyrig.src.resource`.

Icon Conversion:
    The builder expects an `icon.png` file in the resources directory and
    automatically converts it to the appropriate format for each platform:

    - **Windows**: PNG → ICO format via PIL/Pillow
    - **macOS**: PNG → ICNS format via PIL/Pillow
    - **Linux**: PNG copied to temp directory (no conversion needed)

    The converted icon is passed to PyInstaller via the `--icon` argument.
    For best results, use a square PNG (e.g., 512x512 or 1024x1024).

PyInstaller Configuration:
    The builder generates the following PyInstaller command-line options:

    - Entry point: Path to `main.py` from `get_main_path()`
    - `--name`: Application name from `pyproject.toml`
    - `--clean`: Remove PyInstaller cache before building
    - `--noconfirm`: Replace output directory without confirmation
    - `--onefile`: Create a single executable file (not a directory)
    - `--noconsole`: Hide console window (for GUI applications)
    - `--workpath`: Temporary directory for PyInstaller's intermediate files
    - `--specpath`: Directory for generated `.spec` file
    - `--distpath`: Output directory for the executable (temp artifacts dir)
    - `--icon`: Platform-specific icon file path
    - `--add-data`: One argument per resource file (format: `source:destination`)

Example:
    Create a builder for your application::

        from types import ModuleType
        from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
        import myapp.resources

        class MyAppBuilder(PyInstallerBuilder):
            '''Builder for MyApp standalone executable.'''

            @classmethod
            def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                '''Specify additional resource packages to bundle.'''
                return [myapp.resources]

    Build the executable::

        $ uv run pyrig build
        # Creates: dist/myapp-Linux (or platform-specific name)

    The executable will include:
    - All Python code from the project
    - All resources from `pyrig.resources` (auto-discovered)
    - All resources from `myapp.resources` (auto-discovered)
    - Platform-specific icon
    - All dependencies

Module Attributes:
    None (no module-level constants or variables)

See Also:
    pyrig.dev.builders.base.base.Builder: Base builder class
    pyrig.src.modules.package.get_same_modules_from_deps_depen_on_dep:
        Resource discovery mechanism
    pyrig.src.resource: Runtime resource access utilities
    PyInstaller.utils.hooks.collect_data_files: Resource collection utility
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
from pyrig.dev.builders.base.base import Builder
from pyrig.src.modules.package import get_same_modules_from_deps_depen_on_dep


class PyInstallerBuilder(Builder):
    """Abstract builder for creating PyInstaller standalone executables.

    This class extends the Builder base class to provide PyInstaller-specific
    functionality for creating single-file executables. It handles all aspects
    of PyInstaller configuration, resource bundling, and icon conversion.

    The builder creates executables with the following characteristics:
        - Single-file executable (--onefile)
        - No console window for GUI apps (--noconsole)
        - Platform-specific icon (ICO/ICNS/PNG)
        - All resources bundled and accessible at runtime
        - Clean build (--clean removes PyInstaller cache)

    Resource Discovery:
        Resources are automatically discovered and bundled from:
        1. Default resources: All `resources` modules from packages depending on pyrig
        2. Additional resources: Packages specified by `get_additional_resource_pkgs()`

        This multi-package resource system allows applications to bundle resources
        from their entire dependency chain automatically.

    Icon Conversion:
        The builder expects an `icon.png` file in the resources directory and
        automatically converts it to the appropriate format:
        - Windows: Converts to ICO format
        - macOS: Converts to ICNS format
        - Linux: Copies PNG to temp directory

    Subclasses must implement:
        get_additional_resource_pkgs: Return list of additional resource packages
            to bundle beyond the automatically discovered ones.

    Class Attributes:
        Inherits ARTIFACTS_DIR_NAME from Builder (default: "dist").

    Example:
        Basic PyInstaller builder::

            from types import ModuleType
            from pyrig.dev.builders.pyinstaller import PyInstallerBuilder
            import myapp.resources

            class MyAppBuilder(PyInstallerBuilder):
                '''Creates standalone executable for MyApp.'''

                @classmethod
                def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                    '''Bundle application resources.'''
                    return [myapp.resources]

        With custom icon location::

            class MyAppBuilder(PyInstallerBuilder):
                @classmethod
                def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                    return [myapp.resources]

                @classmethod
                def get_app_icon_png_path(cls) -> Path:
                    '''Use custom icon location.'''
                    return cls.get_resources_path() / "custom_icon.png"

    See Also:
        Builder: Base class providing build orchestration
        create_artifacts: Implementation of the build process
        get_pyinstaller_options: PyInstaller configuration
    """

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Build a PyInstaller executable.

        Implements the abstract `create_artifacts` method from Builder to
        generate a standalone executable using PyInstaller. This method
        constructs the PyInstaller command-line options and invokes PyInstaller
        to create the executable.

        The build process:
            1. Generate PyInstaller command-line options
            2. Invoke PyInstaller with those options
            3. PyInstaller creates the executable in temp_artifacts_dir
            4. Builder framework handles renaming and moving to final location

        Args:
            temp_artifacts_dir: Path to the temporary directory where the
                executable should be created. PyInstaller will write the
                final executable to this directory.

        Note:
            This method is called automatically by the Builder.build() method.
            The executable will be automatically renamed with a platform suffix
            and moved to the final output directory after this method completes.

        See Also:
            get_pyinstaller_options: Generates the PyInstaller configuration
        """
        options = cls.get_pyinstaller_options(temp_artifacts_dir)
        run(options)

    @classmethod
    @abstractmethod
    def get_additional_resource_pkgs(cls) -> list[ModuleType]:
        """Return packages containing additional resources to bundle.

        Subclasses must implement this method to specify which resource packages
        should be bundled in the executable beyond the automatically discovered
        ones. All files in the specified packages will be included in the
        executable and accessible at runtime via `importlib.resources`.

        The resources from these packages are combined with the default resources
        (from all packages depending on pyrig) to create the complete set of
        bundled resources.

        Returns:
            List of module objects representing resource packages. Each module
            should be a package (directory with __init__.py) containing resource
            files.

        Example:
            ::

                @classmethod
                def get_additional_resource_pkgs(cls) -> list[ModuleType]:
                    '''Bundle application and plugin resources.'''
                    import myapp.resources
                    import myapp.plugins.resources
                    return [myapp.resources, myapp.plugins.resources]

        Note:
            Resources from packages depending on pyrig are included automatically
            via `get_default_additional_resource_pkgs()`. You only need to specify
            additional packages that aren't in the standard `resources` module
            location.

        See Also:
            get_default_additional_resource_pkgs: Automatically discovered resources
            get_all_resource_pkgs: Combined list of all resources
            pyrig.src.resource.get_resource_path: Runtime resource access
        """

    @classmethod
    def get_default_additional_resource_pkgs(cls) -> list[ModuleType]:
        """Get resource packages from all pyrig-dependent packages.

        Automatically discovers and returns all `resources` modules from packages
        that depend on pyrig. This enables multi-package applications to
        automatically bundle resources from their entire dependency chain.

        The discovery process:
            1. Find all packages that depend on pyrig
            2. For each package, look for a `resources` module
            3. Return all found resources modules

        Returns:
            List of module objects representing resources packages from all
            packages in the dependency chain. Returns an empty list if no
            packages with resources modules are found.

        Example:
            If the dependency chain is::

                pyrig
                ├── pyrig.resources
                └── myapp (depends on pyrig)
                    └── myapp.resources

            Then this returns::

                [pyrig.resources, myapp.resources]

        Note:
            This method is called automatically by `get_all_resource_pkgs()`.
            You don't typically need to call it directly.

        See Also:
            get_same_modules_from_deps_depen_on_dep: Core discovery mechanism
            get_all_resource_pkgs: Combines default and additional resources
        """
        return get_same_modules_from_deps_depen_on_dep(resources, pyrig)

    @classmethod
    def get_all_resource_pkgs(cls) -> list[ModuleType]:
        """Get all resource packages to bundle in the executable.

        Combines the automatically discovered resource packages (from packages
        depending on pyrig) with the additional resource packages specified by
        the subclass. This creates the complete list of resources to bundle.

        Returns:
            List of module objects representing all resource packages to bundle.
            Includes both default (auto-discovered) and additional (subclass-specified)
            resource packages.

        Example:
            ::

                # Auto-discovered: [pyrig.resources, myapp.resources]
                # Additional: [myapp.plugins.resources]
                # Combined: [pyrig.resources, myapp.resources, myapp.plugins.resources]

        Note:
            This method is called by `get_add_datas()` to determine which
            packages to scan for resource files.

        See Also:
            get_default_additional_resource_pkgs: Auto-discovered resources
            get_additional_resource_pkgs: Subclass-specified resources
            get_add_datas: Uses this to build PyInstaller --add-data arguments
        """
        return [
            *cls.get_default_additional_resource_pkgs(),
            *cls.get_additional_resource_pkgs(),
        ]

    @classmethod
    def get_add_datas(cls) -> list[tuple[str, str]]:
        """Build the --add-data arguments for PyInstaller.

        Collects all data files from all resource packages and formats them
        as PyInstaller --add-data arguments. Uses PyInstaller's
        `collect_data_files` utility to automatically gather all files from
        each resource package.

        The collected files include:
            - All non-Python files in resource packages
            - Python files (when include_py_files=True)
            - Files in subdirectories (recursive)

        Returns:
            List of (source_path, destination_path) tuples suitable for
            PyInstaller's --add-data argument. Each tuple specifies a file
            to bundle and where it should be placed in the executable.

        Example:
            ::

                add_datas = cls.get_add_datas()
                # Returns:
                # [
                #     ('/path/to/myapp/resources/icon.png', 'myapp/resources'),
                #     ('/path/to/myapp/resources/config.json', 'myapp/resources'),
                #     ...
                # ]

        Note:
            This method is called by `get_pyinstaller_options()` to build the
            complete PyInstaller command line. The returned tuples are formatted
            as `source:destination` strings for the --add-data argument.

        See Also:
            get_all_resource_pkgs: Determines which packages to scan
            get_pyinstaller_options: Uses this to build --add-data arguments
        """
        add_datas: list[tuple[str, str]] = []
        resources_pkgs = cls.get_all_resource_pkgs()
        for pkg in resources_pkgs:
            # collect_data_files returns list of (source, dest) tuples
            pkg_datas = collect_data_files(pkg.__name__, include_py_files=True)
            add_datas.extend(pkg_datas)
        return add_datas

    @classmethod
    def get_pyinstaller_options(cls, temp_artifacts_dir: Path) -> list[str]:
        """Build the complete PyInstaller command-line options.

        Constructs the full list of command-line arguments to pass to PyInstaller.
        This includes all configuration for creating a single-file executable with
        bundled resources and platform-specific icon.

        PyInstaller Options Generated:
            - Entry point: Path to main.py
            - --name: Application name from pyproject.toml
            - --clean: Remove PyInstaller cache before building
            - --noconfirm: Replace output directory without confirmation
            - --onefile: Create a single executable file
            - --noconsole: Hide console window (GUI applications)
            - --workpath: Temporary work directory for build files
            - --specpath: Directory for generated .spec file
            - --distpath: Output directory for the executable
            - --icon: Platform-specific application icon
            - --add-data: Resource files to bundle (one per resource file)

        Args:
            temp_artifacts_dir: Path to the temporary directory where the
                executable will be created. Used to derive other temporary
                paths for PyInstaller's intermediate files.

        Returns:
            List of command-line argument strings ready to pass to PyInstaller.
            The list can be passed directly to `PyInstaller.__main__.run()`.

        Example:
            ::

                options = cls.get_pyinstaller_options(temp_dir)
                # Returns:
                # [
                #     '/path/to/main.py',
                #     '--name', 'myapp',
                #     '--clean',
                #     '--noconfirm',
                #     '--onefile',
                #     '--noconsole',
                #     '--workpath', '/tmp/xyz/workpath',
                #     '--specpath', '/tmp/xyz/specpath',
                #     '--distpath', '/tmp/xyz/dist',
                #     '--icon', '/tmp/xyz/icon.ico',
                #     '--add-data', '/path/to/resource.png:myapp/resources',
                #     ...
                # ]

        Note:
            This method is called by `create_artifacts()` to build the
            PyInstaller command. The options are platform-independent except
            for the icon format and path separator in --add-data.

        See Also:
            create_artifacts: Uses this to invoke PyInstaller
            get_add_datas: Generates --add-data arguments
            get_app_icon_path: Generates platform-specific icon
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

        Returns the path where PyInstaller should write the final executable.
        This is the same as the temporary artifacts directory used by the
        Builder framework.

        Args:
            temp_dir: Path to the parent temporary directory created by the
                build process.

        Returns:
            Path to the dist subdirectory where PyInstaller will write the
            executable. The directory is guaranteed to exist.

        Note:
            This is passed to PyInstaller via the --distpath argument.

        See Also:
            get_temp_artifacts_path: Creates the artifacts subdirectory
        """
        return cls.get_temp_artifacts_path(temp_dir)

    @classmethod
    def get_temp_workpath(cls, temp_dir: Path) -> Path:
        """Get the temporary work directory for PyInstaller.

        Creates and returns the path to PyInstaller's work directory where
        it stores intermediate build files (.pyz archives, etc.). This
        directory is automatically cleaned up after the build.

        Args:
            temp_dir: Path to the parent temporary directory created by the
                build process.

        Returns:
            Path to the workpath subdirectory. The directory is created if
            it doesn't exist and is guaranteed to exist when this method returns.

        Note:
            This is passed to PyInstaller via the --workpath argument. The
            directory is inside the temporary build directory and is
            automatically cleaned up after the build completes.
        """
        path = temp_dir / "workpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_temp_specpath(cls, temp_dir: Path) -> Path:
        """Get the temporary spec file directory.

        Creates and returns the path where PyInstaller should write its
        generated .spec file. The .spec file contains the build configuration
        and is automatically cleaned up after the build.

        Args:
            temp_dir: Path to the parent temporary directory created by the
                build process.

        Returns:
            Path to the specpath subdirectory. The directory is created if
            it doesn't exist and is guaranteed to exist when this method returns.

        Note:
            This is passed to PyInstaller via the --specpath argument. The
            .spec file is a Python script that PyInstaller generates to
            configure the build. It's stored in the temporary directory and
            cleaned up automatically.
        """
        path = temp_dir / "specpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_app_icon_path(cls, temp_dir: Path) -> Path:
        """Get the platform-appropriate icon path.

        Converts the PNG icon to the appropriate format for the current platform
        and returns the path to the converted icon file. The conversion is
        performed automatically based on the platform:
            - Windows: PNG → ICO
            - macOS: PNG → ICNS
            - Linux: PNG (copied to temp directory)

        The converted icon is written to the temporary directory and used by
        PyInstaller for the executable's icon.

        Args:
            temp_dir: Path to the temporary directory where the converted icon
                file should be written.

        Returns:
            Path to the converted icon file in the temporary directory. The
            file is guaranteed to exist when this method returns.

        Example:
            ::

                # On Windows
                icon_path = cls.get_app_icon_path(temp_dir)
                # Returns: Path('/tmp/xyz/icon.ico')
                # Converted from resources/icon.png

                # On macOS
                icon_path = cls.get_app_icon_path(temp_dir)
                # Returns: Path('/tmp/xyz/icon.icns')
                # Converted from resources/icon.png

                # On Linux
                icon_path = cls.get_app_icon_path(temp_dir)
                # Returns: Path('/tmp/xyz/icon.png')
                # Copied from resources/icon.png

        Note:
            This is passed to PyInstaller via the --icon argument. The icon
            file is created in the temporary directory and cleaned up
            automatically after the build.

        See Also:
            convert_png_to_format: Performs the actual conversion
            get_app_icon_png_path: Source PNG icon location
        """
        if platform.system() == "Windows":
            return cls.convert_png_to_format("ico", temp_dir)
        if platform.system() == "Darwin":
            return cls.convert_png_to_format("icns", temp_dir)
        return cls.convert_png_to_format("png", temp_dir)

    @classmethod
    def convert_png_to_format(cls, file_format: str, temp_dir_path: Path) -> Path:
        """Convert the application icon PNG to another format.

        Uses PIL/Pillow to convert the source PNG icon to the specified format.
        The converted file is written to the temporary directory with the
        appropriate extension.

        Supported formats:
            - ico: Windows icon format
            - icns: macOS icon format
            - png: Portable Network Graphics (re-saved via PIL)

        Args:
            file_format: Target format extension (e.g., "ico", "icns", "png").
                Must be a format supported by PIL/Pillow.
            temp_dir_path: Path to the directory where the converted icon
                should be written.

        Returns:
            Path to the converted icon file. The file is guaranteed to exist
            when this method returns.

        Example:
            ::

                # Convert to Windows ICO format
                ico_path = cls.convert_png_to_format("ico", temp_dir)
                # Returns: Path('/tmp/xyz/icon.ico')

                # Convert to macOS ICNS format
                icns_path = cls.convert_png_to_format("icns", temp_dir)
                # Returns: Path('/tmp/xyz/icon.icns')

        Note:
            The source PNG should be square (e.g., 512x512) for best results.
            PIL/Pillow handles the conversion automatically, including creating
            multiple resolutions for ICO and ICNS formats.

        See Also:
            get_app_icon_png_path: Source PNG icon location
            get_app_icon_path: Platform-specific icon selection
        """
        output_path = temp_dir_path / f"icon.{file_format}"
        png_path = cls.get_app_icon_png_path()
        img = Image.open(png_path)
        img.save(output_path, format=file_format.upper())
        return output_path

    @classmethod
    def get_app_icon_png_path(cls) -> Path:
        """Get the path to the application icon PNG.

        Returns the path to the source PNG icon file that will be converted
        to platform-specific formats. By default, this is `icon.png` in the
        resources directory.

        Override this method in subclasses to use a custom icon location or
        filename.

        Returns:
            Path to the PNG icon file. Default is `resources/icon.png`.

        Example:
            Default usage::

                icon_path = cls.get_app_icon_png_path()
                # Returns: Path('/path/to/myapp/resources/icon.png')

            Custom icon location::

                @classmethod
                def get_app_icon_png_path(cls) -> Path:
                    '''Use custom icon from assets directory.'''
                    return cls.get_resources_path() / "assets" / "app_icon.png"

        Note:
            The PNG file should be square (e.g., 512x512 or 1024x1024) for
            best results when converting to ICO and ICNS formats. Smaller
            sizes may result in lower quality icons on high-DPI displays.

        See Also:
            get_app_icon_path: Converts PNG to platform-specific format
            convert_png_to_format: Performs the conversion
        """
        return cls.get_resources_path() / "icon.png"

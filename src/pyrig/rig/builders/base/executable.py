"""PyInstaller-based artifact builder for creating standalone executables."""

import os
import platform
from abc import abstractmethod
from collections.abc import Generator
from pathlib import Path
from types import ModuleType

from PIL import Image
from PyInstaller.__main__ import run
from PyInstaller.utils.hooks import collect_data_files

from pyrig.core.introspection.dependencies import (
    discover_equivalent_modules_across_dependents,
)
from pyrig.core.introspection.paths import module_file_path
from pyrig.core.resources import resource_path
from pyrig.rig import resources
from pyrig.rig.builders.base.builder import BuilderConfigFile
from pyrig.rig.tools.package_manager import PackageManager


class ExecutableBuilder(BuilderConfigFile):
    """Abstract builder for creating PyInstaller standalone executables.

    Extends ``BuilderConfigFile`` to produce single-file executables using
    PyInstaller. Handles command-line configuration, resource bundling across
    the full pyrig dependency chain, and platform-specific icon conversion.

    Built executables are configured with:

    - Single-file mode (``--onefile``)
    - No console window (``--noconsole``)
    - Platform-specific icon (ICO on Windows, ICNS on macOS, PNG on Linux)
    - All resources bundled and accessible at runtime via ``importlib.resources``
    - Clean workspace for each build (``--clean``)

    Subclasses must implement ``entry_point_module()`` and
    ``app_icon_png_location()``.

    Example:
        Minimal concrete subclass:

            from types import ModuleType
            from pyrig.rig.builders.base.executable import ExecutableBuilder
            from myapp import main, resources

            class AppBuilder(ExecutableBuilder):

                def entry_point_module(self) -> ModuleType:
                    return main

                def app_icon_png_location(self) -> tuple[str, ModuleType]:
                    return "icon", resources
    """

    @abstractmethod
    def entry_point_module(self) -> ModuleType:
        """Return the module that serves as the application's entry point.

        PyInstaller uses this module as the main script. The module should run
        the application when executed directly (i.e., contain an
        ``if __name__ == "__main__"`` block or equivalent).

        Returns:
            Module object for the entry point script.

        Example:
            If your application entry point is in ``myapp/main.py``:

                def entry_point_module(self) -> ModuleType:
                    from myapp import main
                    return main

            Where ``myapp/main.py`` contains:

                def main():
                    ...

                if __name__ == "__main__":
                    main()
        """

    def non_platform_stem(self) -> str:
        """Return the project name as the stem without a platform suffix."""
        return PackageManager.I.project_name()

    def extension(self) -> str:
        """Return the file extension for the built executable based on the platform."""
        if platform.system() == "Windows":
            return "exe"
        return ""

    def extension_separator(self) -> str:
        """Return the separator between the stem and extension for the executable."""
        if platform.system() == "Windows":
            return "."
        return ""

    def create_artifact(self, tmp_path: Path) -> None:
        """Build a PyInstaller executable.

        Gets the options for running Pyinstaller and runs it to build
        the executable.

        Args:
            tmp_path: Temporary directory where the executable is created.
        """
        run(self.executable_options(tmp_path))

    def executable_options(self, tmp_path: Path) -> list[str]:
        """Build the complete set of PyInstaller command-line arguments.

        Assembles all flags and paths required to invoke PyInstaller: the entry
        point script, output name, build paths, icon, and ``--add-data`` entries
        for every resource package. Uses ``tmp_path`` as distpath and as the
        root for workpath and specpath subdirectories.

        Args:
            tmp_path: Temporary directory used as distpath and as the root for
                workpath and specpath subdirectories.

        Returns:
            List of string arguments suitable for passing directly to
            ``PyInstaller.__main__.run``.
        """
        return [
            self.entry_point_path().as_posix(),
            "--name",
            self.stem(),
            "--clean",
            "--noconfirm",
            "--onefile",
            "--noconsole",
            "--workpath",
            self.temp_workpath(tmp_path).as_posix(),
            "--specpath",
            self.temp_specpath(tmp_path).as_posix(),
            "--distpath",
            tmp_path.as_posix(),
            "--icon",
            self.app_icon_path(tmp_path).as_posix(),
            *(
                arg
                for src, dest in self.add_datas()
                for arg in ("--add-data", f"{src}{os.pathsep}{dest}")
            ),
        ]

    def entry_point_path(self) -> Path:
        """Return the absolute path to the application's entry point script.

        Resolves the source file path of the module returned by
        ``entry_point_module()``. PyInstaller uses this path as its main script.

        Returns:
            Absolute path to the entry point ``.py`` file.
        """
        module = self.entry_point_module()
        return module_file_path(module)

    def add_datas(self) -> list[tuple[str, str]]:
        """Build the list of ``--add-data`` arguments for PyInstaller.

        Collects all data files from every resource package returned by
        ``resource_packages()``, including Python source files. Each entry is
        a ``(source_path, destination_path)`` tuple in the format expected by
        PyInstaller's ``--add-data`` option.

        Returns:
            List of ``(source, destination)`` tuples for PyInstaller's
            ``--add-data`` flag.
        """
        add_datas: list[tuple[str, str]] = []
        for package in self.resource_packages():
            package_datas = collect_data_files(package.__name__, include_py_files=True)
            add_datas.extend(package_datas)
        return add_datas

    def resource_packages(self) -> Generator[ModuleType, None, None]:
        """Yield resource packages from all pyrig-dependent packages.

        Discovers all ``resources`` modules from packages that depend on pyrig.
        This allows multi-package applications to bundle resources from their
        entire dependency chain without explicit configuration.

        Intentionally excludes pyrig's own resources package, as its resources
        (gitignore templates, licenses, etc.) are not useful to other applications.

        Returns:
            Generator of module objects for each discovered ``resources`` package.
        """
        return discover_equivalent_modules_across_dependents(resources)

    def app_icon_path(self, tmp_path: Path) -> Path:
        """Return the path to the converted, platform-appropriate icon file.

        Converts the source PNG icon to the format required by the current
        platform before returning the path:

        - Windows: ``.ico``
        - macOS: ``.icns``
        - Linux: ``.png``

        Args:
            tmp_path: Directory where the converted icon file is written.

        Returns:
            Path to the converted icon file.
        """
        if platform.system() == "Windows":
            return self.convert_png_to_format("ico", tmp_path)
        if platform.system() == "Darwin":
            return self.convert_png_to_format("icns", tmp_path)
        return self.convert_png_to_format("png", tmp_path)

    def convert_png_to_format(self, file_format: str, tmp_path: Path) -> Path:
        """Convert the application's PNG icon to the specified image format.

        Opens the source PNG returned by ``app_icon_png_path()`` and saves a
        copy in the requested format using Pillow. The output file is named
        ``icon.<file_format>`` and written to ``tmp_path``.

        ICNS conversion typically requires specific icon sizes (16x16, 32x32,
        128x128, 256x256, 512x512) for best results on macOS.

        Args:
            file_format: Target format extension without the dot
                (e.g., ``"ico"``, ``"icns"``, or ``"png"``).
            tmp_path: Directory where the converted icon is written.

        Returns:
            Path to the converted icon file.
        """
        output_path = tmp_path / f"icon.{file_format}"
        png_path = self.app_icon_png_path()
        with Image.open(png_path) as image:
            image.save(output_path, format=file_format.upper())
        return output_path

    def app_icon_png_path(self) -> Path:
        """Return the filesystem path to the source PNG icon.

        Resolves the PNG file identified by ``app_icon_png_location()`` using
        ``pyrig.core.resources.resource_path``, which works in both development
        environments and PyInstaller-bundled executables.

        Returns:
            Absolute path to the source PNG icon file.
        """
        file_stem, package = self.app_icon_png_location()
        return resource_path(f"{file_stem}.png", package)

    @abstractmethod
    def app_icon_png_location(self) -> tuple[str, ModuleType]:
        """Return the location of the source PNG icon as a ``(stem, package)`` pair.

        Identifies the PNG icon file so it can be resolved via
        ``importlib.resources``. The file must exist within the given package as
        ``<file_stem>.png``. The PNG is then converted to the platform-appropriate
        format (ICO, ICNS, or PNG) before being passed to PyInstaller.

        Returns:
            A ``(file_stem, package)`` tuple where ``file_stem`` is the filename
            without extension and ``package`` is the module containing the
            resource (e.g., ``("icon", resources)`` for ``resources/icon.png``).
        """

    def temp_workpath(self, tmp_path: Path) -> Path:
        """Return the PyInstaller work directory for intermediate build files.

        Creates the directory if it does not already exist.

        Args:
            tmp_path: Root temporary directory for the build.

        Returns:
            Path to the ``workpath`` subdirectory inside ``tmp_path``.
        """
        path = tmp_path / "workpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def temp_specpath(self, tmp_path: Path) -> Path:
        """Return the directory where PyInstaller writes the ``.spec`` file.

        Creates the directory if it does not already exist.

        Args:
            tmp_path: Root temporary directory for the build.

        Returns:
            Path to the ``specpath`` subdirectory inside ``tmp_path``.
        """
        path = tmp_path / "specpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

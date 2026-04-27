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

import pyrig
from pyrig.core.introspection.dependencies import (
    discover_equivalent_modules_across_dependents,
)
from pyrig.core.introspection.paths import module_file_path
from pyrig.core.resources import resource_path
from pyrig.rig import resources
from pyrig.rig.builders.base.builder import BuilderConfigFile


class PyInstallerBuilder(BuilderConfigFile):
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
            from pyrig.rig.builders.base.pyinstaller import PyInstallerBuilder
            from myapp import main, resources

            class AppBuilder(PyInstallerBuilder):

                def entry_point_module(self) -> ModuleType:
                    return main

                def app_icon_png_location(self) -> tuple[str, ModuleType]:
                    return "icon", resources
    """

    def create_artifacts(self, temp_artifacts_dir: Path) -> None:
        """Build a PyInstaller executable.

        Assembles the PyInstaller command-line options and runs PyInstaller.
        The resulting executable is written to ``temp_artifacts_dir``.

        Args:
            temp_artifacts_dir: Temporary directory where the executable is created.
        """
        options = self.pyinstaller_options(temp_artifacts_dir)
        run(options)

    def pyinstaller_options(self, temp_artifacts_dir: Path) -> tuple[str, ...]:
        """Build the complete set of PyInstaller command-line arguments.

        Assembles all flags and paths required to invoke PyInstaller: the entry
        point script, output name, build paths, icon, and ``--add-data`` entries
        for every resource package. Uses ``temp_artifacts_dir.parent`` as the
        root for PyInstaller's internal workpath and specpath subdirectories so
        they remain within the same temporary workspace as the executable.

        Args:
            temp_artifacts_dir: Temporary directory where the executable will be
                written. Its parent is used as the root for workpath and specpath.

        Returns:
            Tuple of string arguments suitable for passing directly to
            ``PyInstaller.__main__.run``.
        """
        temp_dir = temp_artifacts_dir.parent

        return (
            self.entry_point_path().as_posix(),
            "--name",
            self.app_name(),
            "--clean",
            "--noconfirm",
            "--onefile",
            "--noconsole",
            "--workpath",
            self.temp_workpath(temp_dir).as_posix(),
            "--specpath",
            self.temp_specpath(temp_dir).as_posix(),
            "--distpath",
            self.temp_distpath(temp_dir).as_posix(),
            "--icon",
            self.app_icon_path(temp_dir).as_posix(),
            *(
                arg
                for src, dest in self.add_datas()
                for arg in ("--add-data", f"{src}{os.pathsep}{dest}")
            ),
        )

    def entry_point_path(self) -> Path:
        """Return the absolute path to the application's entry point script.

        Resolves the source file path of the module returned by
        ``entry_point_module()``. PyInstaller uses this path as its main script.

        Returns:
            Absolute path to the entry point ``.py`` file.
        """
        module = self.entry_point_module()
        return module_file_path(module)

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

        Discovers all ``resources`` modules from packages in the pyrig dependency
        chain, starting with ``pyrig.rig.resources`` itself. This allows
        multi-package applications to bundle resources from their entire
        dependency chain without explicit configuration.

        Yields:
            Module objects for each discovered ``resources`` package.
        """
        return discover_equivalent_modules_across_dependents(resources, pyrig)

    def app_icon_path(self, temp_dir: Path) -> Path:
        """Return the path to the converted, platform-appropriate icon file.

        Converts the source PNG icon to the format required by the current
        platform before returning the path:

        - Windows: ``.ico``
        - macOS: ``.icns``
        - Linux: ``.png``

        Args:
            temp_dir: Directory where the converted icon file is written.

        Returns:
            Path to the converted icon file.
        """
        if platform.system() == "Windows":
            return self.convert_png_to_format("ico", temp_dir)
        if platform.system() == "Darwin":
            return self.convert_png_to_format("icns", temp_dir)
        return self.convert_png_to_format("png", temp_dir)

    def convert_png_to_format(self, file_format: str, temp_dir_path: Path) -> Path:
        """Convert the application's PNG icon to the specified image format.

        Opens the source PNG returned by ``app_icon_png_path()`` and saves a
        copy in the requested format using Pillow. The output file is named
        ``icon.<file_format>`` and written to ``temp_dir_path``.

        ICNS conversion typically requires specific icon sizes (16x16, 32x32,
        128x128, 256x256, 512x512) for best results on macOS.

        Args:
            file_format: Target format extension without the dot
                (e.g., ``"ico"``, ``"icns"``, or ``"png"``).
            temp_dir_path: Directory where the converted icon is written.

        Returns:
            Path to the converted icon file.
        """
        output_path = temp_dir_path / f"icon.{file_format}"
        png_path = self.app_icon_png_path()
        img = Image.open(png_path)
        img.save(output_path, format=file_format.upper())
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

    def temp_distpath(self, temp_dir: Path) -> Path:
        """Return the temporary directory where PyInstaller writes the executable.

        Args:
            temp_dir: Root temporary directory for the build.

        Returns:
            Path to the dist subdirectory inside ``temp_dir``.
        """
        return self.temp_artifacts_path(temp_dir)

    def temp_workpath(self, temp_dir: Path) -> Path:
        """Return the PyInstaller work directory for intermediate build files.

        Creates the directory if it does not already exist.

        Args:
            temp_dir: Root temporary directory for the build.

        Returns:
            Path to the ``workpath`` subdirectory inside ``temp_dir``.
        """
        path = temp_dir / "workpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def temp_specpath(self, temp_dir: Path) -> Path:
        """Return the directory where PyInstaller writes the ``.spec`` file.

        Creates the directory if it does not already exist.

        Args:
            temp_dir: Root temporary directory for the build.

        Returns:
            Path to the ``specpath`` subdirectory inside ``temp_dir``.
        """
        path = temp_dir / "specpath"
        path.mkdir(parents=True, exist_ok=True)
        return path

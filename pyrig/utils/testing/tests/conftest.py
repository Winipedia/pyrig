"""Pytest configuration for pirig tests.

finds all the plugins in the tests directory and the package's testing module
and adds them to pytest_plugins. This way defining reusable fixtures is easy.
"""

from pathlib import Path

import pyrig
from pyrig.utils.modules.module import to_module_name, to_path

package_path = Path(pyrig.__path__[0])

custom_plugin_path = to_path("tests.base.fixtures", is_package=True)
package_plugin_path = (
    package_path / to_path("utils.testing", is_package=True) / custom_plugin_path
)

custom_plugin_module_names = [
    to_module_name(path) for path in custom_plugin_path.rglob("*.py")
]

package_plugin_module_names = [
    to_module_name(path.relative_to(package_path.parent))
    for path in package_plugin_path.rglob("*.py")
]


pytest_plugins = [
    *package_plugin_module_names,
    *custom_plugin_module_names,
]

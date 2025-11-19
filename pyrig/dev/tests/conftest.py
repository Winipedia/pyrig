"""Pytest configuration for pirig tests.

finds all the plugins in the tests directory and the package's testing module
and adds them to pytest_plugins. This way defining reusable fixtures is easy.
"""

from pathlib import Path

import pyrig
from pyrig import dev
from pyrig.src.modules.module import to_module_name, to_path

tests_to_fixtures = "tests.base.fixtures"
tests_to_fixtures_path = to_path(tests_to_fixtures, is_package=True)

package_root_path = Path(pyrig.__file__).parent.parent
package_plugin_path = Path(dev.__file__).parent / tests_to_fixtures_path
package_plugin_module_names = [
    to_module_name(path.relative_to(package_root_path))
    for path in package_plugin_path.rglob("*.py")
]

if not package_plugin_module_names or not package_plugin_path.exists():
    msg = f"Found no plugins in {package_plugin_path}"
    raise ValueError(msg)


custom_plugin_path = tests_to_fixtures_path
custom_plugin_module_names = [
    to_module_name(path) for path in custom_plugin_path.rglob("*.py")
]
if not custom_plugin_module_names and custom_plugin_path.exists():
    msg = f"Found no plugins in {custom_plugin_path}"
    raise ValueError(msg)

pytest_plugins = [
    *package_plugin_module_names,
    *custom_plugin_module_names,
]

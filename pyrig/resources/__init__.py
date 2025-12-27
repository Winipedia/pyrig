"""Static resource files for pyrig development tools.

Fallback templates for config generators when network operations fail.
Accessed via `pyrig.src.resource.get_resource_path()`.

Resource Files:
    GITIGNORE: GitHub's Python .gitignore template (fallback for API fetch)
    LATEST_PYTHON_VERSION: Latest stable Python version (endoflife.date fallback)
    MIT_LICENSE_TEMPLATE: MIT License with [year] and [fullname] placeholders

Note:
    These are pyrigs internal assets for config generators
    Auto-updated in pyrig dev mode when network fetches succeed and
    running inside pyrig itself

See Also:
    pyrig.src.resource.get_resource_path
    pyrig.dev.utils.resources
    pyrig.dev.configs.python.resources_init
"""

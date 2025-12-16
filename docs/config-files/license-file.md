# LicenceConfigFile

## Overview

**File Location:** `LICENSE`
**ConfigFile Class:** `LicenceConfigFile`
**File Type:** Plain text
**Priority:** Standard

The software license for your project. Pyrig automatically generates an MIT License with the current year and repository owner, but you can replace it with any license you prefer.

## Purpose

The `LICENSE` file serves critical legal and practical purposes:

- **Legal Protection** - Defines how others can use your code
- **Open Source Compliance** - Required for most open source projects
- **PyPI Requirement** - Referenced in `pyproject.toml` for package distribution
- **GitHub Integration** - Displayed on your repository page

### Why pyrig manages this file

pyrig creates a default MIT License to:
1. **Immediate compliance** - Projects are properly licensed from day one
2. **Automatic attribution** - Uses your GitHub username and current year
3. **Standard choice** - MIT is permissive and widely accepted
4. **Easy replacement** - You can change to any license you prefer

The file is created during `pyrig init` with MIT License text. If the file already exists and has content, pyrig leaves it unchanged.

## File Contents

### MIT License (Default)

- **Type:** Plain text (MIT License)
- **Default:** MIT License with current year and repository owner
- **Required:** Yes (for publishing to PyPI)
- **Purpose:** Grants permissions and disclaims liability
- **Why pyrig sets it:** MIT is permissive, simple, and widely used

The license text is fetched from GitHub's SPDX license API and automatically filled with:
- **Year:** Current year (e.g., `2025`)
- **Owner:** Repository owner from git remote URL or git config

### How the Owner is Determined

pyrig extracts the owner from your git configuration:

1. **From remote URL** (preferred):
   ```bash
   git remote get-url origin
   # https://github.com/YourUsername/my-awesome-project
   # Owner: YourUsername
   ```

2. **From git config** (fallback):
   ```bash
   git config user.name
   # Your Name
   # Owner: Your Name
   ```

The remote URL takes precedence because it's more reliable for GitHub projects.

## Default Configuration

For a project owned by `YourUsername` in 2025:

**File location:** `LICENSE`

**File contents:**
```
MIT License

Copyright (c) 2025 YourUsername

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Customization

You can replace the MIT License with any license you prefer. Pyrig will not overwrite an existing LICENSE file that has content.

### Using a Different License

#### Option 1: Replace the File Manually

1. **Delete the MIT License:**
   ```bash
   rm LICENSE
   ```

2. **Create your preferred license:**
   ```bash
   # Example: Apache 2.0
   curl https://www.apache.org/licenses/LICENSE-2.0.txt > LICENSE
   ```

3. **Update pyproject.toml:**
   ```toml
   [project]
   license-files = ["LICENSE"]
   ```

#### Option 2: Use GitHub's License Picker

1. Go to your repository on GitHub
2. Click "Add file" → "Create new file"
3. Name it `LICENSE`
4. Click "Choose a license template"
5. Select your preferred license
6. Commit the file

#### Option 3: Subclass LicenceConfigFile

For a different default license in all your projects:

```python
from pyrig.dev.configs.licence import LicenceConfigFile


class CustomLicenceConfigFile(LicenceConfigFile):
    @classmethod
    def get_content_str(cls) -> str:
        """Use Apache 2.0 instead of MIT."""
        return cls.get_apache_license_with_year_and_owner()

    @classmethod
    def get_apache_license_with_year_and_owner(cls) -> str:
        """Get Apache 2.0 license with year and owner."""
        # Fetch Apache 2.0 license and customize
        # Implementation similar to get_mit_license_with_year_and_owner
        ...
```

### Popular License Choices

| License | Use Case | Permissions |
|---------|----------|-------------|
| **MIT** (default) | Simple, permissive | Commercial use, modification, distribution, private use |
| **Apache 2.0** | Patent protection | Same as MIT + explicit patent grant |
| **GPL v3** | Copyleft | Requires derivative works to be open source |
| **BSD 3-Clause** | Similar to MIT | Permissive with attribution requirement |
| **Unlicense** | Public domain | No restrictions whatsoever |

## Relationship with pyproject.toml

The LICENSE file is referenced in `pyproject.toml`:

```toml
[project]
license-files = ["LICENSE"]
```

This tells build tools to include the license in distributions. When users install your package, they get the LICENSE file.

## PyPI Integration

When you publish to PyPI, the license is:
1. **Included in the package** - Users can read it after installation
2. **Displayed on PyPI** - Shown on your project's PyPI page
3. **Classified** - Use classifiers in `pyproject.toml` to indicate license type:
   ```toml
   classifiers = [
       "License :: OSI Approved :: MIT License",
   ]
   ```

## GitHub Integration

GitHub automatically:
- **Detects the license** - Shows it in the repository sidebar
- **Displays the type** - "MIT License" badge
- **Provides license picker** - When creating new files named LICENSE

## Related Files

- **`pyproject.toml`** - References LICENSE in `license-files` field ([pyproject.toml](pyproject.md))
- **`README.md`** - Often includes a license badge ([readme-file.md](readme-file.md))

## Common Issues

### Issue: Wrong owner name in license

**Symptom:** LICENSE shows incorrect copyright holder

**Cause:** Git remote URL or git config has wrong username

**Solution:**
1. **Check git remote:**
   ```bash
   git remote get-url origin
   ```

2. **Update if wrong:**
   ```bash
   git remote set-url origin https://github.com/CorrectUsername/repo.git
   ```

3. **Regenerate LICENSE:**
   ```bash
   rm LICENSE
   uv run pyrig mkroot
   ```

### Issue: Wrong year in license

**Symptom:** LICENSE shows old year

**Cause:** File was created in a previous year

**Solution:**
1. **Manually update the year:**
   ```bash
   sed -i 's/Copyright (c) 2024/Copyright (c) 2025/' LICENSE
   ```

2. **Or regenerate:**
   ```bash
   rm LICENSE
   uv run pyrig mkroot
   ```

**Note:** Some projects use a year range (e.g., `2024-2025`) to indicate ongoing development.

### Issue: PyPI rejects package due to license

**Symptom:** Upload fails with license-related error

**Cause:** LICENSE file missing or `license-files` not set in `pyproject.toml`

**Solution:**
1. **Ensure LICENSE exists:**
   ```bash
   ls LICENSE
   ```

2. **Check pyproject.toml:**
   ```toml
   [project]
   license-files = ["LICENSE"]
   ```

3. **Rebuild and republish:**
   ```bash
   uv run pyrig build
   uv run pyrig publish
   ```

### Issue: Want to use multiple licenses

**Symptom:** Project has components under different licenses

**Cause:** Complex licensing requirements

**Solution:**
1. **Create multiple license files:**
   ```bash
   LICENSE          # Main license
   LICENSE-MIT      # MIT for some components
   LICENSE-APACHE   # Apache for other components
   ```

2. **Update pyproject.toml:**
   ```toml
   [project]
   license-files = ["LICENSE", "LICENSE-MIT", "LICENSE-APACHE"]
   ```

3. **Document in README:**
   ```markdown
   ## License

   This project is dual-licensed under MIT and Apache 2.0.
   See LICENSE-MIT and LICENSE-APACHE for details.
   ```

### Issue: License file keeps getting regenerated

**Symptom:** LICENSE changes back to MIT after running `pyrig mkroot`

**Cause:** This shouldn't happen - pyrig only creates LICENSE if it doesn't exist or is empty

**Solution:**
Ensure your LICENSE file has content. Pyrig checks:
```python
if LICENSE.exists() and LICENSE.read_text().strip():
    # Don't overwrite
```

If this still happens, it's a bug - please report it.

### Issue: Want to change license mid-project

**Symptom:** Need to switch from MIT to another license

**Cause:** Project requirements changed

**Solution:**
1. **Understand implications** - Changing licenses can be complex legally
2. **Consult a lawyer** - For significant projects
3. **For simple cases:**
   ```bash
   # Replace the license
   rm LICENSE
   # Add new license (e.g., from GitHub)
   curl https://www.apache.org/licenses/LICENSE-2.0.txt > LICENSE
   ```
4. **Update classifiers in pyproject.toml:**
   ```toml
   classifiers = [
       "License :: OSI Approved :: Apache Software License",
   ]
   ```
5. **Announce the change** - In release notes and README

## See Also

- [Choose a License](https://choosealicense.com/) - GitHub's license picker guide
- [SPDX License List](https://spdx.org/licenses/) - Standardized license identifiers
- [OSI Approved Licenses](https://opensource.org/licenses) - Open Source Initiative
- [pyproject.toml](pyproject.md) - License file reference
- [README.md](readme-file.md) - License badge display
- [Getting Started Guide](../getting-started.md) - Initial project setup



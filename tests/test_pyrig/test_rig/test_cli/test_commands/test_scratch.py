"""module."""

from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.rig.cli.commands.scratch import run_scratch_file
from pyrig.rig.configs.scratch import ScratchConfigFile


def test_run_scratch_file(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        ScratchConfigFile.I.validate()
        # write a raise Error in the .scratch file to ensure it gets executed
        path = ScratchConfigFile.I.path()
        msg = "this error is expected from .scratch.py"
        path.write_text(f"""
if __name__ == "__main__":
    raise ValueError("{msg}")
""")
        # Capture the output of run_scratch_file
        with pytest.raises(ValueError, match=msg):
            run_scratch_file()

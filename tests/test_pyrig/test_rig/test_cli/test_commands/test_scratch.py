"""module."""

from contextlib import chdir
from pathlib import Path

import pytest

from pyrig.rig.cli.commands.scratch import run_scratch_file
from pyrig.rig.configs.python.dot_scratch import DotScratchConfigFile


def test_run_scratch_file(tmp_path: Path) -> None:
    """Test function."""
    with chdir(tmp_path):
        DotScratchConfigFile().I.validate()
        # write a raise Error in the .scratch file to ensure it gets executed
        path = DotScratchConfigFile.I.path()
        msg = "This error is expected from .scratch!"
        path.write_text(f'raise ValueError("{msg}")')
        # Capture the output of run_scratch_file
        with pytest.raises(ValueError, match=msg):
            run_scratch_file()

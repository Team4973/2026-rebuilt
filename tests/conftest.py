"""Platform-aware test configuration for Phoenix 6 swerve projects.

On Windows, Phoenix 6 CAN simulation is significantly slower, causing
pyfrc's built-in tests to hang or timeout. Skip them on Windows and
only run on macOS/Linux where sim performance is acceptable.
"""

import platform
import sys

import pytest

# Skip all pyfrc built-in tests on Windows — Phoenix 6 CAN sim is too slow
if platform.system() == "Windows":
    collect_ignore_glob = ["pyfrc_test.py"]
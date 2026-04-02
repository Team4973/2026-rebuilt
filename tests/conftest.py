"""Platform-aware test configuration for Phoenix 6 swerve projects.

On Windows, Phoenix 6 CAN simulation is significantly slower, causing
pyfrc's built-in tests to timeout during robotInit. Skip them on Windows
and only run on macOS/Linux where sim performance is acceptable.
"""

import platform
import sys

import pytest


def pytest_collection_modifyitems(config, items):
    """Skip all tests on Windows — Phoenix 6 CAN sim is too slow."""
    if platform.system() == "Windows":
        skip_windows = pytest.mark.skip(reason="Phoenix 6 CAN sim too slow on Windows")
        for item in items:
            item.add_marker(skip_windows)
"""Increase the pyfrc robotInit timeout for Phoenix 6 swerve projects.

Phoenix 6's SwerveDrivetrain does blocking WaitForAll calls for all
motors/encoders/IMU during init. On Windows, the simulated CAN bus is
slower and the default 2-second pyfrc timeout is not enough.
"""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def increase_robot_init_timeout():
    """Patch TestController.run_robot to allow 10 seconds for robotInit."""
    from pyfrc.test_support.controller import TestController
    import contextlib
    import threading

    original_run_robot = TestController.run_robot

    @contextlib.contextmanager
    def patched_run_robot(self):
        robot = self._robot
        self._robot = None

        self._thread = th = threading.Thread(
            target=self._robot_thread, args=(robot,), daemon=True
        )
        th.start()

        with self._cond:
            assert self._cond.wait_for(lambda: self._robot_started, timeout=5)
            assert self._cond.wait_for(lambda: self._robot_initialized, timeout=10)

        try:
            yield
        finally:
            self._robot_finished = True
            robot.endCompetition()

            if isinstance(self._reraise.exception, RuntimeError):
                if str(self._reraise.exception).startswith(
                    "HAL: A handle parameter was passed incorrectly"
                ):
                    msg = (
                        "Do not reuse HAL objects in tests! This error may occur if you"
                        " stored a motor/sensor as a global or as a class variable"
                        " outside of a method."
                    )
                    if hasattr(Exception, "add_note"):
                        self._reraise.exception.add_note(f"*** {msg}")
                    else:
                        e = self._reraise.exception
                        self._reraise.reset()
                        raise RuntimeError(msg) from e

        from wpilib.simulation import stepTimingAsync

        stepTimingAsync(1.0)

        th.join(timeout=5)
        if th.is_alive():
            pytest.fail("robot did not exit within 5 seconds")

        self._robot = None
        self._thread = None

    with patch.object(TestController, "run_robot", patched_run_robot):
        yield
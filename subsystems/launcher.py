from commands2 import Subsystem
from phoenix6 import hardware, controls


class Launcher(Subsystem):
    """Launcher subsystem with a single TalonFX motor."""

    def __init__(self, launcher_motor_id: int = 33):
        super().__init__()
        self._launcher_motor = hardware.TalonFX(launcher_motor_id)
        self._duty_cycle = controls.DutyCycleOut(0)

    def set_speed(self, speed: float) -> None:
        """Set motor speed (-1.0 to 1.0)."""
        self._launcher_motor.set_control(self._duty_cycle.with_output(speed))
    def stop(self) -> None:
        """Stop the motor."""
        self._launcher_motor.set_control(self._duty_cycle.with_output(0))
       

    #PID - def set_rpm(self) -> None:
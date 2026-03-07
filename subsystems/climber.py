from commands2 import Subsystem
from phoenix6 import hardware, controls


class Climber(Subsystem):
    """Launcher subsystem with a single TalonFX motor."""

    def __init__(self, motor_id: int = 47):
        super().__init__()
        self._motor = hardware.TalonFX(motor_id)
        self._duty_cycle = controls.DutyCycleOut(0)

    def set_speed(self, speed: float) -> None:
        """Set motor speed (-1.0 to 1.0)."""
        self._motor.set_control(self._duty_cycle.with_output(speed))

    def stop(self) -> None:
        """Stop the motor."""
        self._motor.set_control(self._duty_cycle.with_output(0))

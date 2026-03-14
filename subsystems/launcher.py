from commands2 import Subsystem
from phoenix6 import hardware, controls, configs


class Launcher(Subsystem):
    """Launcher subsystem with a single TalonFX motor."""

    # Tune these PID gains on the real robot
    LAUNCHER_KP = 0.1
    LAUNCHER_KV = 0.12

    def __init__(self, launcher_motor_id: int = 33):
        super().__init__()
        self._launcher_motor = hardware.TalonFX(launcher_motor_id)

        # Configure Slot0 PID for velocity control
        slot0 = configs.Slot0Configs().with_k_p(self.LAUNCHER_KP).with_k_v(self.LAUNCHER_KV)
        motor_config = configs.TalonFXConfiguration().with_slot0(slot0)
        self._launcher_motor.configurator.apply(motor_config)

        self._velocity = controls.VelocityVoltage(0)
        self._duty_cycle = controls.DutyCycleOut(0)

    def set_velocity(self, rps: float) -> None:
        """Set motor velocity in rotations per second."""
        self._launcher_motor.set_control(self._velocity.with_velocity(rps))

    def set_speed(self, speed: float) -> None:
        """Set motor speed (-1.0 to 1.0) open-loop. Kept as fallback."""
        self._launcher_motor.set_control(self._duty_cycle.with_output(speed))

    def stop(self) -> None:
        """Stop the motor."""
        self._launcher_motor.set_control(self._duty_cycle.with_output(0))
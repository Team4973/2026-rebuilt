from commands2 import Subsystem
from phoenix6 import controls, hardware

class Intake_Arm(Subsystem):
    def __init__(self, feeder_motor_id: int = 30):
        super().__init__()
        self.feeder_motor = hardware.TalonFX(feeder_motor_id)
        self._duty_cycle = controls.DutyCycleOut(0)

    def set_speed(self, speed: float) -> None:
        self.feeder_motor.set_control(self._duty_cycle.with_output(speed))

    def stop(self) -> None:
        """Stop the motor."""
        self.feeder_motor.set_control(self._duty_cycle.with_output(0))
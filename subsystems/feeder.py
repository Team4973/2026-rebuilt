from commands2 import Subsystem
from phoenix6 import controls, hardware

class Feeder(Subsystem):
    def __init__(self, l_feeder_motor_id: int = 32, r_feeder_motor_id = 31):
        super().__init__()
        self.l_feeder_motor = hardware.TalonFX(l_feeder_motor_id)
        self.r_feeder_motor = hardware.TalonFX(r_feeder_motor_id)
        self._duty_cycle = controls.DutyCycleOut(0)

    def set_speed(self, speed: float) -> None:
        self.l_feeder_motor.set_control(self._duty_cycle.with_output(speed))
        self.r_feeder_motor.set_control(self._duty_cycle.with_output(speed))

    def stop(self) -> None:
        """Stop the motor."""
        self.l_feeder_motor.set_control(self._duty_cycle.with_output(0))
        self.r_feeder_motor.set_control(self._duty_cycle.with_output(0))
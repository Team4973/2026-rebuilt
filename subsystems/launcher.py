from commands2 import Subsystem
from phoenix6 import hardware, controls, configs
from wpilib import SmartDashboard, Timer
from subsystems import launcher_config


class Launcher(Subsystem):
    """Launcher subsystem with a single TalonFX motor."""

    # Tune these PID gains on the real robot
    LAUNCHER_KP = 0.1
    LAUNCHER_KV = 0.15
    LAUNCHER_KS = 0.0

    # Speed management constants
    DEFAULT_RPS = 54.0 
    RPS_INCREMENT = 1.0
    MIN_RPS = 45.0
    MAX_RPS = 80.0

    def __init__(self, launcher_motor_id: int = 33):
        super().__init__()
        self._launcher_motor = hardware.TalonFX(launcher_motor_id)

        # Configure Slot0 PID for velocity control
        slot0 = (
            configs.Slot0Configs()
            .with_k_p(self.LAUNCHER_KP)
            .with_k_v(self.LAUNCHER_KV)
            .with_k_s(self.LAUNCHER_KS)
        )
        motor_config = configs.TalonFXConfiguration().with_slot0(slot0)
        self._launcher_motor.configurator.apply(motor_config)

        self._velocity = controls.VelocityVoltage(0)
        self._duty_cycle = controls.DutyCycleOut(0)

        # Track current PID gains for live tuning
        self._kp = self.LAUNCHER_KP
        self._kv = self.LAUNCHER_KV
        self._ks = self.LAUNCHER_KS
        SmartDashboard.putNumber("Launcher/kP", self._kp)
        SmartDashboard.putNumber("Launcher/kV", self._kv)
        SmartDashboard.putNumber("Launcher/kS", self._ks)

        # Spin-up tracking
        self._spinup_start_time: float | None = None
        self._last_at_target = False

        # Adjustable target speed
        self._target_rps = self.DEFAULT_RPS
        self._auto_mode = False
        self._auto_rps = self.DEFAULT_RPS
        self._distance_to_hopper = 0.0

    def set_velocity(self, rps: float) -> None:
        """Set motor velocity in rotations per second."""
        self._launcher_motor.set_control(self._velocity.with_velocity(rps))

    def set_speed(self, speed: float) -> None:
        """Set motor speed (-1.0 to 1.0) open-loop. Kept as fallback."""
        self._launcher_motor.set_control(self._duty_cycle.with_output(speed))

    def stop(self) -> None:
        """Stop the motor."""
        self._launcher_motor.set_control(self._duty_cycle.with_output(0))

    def get_target_rps(self) -> float:
        """Return the active target RPS (auto or manual depending on mode)."""
        if self._auto_mode:
            return self._auto_rps
        return self._target_rps

    def toggle_auto_mode(self) -> None:
        """Toggle between manual and auto (distance-based) speed mode."""
        self._auto_mode = not self._auto_mode

    def is_auto_mode(self) -> bool:
        return self._auto_mode

    def set_auto_rps(self, rps: float) -> None:
        """Set the auto-calculated RPS (called externally from distance logic)."""
        self._auto_rps = rps

    def set_distance_to_hopper(self, distance_m: float) -> None:
        """Store distance for telemetry display."""
        self._distance_to_hopper = distance_m

    def nudge_speed_up(self) -> None:
        """Increase target RPS by increment, clamped to MAX_RPS."""
        self._target_rps = min(self._target_rps + self.RPS_INCREMENT, self.MAX_RPS)

    def nudge_speed_down(self) -> None:
        """Decrease target RPS by increment, clamped to MIN_RPS."""
        self._target_rps = max(self._target_rps - self.RPS_INCREMENT, self.MIN_RPS)

    def reset_speed(self) -> None:
        """Reset target RPS to default."""
        self._target_rps = self.DEFAULT_RPS

    def periodic(self) -> None:
        target_rps = self.get_target_rps()
        actual_rps = self._launcher_motor.get_velocity().value
        error_rps = target_rps - actual_rps
        at_target = abs(error_rps) < 2.0 and target_rps > 0

        SmartDashboard.putNumber("Launcher/TargetRPS", target_rps)
        SmartDashboard.putNumber("Launcher/ManualRPS", self._target_rps)
        SmartDashboard.putNumber("Launcher/AutoRPS", self._auto_rps)
        SmartDashboard.putNumber("Launcher/ActualRPS", actual_rps)
        SmartDashboard.putNumber("Launcher/ErrorRPS", error_rps)
        SmartDashboard.putBoolean("Launcher/AtTarget", at_target)
        SmartDashboard.putString(
            "Launcher/Mode", "Auto" if self._auto_mode else "Manual"
        )
        SmartDashboard.putNumber("Launcher/DistanceToHopper", self._distance_to_hopper)

        # Spin-up time tracking: measure time from first movement to reaching target
        if target_rps > 0 and abs(actual_rps) > 1.0 and self._spinup_start_time is None:
            self._spinup_start_time = Timer.getFPGATimestamp()
        if at_target and not self._last_at_target and self._spinup_start_time is not None:
            elapsed = Timer.getFPGATimestamp() - self._spinup_start_time
            SmartDashboard.putNumber("Launcher/SpinUpTimeSec", elapsed)
        if target_rps == 0 or actual_rps < 1.0:
            self._spinup_start_time = None
        self._last_at_target = at_target

        # Live-tunable launcher velocity PID (only apply on change)
        new_kp = SmartDashboard.getNumber("Launcher/kP", self._kp)
        new_kv = SmartDashboard.getNumber("Launcher/kV", self._kv)
        new_ks = SmartDashboard.getNumber("Launcher/kS", self._ks)
        if new_kp != self._kp or new_kv != self._kv or new_ks != self._ks:
            self._kp = new_kp
            self._kv = new_kv
            self._ks = new_ks
            slot0 = (
                configs.Slot0Configs()
                .with_k_p(new_kp)
                .with_k_v(new_kv)
                .with_k_s(new_ks)
            )
            self._launcher_motor.configurator.apply(
                configs.TalonFXConfiguration().with_slot0(slot0)
            )

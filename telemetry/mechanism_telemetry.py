from phoenix6 import BaseStatusSignal, SignalLogger, hardware
from phoenix6.status_signal import StatusSignal
from ntcore import NetworkTableInstance


class MechanismTelemetry:
    """Publishes mechanism TalonFX telemetry (RPM) to NetworkTables + hoot logs."""

    def __init__(self) -> None:
        self._inst = NetworkTableInstance.getDefault()
        self._table = self._inst.getTable("Mechanism Telemetry")
        self._entries: list[tuple[str, StatusSignal, object]] = []
        self._signals: list[BaseStatusSignal] = []

    def add_talonfx(
        self,
        name: str,
        motor: hardware.TalonFX,
        *,
        use_rotor_velocity: bool = False,
        signal_rate_hz: float = 50.0,
    ) -> None:
        """Register a TalonFX motor to publish as RPM."""
        velocity_signal = (
            motor.get_rotor_velocity(False)
            if use_rotor_velocity
            else motor.get_velocity(False)
        )
        velocity_signal.set_update_frequency(signal_rate_hz)
        rpm_publisher = self._table.getDoubleTopic(f"{name}/RPM").publish()
        cur_publisher = self._table.getDoubleTopic(f"{name}/A").publish()
        self._entries.append((name, velocity_signal, rpm_publisher))
        self._signals.append(velocity_signal)

    def update(self) -> None:
        """Refresh and publish all registered mechanism RPM values."""
        if not self._signals:
            return

        BaseStatusSignal.refresh_all(self._signals)

        for name, velocity_signal, rpm_publisher in self._entries:
            rpm = velocity_signal.value * 60.0
            rpm_publisher.set(rpm)
            SignalLogger.write_double(f"Mechanism/{name}/RPM", rpm, "rpm")

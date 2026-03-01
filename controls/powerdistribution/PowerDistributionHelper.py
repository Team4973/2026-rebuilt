from wpilib import PowerDistribution


class PowerDistributionHelper:
    def __init__(
        self,
        can_id: int = 1,
        module_type: PowerDistribution.ModuleType = PowerDistribution.ModuleType.kRev,
        channel_count: int | None = None,
    ) -> None:
        self._power_distribution = PowerDistribution(can_id, module_type)
        self.channel_count = (
            channel_count
            if channel_count is not None
            else (24 if module_type == PowerDistribution.ModuleType.kRev else 16)
        )

        self.sys_voltage = 0.0
        self.total_current = 0.0
        self.pdh_temp = 0.0
        self.channel_currents = [0.0] * self.channel_count

    def update(self) -> None:
        self.sys_voltage = self._power_distribution.getVoltage()
        self.total_current = self._power_distribution.getTotalCurrent()
        self.pdh_temp = self._power_distribution.getTemperature()

        for channel in range(self.channel_count):
            current = self._power_distribution.getCurrent(channel)
            self.channel_currents[channel] = current
            setattr(self, f"pdCh{channel}Current", current)

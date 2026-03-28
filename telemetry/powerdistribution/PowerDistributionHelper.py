from dataclasses import dataclass

from wpilib import PowerDistribution


@dataclass(slots=True)
class PowerDistributionSnapshot:
    voltage: float
    total_current: float
    temperature: float
    switchable_channel: bool
    channel_currents: list[float]
    breaker_faults: list[bool]
    sticky_breaker_faults: list[bool]
    active_faults: list[str]
    active_sticky_faults: list[str]
    version: str


class PowerDistributionHelper:
    def __init__(
        self,
        module_id: int = 1,
        module_type: PowerDistribution.ModuleType = PowerDistribution.ModuleType.kRev,
    ) -> None:
        self._power_distribution = PowerDistribution(module_id, module_type)

    def read(self) -> PowerDistributionSnapshot:
        faults = self._power_distribution.getFaults()
        sticky_faults = self._power_distribution.getStickyFaults()
        num_channels = self._power_distribution.getNumChannels()

        return PowerDistributionSnapshot(
            voltage=self._power_distribution.getVoltage(),
            total_current=self._power_distribution.getTotalCurrent(),
            temperature=self._power_distribution.getTemperature(),
            switchable_channel=self._power_distribution.getSwitchableChannel(),
            channel_currents=self._power_distribution.getAllCurrents(),
            breaker_faults=[
                faults.getBreakerFault(channel) for channel in range(num_channels)
            ],
            sticky_breaker_faults=[
                sticky_faults.getBreakerFault(channel)
                for channel in range(num_channels)
            ],
            active_faults=self._get_active_fault_names(
                faults,
                ("Brownout", "CanWarning", "HardwareFault"),
            ),
            active_sticky_faults=self._get_active_fault_names(
                sticky_faults,
                (
                    "Brownout",
                    "CanBusOff",
                    "CanWarning",
                    "FirmwareFault",
                    "HardwareFault",
                    "HasReset",
                ),
            ),
            version=self._format_version(),
        )

    def _format_version(self) -> str:
        version = self._power_distribution.getVersion()
        return (
            f"fw={version.FirmwareMajor}.{version.FirmwareMinor}.{version.FirmwareFix}, "
            f"hw={version.HardwareMajor}.{version.HardwareMinor}, "
            f"uid={version.UniqueId}"
        )

    @staticmethod
    def _get_active_fault_names(
        fault_data: object,
        attribute_names: tuple[str, ...],
    ) -> list[str]:
        return [
            attribute_name
            for attribute_name in attribute_names
            if bool(getattr(fault_data, attribute_name, 0))
        ]

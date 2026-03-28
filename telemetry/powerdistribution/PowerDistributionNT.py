from ntcore import NetworkTableInstance, PubSubOptions

from telemetry.powerdistribution.PowerDistributionHelper import PowerDistributionHelper


class PowerDistributionNT:
    def __init__(
        self,
        helper: PowerDistributionHelper,
        nt_instance: NetworkTableInstance | None = None,
    ) -> None:
        self._helper = helper
        self._table = (nt_instance or NetworkTableInstance.getDefault()).getTable(
            "PowerDistribution"
        )

        options = PubSubOptions(keepDuplicates=True)
        self._total_current_publisher = (
            self._table.getDoubleTopic("TotalCurrent").publish(options)
        )
        self._voltage_publisher = self._table.getDoubleTopic("Voltage").publish(options)
        self._temperature_publisher = (
            self._table.getDoubleTopic("Temperature").publish(options)
        )
        self._switchable_channel_publisher = (
            self._table.getBooleanTopic("SwitchableChannel").publish(options)
        )
        self._channel_currents_publisher = (
            self._table.getDoubleArrayTopic("ChannelCurrents").publish(options)
        )
        self._breaker_faults_publisher = (
            self._table.getBooleanArrayTopic("BreakerFaults").publish(options)
        )
        self._sticky_breaker_faults_publisher = (
            self._table.getBooleanArrayTopic("StickyBreakerFaults").publish(options)
        )
        self._active_faults_publisher = (
            self._table.getStringArrayTopic("ActiveFaults").publish(options)
        )
        self._active_sticky_faults_publisher = (
            self._table.getStringArrayTopic("ActiveStickyFaults").publish(options)
        )
        self._version_publisher = self._table.getStringTopic("Version").publish(options)

    def publish_values(self) -> None:
        snapshot = self._helper.read()

        self._total_current_publisher.set(snapshot.total_current)
        self._voltage_publisher.set(snapshot.voltage)
        self._temperature_publisher.set(snapshot.temperature)
        self._switchable_channel_publisher.set(snapshot.switchable_channel)
        self._channel_currents_publisher.set(snapshot.channel_currents)
        self._breaker_faults_publisher.set(snapshot.breaker_faults)
        self._sticky_breaker_faults_publisher.set(snapshot.sticky_breaker_faults)
        self._active_faults_publisher.set(snapshot.active_faults)
        self._active_sticky_faults_publisher.set(snapshot.active_sticky_faults)
        self._version_publisher.set(snapshot.version)

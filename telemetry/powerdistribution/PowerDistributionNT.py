import PowerDistributionHelper

from ntcore import DoubleTopic, PubSubOptions

class PowerDistributionNT:
    def __init__(self, 
                 pdTopicCurrent: DoubleTopic, 
                 pdTopicVoltage: DoubleTopic,
                 pdTopicFaults: DoubleTopic,
                 pdTopicVersion: DoubleTopic,):
        # Create publishers for each topic
        self.pdPub_TotalCurrent = pdTopicCurrent.publish(PubSubOptions(keepDuplicates=True))
        self.pdPub_Voltage = pdTopicVoltage.publish(PubSubOptions(keepDuplicates=True))
        self.pdPub_Version = pdTopicVersion.publish(PubSubOptions(keepDuplicates=True))
        self.pdPub_Faults = pdTopicFaults.publish(PubSubOptions(keepDuplicates=True))

    def publishValues(self):
        # Publish total current
        self.pdPub_TotalCurrent.set(PowerDistributionHelper.totalCurrent)
        
        # Publish voltage
        self.pdPub_Voltage.set(PowerDistributionHelper.voltage)

        # Publish version
        self.pdPub_Version.set(PowerDistributionHelper.pdmVersion)

        # Publish faults
        self.pdPub_Faults.set(PowerDistributionHelper.pdmFaults)
       
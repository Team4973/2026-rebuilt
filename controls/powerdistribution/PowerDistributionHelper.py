from wpilib import PowerDistribution

class PowerDistributionHelper:
    def __init__(self, can_id: int = 1) -> None:
        self.pdh = PowerDistribution(can_id, PowerDistribution.ModuleType.kRev)

        self.sys_voltage = 0.0
        self.total_current = 0.0

    def update(self) -> None:
        self.sys_voltage = self.pdh.getVoltage()
        self.total_current = self.pdh.getTotalCurrent()
        self.pdh_temp = self.pdh.getTemperature()

        self.pdCh0Current = self.pdh.getCurrent(0)
        self.pdCh1Current = self.pdh.getCurrent(1)
        self.pdCh2Current = self.pdh.getCurrent(2)
        self.pdCh3Current = self.pdh.getCurrent(3)
        self.pdCh4Current = self.pdh.getCurrent(4)
        self.pdCh5Current = self.pdh.getCurrent(5)
        self.pdCh6Current = self.pdh.getCurrent(6)
        self.pdCh7Current = self.pdh.getCurrent(7)
        self.pdCh8Current = self.pdh.getCurrent(8)
        self.pdCh9Current = self.pdh.getCurrent(9)
        self.pdCh10Current = self.pdh.getCurrent(10)
        self.pdCh11Current = self.pdh.getCurrent(11)
        self.pdCh12Current = self.pdh.getCurrent(12)
        self.pdCh13Current = self.pdh.getCurrent(13)
        self.pdCh14Current = self.pdh.getCurrent(14)
        self.pdCh15Current = self.pdh.getCurrent(15)
        self.pdCh16Current = self.pdh.getCurrent(16)
        self.pdCh17Current = self.pdh.getCurrent(17)
        self.pdCh18Current = self.pdh.getCurrent(18)
        self.pdCh19Current = self.pdh.getCurrent(19)
        self.pdCh20Current = self.pdh.getCurrent(20)
        self.pdCh21Current = self.pdh.getCurrent(21)
        self.pdCh22Current = self.pdh.getCurrent(22)
        self.pdCh23Current = self.pdh.getCurrent(23)
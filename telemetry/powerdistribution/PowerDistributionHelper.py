from wpilib import PowerDistribution

pdm = PowerDistribution(1, PowerDistribution.ModuleType.kRev)


# gets voltage of pdm, increments of 0.05V
voltage = pdm.getVoltage()

# gets the total current 
totalCurrent = pdm.getTotalCurrent()

# gets the total energy
pdmVersion = pdm.getVersion()

# read faults
pdmFaults = pdm.getFaults()

# gets the current reported on each channel of the pdmH (1-24)
channel1current = pdm.getCurrent(1)
channel2current = pdm.getCurrent(2)
channel3current = pdm.getCurrent(3)
channel4current = pdm.getCurrent(4)
channel5current = pdm.getCurrent(5)
channel6current = pdm.getCurrent(6)
channel7current = pdm.getCurrent(7)
channel8current = pdm.getCurrent(8)
channel9current = pdm.getCurrent(9)
channel10current = pdm.getCurrent(10)
channel11current = pdm.getCurrent(11)
channel12current = pdm.getCurrent(12)
channel13current = pdm.getCurrent(13)
channel14current = pdm.getCurrent(14)
channel15current = pdm.getCurrent(15)
channel16current = pdm.getCurrent(16)
channel17current = pdm.getCurrent(17)
channel18current = pdm.getCurrent(18)
channel19current = pdm.getCurrent(19)
channel20current = pdm.getCurrent(20)
channel21current = pdm.getCurrent(21)
channel22current = pdm.getCurrent(22)
channel23current = pdm.getCurrent(23)
channel24current = pdm.getCurrent(24)
from wpilib import SendableChooser, SmartDashboard

from autos.position1 import position1_auto
from autos.position2 import position2_auto
from autos.position3 import position3_auto


def build_auto_chooser(container) -> SendableChooser:
    """Build a SendableChooser with all autonomous routines and publish to dashboard."""
    chooser = SendableChooser()
    chooser.setDefaultOption("Position 1", position1_auto(container))
    chooser.addOption("Position 2", position2_auto(container))
    chooser.addOption("Position 3", position3_auto(container))
    SmartDashboard.putData("Auto Chooser", chooser)
    return chooser
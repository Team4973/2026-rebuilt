from wpilib import DriverStation
from wpimath.geometry import Translation2d


# Hopper geometric centers — midpoint of all 8 AprilTags on each hopper
# Red: X = (11.312 + 12.519) / 2 = 11.916, Y = (3.431 + 4.638) / 2 = 4.035
# Blue: X = (4.022 + 5.229) / 2 = 4.626, Y = (3.431 + 4.638) / 2 = 4.035
HOPPER_POSITIONS = {
    DriverStation.Alliance.kRed: Translation2d(11.916, 4.035),
    DriverStation.Alliance.kBlue: Translation2d(4.626, 4.035),
}

# Calibrated distance (meters) → launcher RPS lookup.
# Sorted by distance. Interpolates linearly between points.
# Known good: 60 RPS at ~1.57m (62 inches from hopper edge).
# Other values are placeholders — calibrate on the field.
DISTANCE_RPS_POINTS: list[tuple[float, float]] = [
    (1.0, 45.0),  # close range
    (1.57, 60.0),  # known good
    (2.5, 72.0),  # far — calibrate
    (3.5, 80.0),  # max range — calibrate
]


def interpolate_rps(distance_m: float) -> float:
    """Linear interpolation between calibrated distance/RPS points.

    Clamps to the first/last entry if distance is outside the table range.
    """
    table = DISTANCE_RPS_POINTS
    if distance_m <= table[0][0]:
        return table[0][1]
    if distance_m >= table[-1][0]:
        return table[-1][1]

    for i in range(len(table) - 1):
        d0, rps0 = table[i]
        d1, rps1 = table[i + 1]
        if d0 <= distance_m <= d1:
            t = (distance_m - d0) / (d1 - d0)
            return rps0 + t * (rps1 - rps0)

    return table[-1][1]


def get_hopper_position() -> Translation2d:
    """Return the hopper position for the current alliance. Defaults to blue."""
    alliance = DriverStation.getAlliance()
    if alliance is not None:
        return HOPPER_POSITIONS.get(
            alliance, HOPPER_POSITIONS[DriverStation.Alliance.kBlue]
        )
    return HOPPER_POSITIONS[DriverStation.Alliance.kBlue]

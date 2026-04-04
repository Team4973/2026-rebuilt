import commands2
from commands2 import cmd
from phoenix6 import swerve
from wpilib import DriverStation
from wpimath.geometry import Pose2d, Rotation2d

_FIELD_LENGTH = 16.541
_STARTING_X_BLUE = 4.03
_STARTING_X_RED = _FIELD_LENGTH - _STARTING_X_BLUE

# Position 2: center (Y≈4.0 for both alliances)
# Blue faces 0° (toward red wall), red faces 180° (toward blue wall).
_BLUE_POSE = Pose2d(_STARTING_X_BLUE, 4.0, Rotation2d.fromDegrees(0))
_RED_POSE = Pose2d(_STARTING_X_RED, 4.0, Rotation2d.fromDegrees(180))


def _get_starting_pose() -> Pose2d:
    alliance = DriverStation.getAlliance()
    if alliance == DriverStation.Alliance.kRed:
        return _RED_POSE
    return _BLUE_POSE


def position2_auto(container) -> commands2.Command:
    """Starting position 2 (center).

    Resets pose to estimated start, drives forward slowly for 3 seconds, then idles.
    """
    idle = swerve.requests.Idle()
    drive = (
        swerve.requests.FieldCentric()
        .with_drive_request_type(
            swerve.SwerveModule.DriveRequestType.OPEN_LOOP_VOLTAGE
        )
    )

    return cmd.sequence(
        container.drivetrain.runOnce(
            lambda: container.drivetrain.reset_pose(_get_starting_pose())
        ),
        container.drivetrain.apply_request(
            lambda: drive.with_velocity_x(0.5).with_velocity_y(0).with_rotational_rate(0)
        ).withTimeout(3.0),
        container.drivetrain.apply_request(lambda: idle),
    ).withName("Position 2")
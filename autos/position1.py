import math

import commands2
from commands2 import cmd
from phoenix6 import swerve
from wpimath.geometry import Pose2d, Rotation2d

from autos.drive_to_pose import DriveToPose
from subsystems.launcher_config import get_hopper_position

# Field: 16.541m x 8.069m. Starting line is 4.03m from each alliance wall.
# All poses are in blue-alliance coordinates.
# Headings: 0° = +X (toward red wall), 90° = +Y, -90° = -Y (toward field center).
_TRENCH_Y = 7.2  # High-Y trench underpass center (safe range 6.7-7.8)
_MIDLINE_X = 8.0  # Just inside the fuel rectangle (rect starts ~X=7.35)
_STARTING_X = 4.03
_ALLIANCE_X = 4.5  # Safe position on alliance side of trench

# Heading constants
_FACING_FORWARD = Rotation2d.fromDegrees(0)    # +X, toward red wall
_FACING_CENTER = Rotation2d.fromDegrees(-90)   # -Y, toward field center

# Fuel rectangle centered on midline, ~5.23m wide in Y, centered at Y≈4.0.
# From trench side, the near edge of the fuel is around Y≈6.6.
# Drive to Y≈5.5 to get solidly into the fuel.
_FUEL_Y = 5.5

# After clearing trench, move away from guardrail to launch.
_LAUNCH_Y = 6.0

_STARTING_POSE = Pose2d(_STARTING_X, _TRENCH_Y, _FACING_FORWARD)


def _heading_to_hopper(container) -> Rotation2d:
    """Heading from robot to hopper in blue-alliance field coordinates."""
    hopper = get_hopper_position()
    pose = container.drivetrain.get_state().pose
    return Rotation2d(hopper.x - pose.x, hopper.y - pose.y)


def position1_auto(container) -> commands2.Command:
    """Position 1 auto (BLUE alliance): collect fuel through trench, launch.

    Path (all coordinates in blue-alliance field frame):
    1. Start at (4.03, 7.2), facing +X
    2. Jerk backward to drop intake arm
    3. Drive under trench to midline (8.0, 7.2), facing +X, arm held down
    4. Turn to face center (-90°), drive into fuel rectangle (8.0, 5.5)
    5. Return to trench corridor (8.0, 7.2), still facing center (-90°)
    6. Drive back through trench (4.5, 7.2), facing center (-90°), arm down
    7. Move away from edge (4.5, 6.0), face hopper
    8. Launch fuel into hopper
    """
    idle = swerve.requests.Idle()
    drive = (
        swerve.requests.FieldCentric()
        .with_drive_request_type(
            swerve.SwerveModule.DriveRequestType.OPEN_LOOP_VOLTAGE
        )
        .with_forward_perspective(
            swerve.requests.ForwardPerspectiveValue.BLUE_ALLIANCE
        )
    )

    face_hub = (
        swerve.requests.FieldCentricFacingAngle()
        .with_drive_request_type(
            swerve.SwerveModule.DriveRequestType.OPEN_LOOP_VOLTAGE
        )
        .with_forward_perspective(
            swerve.requests.ForwardPerspectiveValue.BLUE_ALLIANCE
        )
    )
    face_hub.heading_controller.setPID(-7.0, 0, 0)
    face_hub.heading_controller.enableContinuousInput(-math.pi, math.pi)

    def drive_to(pose: Pose2d, max_speed: float = 2.0, timeout: float = 4.0):
        return DriveToPose(
            container.drivetrain, pose, max_speed=max_speed
        ).withTimeout(timeout)

    return cmd.sequence(
        # 1. Reset pose to starting position
        container.drivetrain.runOnce(
            lambda: container.drivetrain.reset_pose(_STARTING_POSE)
        ),

        # 2. Jerk backward to drop intake arm
        container.drivetrain.apply_request(
            lambda: drive.with_velocity_x(-2.0)
            .with_velocity_y(0)
            .with_rotational_rate(0)
        ).withTimeout(0.3),

        # 3. Drive under trench to midline, heading forward, arm held down
        cmd.deadline(
            drive_to(
                Pose2d(_MIDLINE_X, _TRENCH_Y, _FACING_FORWARD),
                max_speed=1.5, timeout=5.0,
            ),
            container.intake_arm.run(
                lambda: container.intake_arm.set_speed(0.3)
            ),
        ),

        # 4. Face center and drive into fuel rectangle, intake running
        cmd.deadline(
            drive_to(
                Pose2d(_MIDLINE_X, _FUEL_Y, _FACING_CENTER),
                max_speed=1.0, timeout=3.0,
            ),
            container.intake.run(
                lambda: container.intake.set_speed(-0.5)
            ),
            container.intake_arm.run(
                lambda: container.intake_arm.set_speed(0.3)
            ),
        ),

        # 5. Return to trench corridor, still facing center, intake running
        cmd.deadline(
            drive_to(
                Pose2d(_MIDLINE_X, _TRENCH_Y, _FACING_CENTER),
                max_speed=1.5, timeout=3.0,
            ),
            container.intake.run(
                lambda: container.intake.set_speed(-0.5)
            ),
            container.intake_arm.run(
                lambda: container.intake_arm.set_speed(0.3)
            ),
        ),

        # 6. Drive back through trench to alliance side, facing center, arm down
        cmd.deadline(
            drive_to(
                Pose2d(_ALLIANCE_X, _TRENCH_Y, _FACING_CENTER),
                max_speed=1.5, timeout=4.0,
            ),
            container.intake_arm.run(
                lambda: container.intake_arm.set_speed(0.3)
            ),
        ),

        # 7. Stop intake and arm
        cmd.parallel(
            container.intake.runOnce(container.intake.stop),
            container.intake_arm.runOnce(container.intake_arm.stop),
        ),

        # 8. Move away from edge, face hopper, spin up launcher
        cmd.parallel(
            drive_to(
                Pose2d(_ALLIANCE_X, _LAUNCH_Y, _FACING_CENTER),
                max_speed=1.0, timeout=2.0,
            ),
            container.launcher.run(
                lambda: container.launcher.set_velocity(
                    container.launcher.get_target_rps()
                )
            ),
        ),

        # 9. Aim at hopper and launch
        cmd.parallel(
            container.launcher.run(
                lambda: container.launcher.set_velocity(
                    container.launcher.get_target_rps()
                )
            ),
            container.feeder.run(lambda: container.feeder.set_speed(-0.5)),
            container.drivetrain.apply_request(
                lambda: face_hub
                .with_velocity_x(0)
                .with_velocity_y(0)
                .with_target_direction(_heading_to_hopper(container))
            ),
        ).withTimeout(3.0),

        # 10. Stop launcher and feeder
        cmd.parallel(
            container.launcher.runOnce(container.launcher.stop),
            container.feeder.runOnce(container.feeder.stop),
        ),

        # 11. Idle for remainder of auto
        container.drivetrain.apply_request(lambda: idle),
    ).withName("Position 1")
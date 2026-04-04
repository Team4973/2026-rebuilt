import math

import commands2
from phoenix6 import swerve
from wpimath.controller import PIDController
from wpimath.geometry import Pose2d


class DriveToPose(commands2.Command):
    """Drive the swerve drivetrain to an absolute field pose using PID control.

    Uses two PIDControllers for X/Y translation and FieldCentricFacingAngle
    for heading, all in blue-alliance field coordinates so behavior is
    consistent regardless of alliance.
    """

    def __init__(
        self,
        drivetrain,
        target: Pose2d,
        max_speed: float = 2.0,
        position_tolerance: float = 0.10,
        heading_tolerance_deg: float = 3.0,
    ):
        super().__init__()
        self._drivetrain = drivetrain
        self._target = target
        self._max_speed = max_speed

        self._x_pid = PIDController(3.0, 0.0, 0.1)
        self._y_pid = PIDController(3.0, 0.0, 0.1)
        self._x_pid.setTolerance(position_tolerance)
        self._y_pid.setTolerance(position_tolerance)

        self._request = (
            swerve.requests.FieldCentricFacingAngle()
            .with_drive_request_type(
                swerve.SwerveModule.DriveRequestType.OPEN_LOOP_VOLTAGE
            )
            .with_forward_perspective(
                swerve.requests.ForwardPerspectiveValue.BLUE_ALLIANCE
            )
        )
        self._request.heading_controller.setPID(-7.0, 0.0, 0.0)
        self._request.heading_controller.enableContinuousInput(
            -math.pi, math.pi
        )

        self._heading_tolerance = math.radians(heading_tolerance_deg)
        self.addRequirements(drivetrain)

    def initialize(self):
        self._x_pid.reset()
        self._y_pid.reset()

    def execute(self):
        pose = self._drivetrain.get_state().pose
        vx = self._x_pid.calculate(pose.x, self._target.x)
        vy = self._y_pid.calculate(pose.y, self._target.y)

        # Clamp to max speed
        vx = max(-self._max_speed, min(self._max_speed, vx))
        vy = max(-self._max_speed, min(self._max_speed, vy))

        self._drivetrain.set_control(
            self._request
            .with_velocity_x(vx)
            .with_velocity_y(vy)
            .with_target_direction(self._target.rotation())
        )

    def isFinished(self) -> bool:
        pose = self._drivetrain.get_state().pose
        heading_error = abs(
            (pose.rotation() - self._target.rotation()).radians()
        )
        return (
            self._x_pid.atSetpoint()
            and self._y_pid.atSetpoint()
            and heading_error < self._heading_tolerance
        )

    def end(self, interrupted: bool):
        self._drivetrain.set_control(swerve.requests.SwerveDriveBrake())
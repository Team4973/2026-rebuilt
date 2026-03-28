#
# Copyright (c) FIRST and other WPILib contributors.
# Open Source Software; you can modify and/or share it under the terms of
# the WPILib BSD license file in the root directory of this project.
#

import commands2
from commands2 import cmd
from commands2.button import CommandXboxController, Trigger

from generated.tuner_constants import TunerConstants
from subsystems.launcher import Launcher
from subsystems.launcher_config import get_hopper_position, interpolate_rps
from subsystems.feeder import Feeder
from subsystems.intake.intake import Intake
from subsystems.intake.intake_arm import Intake_Arm
from subsystems.vision import Vision
from telemetry import telemetry

from phoenix6 import swerve
from wpilib import DriverStation
from wpimath.geometry import Rotation2d
from wpimath.units import rotationsToRadians
from wpimath.filter import SlewRateLimiter


class RobotContainer:
    """
    This class is where the bulk of the robot should be declared. Since Command-based is a
    "declarative" paradigm, very little robot logic should actually be handled in the :class:`.Robot`
    periodic methods (other than the scheduler calls). Instead, the structure of the robot (including
    subsystems, commands, and button mappings) should be declared here.
    """

    def __init__(self) -> None:
        self.x_limiter = SlewRateLimiter(4)
        self.y_limiter = SlewRateLimiter(4)
        self.rot_limiter = SlewRateLimiter(4)

        self._max_speed = (
            1.0 * TunerConstants.speed_at_12_volts
        )  # speed_at_12_volts desired top speed
        self._max_angular_rate = rotationsToRadians(
            0.75
        )  # 3/4 of a rotation per second max angular velocity

        # Setting up bindings for necessary control of the swerve drive platform
        self._drive = (
            swerve.requests.FieldCentric()
            .with_deadband(self._max_speed * 0.1)
            .with_rotational_deadband(
                self._max_angular_rate * 0.1
            )  # Add a 10% deadband
            .with_drive_request_type(
                swerve.SwerveModule.DriveRequestType.OPEN_LOOP_VOLTAGE
            )  # Use open-loop control for drive motors
        )
        self._brake = swerve.requests.SwerveDriveBrake()
        self._point = swerve.requests.PointWheelsAt()

        self._logger = telemetry.Telemetry(self._max_speed)

        self._joystick = CommandXboxController(0)

        self.drivetrain = TunerConstants.create_drivetrain()
        self.launcher = Launcher(33)
        self.feeder = Feeder(32)
        self.intake = Intake()
        self.intake_arm = Intake_Arm()
        self.vision = Vision(self.drivetrain)

        # Configure the button bindings
        self.configureButtonBindings()

    def configureButtonBindings(self) -> None:
        """
        Use this method to define your button->command mappings. Buttons can be created by
        instantiating a :GenericHID or one of its subclasses (Joystick or XboxController),
        and then passing it to a JoystickButton.
        """

        # Note that X is defined as forward according to WPILib convention,
        # and Y is defined as to the left according to WPILib convention.
        self.drivetrain.setDefaultCommand(
            # Drivetrain will execute this command periodically
            self.drivetrain.apply_request(
                lambda: (
                    self._drive.with_velocity_x(
                        self.x_limiter.calculate(
                            self._joystick.getLeftY() * self._max_speed
                        )
                    )  # Drive forward with negative Y (forward)
                    .with_velocity_y(
                        self.y_limiter.calculate(
                            self._joystick.getLeftX() * self._max_speed
                        )
                    )  # Drive left with negative X (left)
                    .with_rotational_rate(
                        -self.rot_limiter.calculate(
                            self._joystick.getRightX() * self._max_angular_rate
                        )
                    )  # Drive counterclockwise with negative X (left)
                )
            )
        )

        # Idle while the robot is disabled. This ensures the configured
        # neutral mode is applied to the drive motors while disabled.
        idle = swerve.requests.Idle()
        Trigger(DriverStation.isDisabled).whileTrue(
            self.drivetrain.apply_request(lambda: idle).ignoringDisable(True)
        )
        self._joystick.a().whileTrue(self.drivetrain.apply_request(lambda: self._brake))
        self._joystick.b().whileTrue(
            self.drivetrain.apply_request(
                lambda: self._point.with_module_direction(
                    Rotation2d(self._joystick.getLeftY(), self._joystick.getLeftX())
                )
            )
        )

        # CONTROLS

        # X: Seed Field Centric/Reset Position
        self._joystick.x().onTrue(
            self.drivetrain.runOnce(self.drivetrain.seed_field_centric)
        )

        # Right trigger: Run launcher at adjustable target velocity
        self._joystick.rightTrigger(0.1).whileTrue(
            self.launcher.run(
                lambda: self.launcher.set_velocity(self.launcher.get_target_rps())
            )
        ).onFalse(self.launcher.runOnce(self.launcher.stop))

        # Right bumper: Hold Intake
        self._joystick.rightBumper().whileTrue(
            self.intake.run(lambda: self.intake.set_speed(-0.5))
        ).onFalse(self.intake.runOnce(self.intake.stop))

        # Y: Intake arm down
        self._joystick.y().whileTrue(
            self.intake_arm.run(lambda: self.intake_arm.set_speed(0.8))
        ).onFalse(self.intake_arm.runOnce(self.intake_arm.stop))

        self.drivetrain.register_telemetry(self._update_telemetry)

        # Left trigger: Arm Launcher & Feeder
        self._joystick.leftTrigger(0.1).whileTrue(
            cmd.parallel(
                self.feeder.run(lambda: self.feeder.set_speed(-0.5)),
                self.launcher.run(
                    lambda: self.launcher.set_velocity(self.launcher.get_target_rps())
                ),
            )
        ).onFalse(
            cmd.parallel(
                self.feeder.runOnce(self.feeder.stop),
                self.launcher.runOnce(self.launcher.stop),
            )
        )

        # D-pad left/right: Nudge launcher speed down/up
        self._joystick.povLeft().onTrue(
            self.launcher.runOnce(self.launcher.nudge_speed_down)
        )
        self._joystick.povRight().onTrue(
            self.launcher.runOnce(self.launcher.nudge_speed_up)
        )

        # Back button: Toggle auto/manual launcher speed mode
        self._joystick.back().onTrue(
            self.launcher.runOnce(self.launcher.toggle_auto_mode)
        )

    def _update_telemetry(self, state) -> None:
        """Called every drivetrain cycle. Updates telemetry and auto launcher speed."""
        self._logger.telemeterize(state)

        # Calculate distance to hopper and update auto launcher RPS
        hopper = get_hopper_position()
        distance = state.pose.translation().distance(hopper)
        auto_rps = interpolate_rps(distance)
        self.launcher.set_auto_rps(auto_rps)
        self.launcher.set_distance_to_hopper(distance)

    def getAutonomousCommand(self) -> commands2.Command:
        """
        Use this to pass the autonomous command to the main {@link Robot} class.

        :returns: the command to run in autonomous
        """
        # Simple drive forward auton
        idle = swerve.requests.Idle()
        return cmd.sequence(
            # Reset our field centric heading to match the robot
            # facing away from our alliance station wall (0 deg).
            self.drivetrain.runOnce(
                lambda: self.drivetrain.seed_field_centric(Rotation2d.fromDegrees(0))
            ),
            # Then slowly drive forward (away from us) for 5 seconds.
            self.drivetrain.apply_request(
                lambda: (
                    self._drive.with_velocity_x(0.5)
                    .with_velocity_y(0)
                    .with_rotational_rate(0)
                )
            ).withTimeout(5.0),
            # Finally idle for the rest of auton
            self.drivetrain.apply_request(lambda: idle),
        )

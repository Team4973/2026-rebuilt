from commands2 import Subsystem
from phoenix6 import utils
from robotpy_apriltag import AprilTagField, AprilTagFieldLayout
from wpilib import SmartDashboard
from wpimath.geometry import Rotation3d, Transform3d, Translation3d

from subsystems.command_swerve_drivetrain import CommandSwerveDrivetrain


class Vision(Subsystem):
    """Subsystem that uses PhotonVision for AprilTag-based pose estimation."""

    # Camera mount position relative to robot center
    # Adjust these to match your actual camera placement
    ROBOT_TO_CAMERA = Transform3d(
        Translation3d(-0.1, 0.254, 0.46),  # 10cm back, 25.4cm left, 46cm up from center
        Rotation3d(0, 0, 0),  # no tilt, forward looking
    )

    CAMERA_NAME = "front_camera"

    def __init__(self, drivetrain: CommandSwerveDrivetrain) -> None:
        super().__init__()
        self._drivetrain = drivetrain
        self._camera = None
        self._estimator = None

        self._field_layout = AprilTagFieldLayout.loadField(
            AprilTagField.k2026RebuiltWelded
        )

        # PhotonCamera spawns a TimeSyncServer thread that can slow down
        # robotInit beyond the pyfrc 2-second test timeout. Only create
        # the camera when running on a real robot or in sim mode (not tests).
        import os
        import sys

        running_tests = (
            "pytest" in sys.modules
            or "pyfrc" in sys.modules
            or "ROBOTPY_TEST" in os.environ
            or os.environ.get("PYTEST_CURRENT_TEST") is not None
        )
        if not running_tests:
            from photonlibpy import PhotonCamera, PhotonPoseEstimator

            self._camera = PhotonCamera(self.CAMERA_NAME)
            self._estimator = PhotonPoseEstimator(
                self._field_layout,
                self.ROBOT_TO_CAMERA,
            )

        self._vision_update_count = 0

        # Simulation support — full vision sim when not in test mode
        if utils.is_simulation() and self._camera is not None:
            self._init_sim()

    def _init_sim(self) -> None:
        from photonlibpy.simulation import (
            PhotonCameraSim,
            SimCameraProperties,
            VisionSystemSim,
        )

        self._vision_sim = VisionSystemSim("main")
        self._vision_sim.addAprilTags(self._field_layout)

        cam_props = SimCameraProperties.PERFECT_90DEG()
        self._camera_sim = PhotonCameraSim(self._camera, cam_props)
        self._camera_sim.setMaxSightRange(8.0)  # 8 meters max range

        self._vision_sim.addCamera(self._camera_sim, self.ROBOT_TO_CAMERA)

    def periodic(self) -> None:
        if self._camera is None:
            return

        results = self._camera.getAllUnreadResults()
        SmartDashboard.putNumber("Vision/ResultCount", len(results))

        for result in results:
            has_targets = result.hasTargets()
            targets = result.getTargets() if has_targets else []
            SmartDashboard.putBoolean("Vision/HasTargets", has_targets)
            SmartDashboard.putNumber("Vision/NumTargets", len(targets))
            if targets:
                best = targets[0]
                SmartDashboard.putNumber("Vision/BestTargetID", best.fiducialId)
                SmartDashboard.putNumber("Vision/BestTargetAmbiguity", best.poseAmbiguity)

            # Try multi-tag first, then single-tag, then PnP/trig solve
            multi_pose = self._estimator.estimateCoprocMultiTagPose(result)
            single_pose = self._estimator.estimateLowestAmbiguityPose(result)
            pnp_pose = self._estimator.estimatePnpDistanceTrigSolvePose(result)
            SmartDashboard.putBoolean("Vision/MultiTagOK", multi_pose is not None)
            SmartDashboard.putBoolean("Vision/SingleTagOK", single_pose is not None)
            SmartDashboard.putBoolean("Vision/PnpTrigOK", pnp_pose is not None)

            pose = multi_pose or single_pose or pnp_pose
            if pose is not None:
                self._vision_update_count += 1
                self._drivetrain.add_vision_measurement(
                    pose.estimatedPose.toPose2d(),
                    pose.timestampSeconds,
                )
                ep = pose.estimatedPose
                SmartDashboard.putString(
                    "Vision/EstPose",
                    f"({ep.x:.2f}, {ep.y:.2f})",
                )

        SmartDashboard.putBoolean("Vision/Connected", self._camera.isConnected())
        SmartDashboard.putNumber("Vision/UpdateCount", self._vision_update_count)

        # Publish the drivetrain's believed pose for debugging
        pose = self._drivetrain.get_state().pose
        SmartDashboard.putString(
            "Vision/RobotPose",
            f"({pose.x:.2f}, {pose.y:.2f}, {pose.rotation().degrees():.1f}°)",
        )

    def simulationPeriodic(self) -> None:
        if hasattr(self, "_vision_sim"):
            self._vision_sim.update(self._drivetrain.get_state().pose)

from wpimath.estimator import SwerveDrive4PoseEstimator
from wpimath.geometry import Pose2d, Rotation2d
from wpimath.kinematics import SwerveModulePosition
import ntcore

class PostEstimator:
    def __init__(self, drivetrain):
        self.drivetrain = drivetrain

        self.estimator = SwerveDrive4PoseEstimator(
            drivetrain.kinematics,
        )
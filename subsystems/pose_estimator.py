from wpimath.estimator import SwerveDrive4PoseEstimator

class PostEstimator:
    def __init__(self, drivetrain):
        self.drivetrain = drivetrain

        self.estimator = SwerveDrive4PoseEstimator(
            drivetrain.kinematics,
        )
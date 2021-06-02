from enum import Enum


class ObstacleSide(Enum):
    NO_SIDE = -1
    LEFT = 0
    RIGHT = 1


class ObstacleState(Enum):
    IDLE = 0
    DETECTED = 1
    AVOID_1 = 2
    AVOID_2 = 3
    SURVIVED = 4


class Obstacle:
    def __init__(self):
        self.state = ObstacleState.IDLE
        self.oam_active = False
        self.ofm_active = False
        self.oam_side = ObstacleSide.NO_SIDE
        self.oam_reset = 0
        self.oam_speed = [0, 0]
        self.ofm_speed = [0, 0]
        self.detected_location = None
        self.end_location = None

    def is_avoid(self, robot_location):
        return robot_location.is_close(self.end_location, delta=0.2)

    def reset(self):
        self.state = ObstacleState.IDLE
        self.oam_active = False
        self.ofm_active = False
        self.oam_side = ObstacleSide.NO_SIDE
        self.oam_reset = 0
        self.oam_speed = [0, 0]
        self.ofm_speed = [0, 0]
        self.detected_location = None
        self.end_location = None

    def __str__(self):
        return "RobotId: {}, Content: {}".format(self.robot_id, self.content)

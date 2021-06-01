from enum import Enum

class ObstacleSide(Enum):
    NO_SIDE = -1
    LEFT = 0
    RIGHT = 1


class Obstacle:
    def __init__(self):
        self.oam_active = False
        self.ofm_active = False
        self.oam_side = ObstacleSide.NO_SIDE
        self.oam_reset = 0
        self.oam_speed = [0, 0]
        self.ofm_speed = [0, 0]

    def __str__(self):
        return "RobotId: {}, Content: {}".format(self.robot_id, self.content)


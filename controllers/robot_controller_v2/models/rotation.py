import math

class Rotation:
    def __init__(self, rotations):
        if rotations is None:
            self.angle = 0
            return

        self.angle = rotations[3] * 180 / math.pi

    def __str__(self):
        return "angle: {}".format(self.angle)
       

import math
import util

class Rotation:
    def __init__(self, rotations):
        if rotations is None:
            self.angle = 0
            return
        self.angle =  util.normalize_degree(math.degrees(rotations[3]))

    def __str__(self):
        return "angle: {}".format(self.angle)
       

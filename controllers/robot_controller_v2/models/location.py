from math import atan2, degrees
import util


class Location:
    def __init__(self, locations):
        if locations is None:
            self.x = self.y = self.z = 0
            return

        self.x = round(locations[0], 4)
        self.y = round(locations[1], 4)
        self.z = round(locations[2], 4)

    def is_close(self, other, delta=0.2) -> bool:
        if util.is_close(self.x, other.x, delta) and util.is_close(self.z, other.z, delta):
            return True
        return False

    def subtract(self, location):
        return self._arithmetic_operator(location, lambda x, y: x-y)

    def add(self, location):
        return self._arithmetic_operator(location, lambda x, y: x+y)

    def _arithmetic_operator(self, location, operate):
        return Location([operate(self.x, location.x), operate(self.y, location.y), operate(self.z, location.z)])

    def compare(self, location):
        if location is None:
            return 0.0
        return self.z - location.z

    def calculate_degree_between(self, other):
        delta_x = other.x - self.x 
        delta_z = other.z - self.z

        rads = atan2(-delta_z, delta_x)
        degree = util.normalize_degree(degrees(rads)) + 90

        return degree

    def calculate_area(self, x, y):
        if x < 0 and y < 0:
            return 90
        else:
            return -90

    def __str__(self):
        return "x: {}, y: {}, z: {}".format(self.x, self.y, self.z)

    @staticmethod
    def from_coords(x, y, z):
        return Location([x, y, z])

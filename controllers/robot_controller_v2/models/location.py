class Location:
    def __init__(self, locations):
        if locations is None:
            self.x = self.y = self.z = 0
            return

        self.x = round(locations[0],4)
        self.y = round(locations[1],4)
        self.z = round(locations[2],4)

    def is_close(self, other, delta=0.2) -> bool:
        if (self.x <= other.x + delta and self.x >= other.x - delta) and (self.z <= other.z + delta and self.z >= other.z - delta):
            return True
        return False
    
    def subtract(self, location):
        return self._arithmetic_operator(location, lambda x,y: x-y)

    def add(self, location):
        return self._arithmetic_operator(location, lambda x,y: x+y)

    def _arithmetic_operator(self, location, operate):
        return Location([operate(self.x, location.x), operate(self.y, location.y), operate(self.z, location.z)])
    
    def compare(self, location):
        if location is None:
            return 0.0
        return self.z - location.z

    def __str__(self):
        return "x: {}, y: {}, z: {}".format(self.x, self.y, self.z)

    @staticmethod
    def from_coords(x, y, z):
        return Location([x, y, z])

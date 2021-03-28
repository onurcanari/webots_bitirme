class Location:
    def __init__(self):
        self.x = self.y = self.z = 0

    def __init__(self, locations):
        self.x = locations[0]
        self.y = locations[1]
        self.z = locations[2]

    def is_close(other, delta=0.2) -> bool:
        if (x <= other.x + delta and x >= other.x - delta) and (z <= other.z + delta and z >= other.z - delta):
            return true;
        return false;

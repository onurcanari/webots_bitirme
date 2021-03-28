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

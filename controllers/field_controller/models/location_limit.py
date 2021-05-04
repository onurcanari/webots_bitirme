from models.location import Location

class LocationLimit:
    def __init__(self, lower_limit: Location, upper_limit: Location):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def is_inside(self, loc):
        return True

    def __str__(self):
        return "Lower Limit : {}, Upper Limit : {}".format(self.lower_limit,self.upper_limit)

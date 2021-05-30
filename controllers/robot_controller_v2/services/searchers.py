import logging
import random

import numpy

from models.enums import SearchAlgorithms
from models.location import Location
from models.location_limit import LocationLimit

log = logging.getLogger()


class SearchService:
    DIVIDE_COUNT = 10

    def __init__(self, search_method):
        self.target_points: [TargetPoint] = None
        self.target_point_index = 0
        self.method = search_method
        log.debug("Searching with : {}".format(str(self.method.name)))

    @property
    def target_point(self):
        if len(self.target_points) - 1 == self.target_point_index:
            return None
        return self.target_points[self.target_point_index]

    def set_next_target(self, robot_loc: Location):
        if self.target_point is None:
            return None

        if self.target_point.location.is_close(robot_loc, delta=0.1):
            self.target_point.visited = True
            while self.target_point.visited is True:
                self.target_point_index += 1
                if self.target_point is None:
                    return None
            # log.debug("Next target : {} selected.".format(self.target_point))
            return True

        return False

    def calculate_target_location(self, robot_loc: Location):
        next_target_set = self.set_next_target(robot_loc)
        if next_target_set is None:
            return None

        not_visited_target_points = filter(lambda p: p.visited is False, self.target_points)

        for target_point in not_visited_target_points:
            if target_point.location.is_close(robot_loc, delta=0.3):
                target_point.visited = True

        return self.target_point.location

    def create_subdivisions(self, loc_limit: LocationLimit):
        first_column_z = numpy.flip(numpy.linspace(loc_limit.upper_limit.z, loc_limit.lower_limit.z, self.DIVIDE_COUNT))
        first_row_x = numpy.linspace(loc_limit.lower_limit.x, loc_limit.upper_limit.x, self.DIVIDE_COUNT)
        loc_points = []
        index = 0
        for x in first_row_x:
            column_z = first_column_z
            if index % 2 == 1:
                column_z = numpy.flip(first_column_z)
            for z in column_z:
                loc_points.append(Location.from_coords(x, 0, z))
            index += 1
        self.target_points = list(map(lambda loc: TargetPoint(loc), loc_points))
        self.target_point_index = 0

        if self.method == SearchAlgorithms.SEARCH_WITH_RAND_POINTS:
            random.shuffle(self.target_points)


class TargetPoint:
    def __init__(self, loc):
        self.visited = False
        self.location: Location = loc

    def __str__(self):
        return "loc: {}".format(self.location)

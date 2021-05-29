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
        return self.target_points[self.target_point_index]

    def set_next_target(self, robot_loc: Location):
        if len(self.target_points) - 1 == self.target_point_index:
            return None

        if self.target_point.location.is_close(robot_loc, delta=0.1):
            self.target_point.visited = True
            self.target_point_index += 1
            return True

        return False

    def calculate_target_location(self, robot_loc):
        next_target_set = self.set_next_target(robot_loc)
        if next_target_set is None:
            return None

        filter(lambda p: p.visited is False, self.target_points)

        return self.target_point.location


class SearchWithPointsService(SearchService):

    def __init__(self):
        super().__init__(SearchAlgorithms.SEARCH_WITH_RAND_POINTS)

    def create_subdivisions(self, loc_limit):
        field_size = loc_limit.lower_limit.z - loc_limit.upper_limit.z
        start_point = [loc_limit.lower_limit.x, loc_limit.lower_limit.z - field_size]
        points_between_distance = abs(start_point[0] - start_point[1]) / (self.DIVIDE_COUNT - 1)
        new_map = [[[0, 0] for i in range(self.DIVIDE_COUNT)] for j in range(self.DIVIDE_COUNT)]

        shuffle_field = []

        for y in range(self.DIVIDE_COUNT):
            for x in range(self.DIVIDE_COUNT):
                loc = Location([start_point[0] + round((points_between_distance * x), 2), 0,
                                start_point[1] + round((y * points_between_distance), 2)])
                new_map[y][x] = TargetPoint(loc)
                shuffle_field.append(new_map[y][x])

        upper_limit = shuffle_field[self.DIVIDE_COUNT - 1]
        del shuffle_field[self.DIVIDE_COUNT - 1]
        random.shuffle(shuffle_field)
        shuffle_field.append(upper_limit)

        self.target_points = shuffle_field
        self.target_point_index = 0


class SearchWithStepService(SearchService):

    def __init__(self):
        super().__init__(SearchAlgorithms.SEARCH_WITH_STEP)

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


class TargetPoint:
    def __init__(self, loc):
        self.visited = False
        self.location = loc

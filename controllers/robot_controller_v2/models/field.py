import numpy as np
from enum import Enum

from models.location import Location
from models.location_limit import LocationLimit


class FieldState(Enum):
    NONE = 0,
    BLOCKED = 1,
    SCANNED = 2,
    SCANNING = 3,
    CAN_BE_SCANNED = 4


class Field:
    def __init__(self, loc_limit: LocationLimit):
        self.state = FieldState.NONE
        self.loc_limit = loc_limit
        self.scanner = None

    def __str__(self):
        return "{}".format(self.loc_limit)


class FieldService:
    MAP_LENGTH = 20
    DELTA = 1

    def __init__(self, middle_loc: Location, offset: Location):
        self.fields: [Field] = [[0 for i in range(FieldService.MAP_LENGTH)] for j in range(FieldService.MAP_LENGTH)]
        middle_coords = [[0 for i in range(FieldService.MAP_LENGTH)] for j in range(FieldService.MAP_LENGTH)]
        firstSideX = middle_loc.x - (FieldService.MAP_LENGTH // 2 * offset.x)
        firstSideZ = middle_loc.z - (FieldService.MAP_LENGTH // 2 * offset.z)

        self.available_fields: [Field] = None

        for i in range(FieldService.MAP_LENGTH):
            for j in range(FieldService.MAP_LENGTH):
                middle_coords[i][j] = Location.from_coords(
                    firstSideX + j * offset.x, None, firstSideZ + i * offset.z)
                Location.from_coords(
                    middle_coords[i][j].x, None, middle_coords[i][j].z + offset.z / 2)
                lower_limit = Location.from_coords(x=middle_coords[i][j].x - offset.x / 2,
                                                   z=middle_coords[i][j].z + offset.z / 2)
                upper_limit = Location.from_coords(x=middle_coords[i][j].x + offset.x / 2,
                                                   z=middle_coords[i][j].z - offset.z / 2)
                self.fields[i][j] = Field(
                    loc_limit=LocationLimit(lower_limit, upper_limit))

    def get_middle(self):
        return self.fields[FieldService.MAP_LENGTH // 2][FieldService.MAP_LENGTH // 2]

    def change_field_state(self, x, y, new_state: FieldState):
        self.fields[x][y].state = new_state

        if not self.is_available_to_search():
            self.make_field_neighbors_available(FieldService.DELTA)

    def is_available_to_search(self) -> bool:
        available_fields = list(filter(lambda f: f.STATE == FieldState.CAN_BE_SCANNED, self.available_fields))
        if not available_fields:
            return False
        return True

    def make_field_neighbors_available(self, delta):
        self.delta = delta
        old_fields = self._calculate_neighbors(delta - 1)
        new_fields = self._calculate_neighbors(delta)
        for field in old_fields:
            new_fields.remove(field)
        self.available_fields = new_fields

    def _calculate_neighbors(self, delta):
        avaible_fields = []
        rowNumber = colNumber = FieldService.MAP_LENGTH/2
        for rowAdd in range(-delta+1, delta):
            newRow = rowNumber + rowAdd
            if 0 <= newRow <= len(self.fields)-1:
                for colAdd in range(-delta+1, delta):
                    newCol = colNumber + colAdd
                    if 0 <= newCol <= len(self.fields)-1:
                        if newCol == colNumber and newRow == rowNumber:
                            continue
                        avaible_fields.append(self.fields[newCol][newRow])
        return avaible_fields

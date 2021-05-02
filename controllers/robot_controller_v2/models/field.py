from enum import Enum
from time import sleep

from models.location import Location
from models.location_limit import LocationLimit


class FieldState(str, Enum):
    NONE = "NONE",
    BLOCKED = "BLOCKED",
    SCANNED = "SCANNED",
    SCANNING = "SCANNING",
    CAN_BE_SCANNED = "CAN_BE_SCANNED"


class Field:
    def __init__(self, index, loc_limit: LocationLimit):
        self.x, self.y = index
        self._state = FieldState.NONE
        self.loc_limit = loc_limit
        self.scanner = None

    def __str__(self):
        return "{}".format(self.loc_limit)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state: FieldState):
        if new_state is FieldState.CAN_BE_SCANNED:
            if self._state is not FieldState.NONE:
                return
        self._state = new_state


class FieldService:
    MAP_LENGTH = 20
    DELTA = 1

    def __init__(self, middle_loc: Location, offset: Location):
        self.fields: [Field] = [[0 for i in range(
            FieldService.MAP_LENGTH)] for j in range(FieldService.MAP_LENGTH)]
        middle_coords = [[0 for i in range(FieldService.MAP_LENGTH)] for j in range(
            FieldService.MAP_LENGTH)]
        firstSideX = middle_loc.x - (FieldService.MAP_LENGTH // 2 * offset.x)
        firstSideZ = middle_loc.z - (FieldService.MAP_LENGTH // 2 * offset.z)

        self._available_fields: [Field] = None
        self.delta = 0

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
                self.fields[i][j] = Field((i, j),
                                          loc_limit=LocationLimit(lower_limit, upper_limit))
        self.make_field_neighbors_available(FieldService.DELTA)

    def get_middle(self):
        return self.fields[FieldService.MAP_LENGTH // 2][FieldService.MAP_LENGTH // 2]

    def change_field_state(self, field: Field, new_state: FieldState):
        self.fields[field.x][field.y].state = new_state
        if not self.is_available_to_search():
            self.make_field_neighbors_available(FieldService.DELTA)

    @property
    def available_fields(self):
        if not self.is_available_to_search():
            self.make_field_neighbors_available(FieldService.DELTA)
        return self._available_fields

    def is_available_to_search(self) -> bool:
        _available_fields = list(
            filter(lambda f: f.state == FieldState.CAN_BE_SCANNED, self._available_fields))
        if not _available_fields:
            return False
        return True

    def make_field_neighbors_available(self, delta):
        self.delta += delta
        old_fields = self._calculate_neighbors(self.delta - 1)
        new_fields = self._calculate_neighbors(self.delta)
        for field in old_fields:
            new_fields.remove(field)
        self._available_fields = new_fields

    def _calculate_neighbors(self, delta):
        available_fields = []
        rowNumber = colNumber = FieldService.MAP_LENGTH // 2
        for rowAdd in range(-delta + 1, delta):
            newRow = rowNumber + rowAdd
            if 0 <= newRow <= len(self.fields) - 1:
                for colAdd in range(-delta + 1, delta):
                    newCol = colNumber + colAdd
                    if 0 <= newCol <= len(self.fields) - 1:
                        if newCol == colNumber and newRow == rowNumber:
                            continue
                        new_field = self.fields[newCol][newRow]
                        new_field.state = FieldState.CAN_BE_SCANNED
                        available_fields.append(new_field)

        print(available_fields)
        return available_fields

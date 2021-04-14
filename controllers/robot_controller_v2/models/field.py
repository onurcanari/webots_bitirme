import numpy as np
from enum import Enum

from models.location import Location
from models.location_limit import LocationLimit


class FieldState(Enum):
    NONE = 0,
    BLOCKED = 1,
    SCANNED = 2,
    SCANNING = 3


# TODO her birinin loc limit hesaplanıp diziye atanacak. sonra ortanca elemandan başaklyarak ve çevresinden. alanları
#  sırasıyla genişleyerek tara. her birinde robot içeride mi kontrol et. 25 x offset kadar yukarı çıkınca sınırdan
#  ilk eleman. sonra ona ekleye ekelye 50 tane sağa eklecek. sonra 50şer tane aşağı ekleyecek.


class Field:
    def __init__(self, loc_limit: LocationLimit):
        self.state = FieldState.NONE
        self.loc_limit = loc_limit
        self.scanner = None

    def __str__(self):
        return "{}".format(self.loc_limit)


class FieldService:
    MAP_LENGTH = 20

    def __init__(self, middle_loc: Location, offset: Location):
        self.fields = [[0 for i in range(FieldService.MAP_LENGTH)] for j in range(FieldService.MAP_LENGTH)]
        middle_coords = [[0 for i in range(FieldService.MAP_LENGTH)] for j in range(FieldService.MAP_LENGTH)]
        firstSideX = middle_loc.x - (FieldService.MAP_LENGTH // 2 * offset.x)
        firstSideZ = middle_loc.z - (FieldService.MAP_LENGTH // 2 * offset.z)

        for i in range(FieldService.MAP_LENGTH):
            for j in range(FieldService.MAP_LENGTH):
                middle_coords[i][j] = Location.from_coords(firstSideX + j * offset.x, None, firstSideZ + i * offset.z)
                Location.from_coords(middle_coords[i][j].x, None, middle_coords[i][j].z + offset.z / 2)
                lower_limit = Location.from_coords(x=middle_coords[i][j].x - offset.x / 2,
                                                   z=middle_coords[i][j].z + offset.z / 2)
                upper_limit = Location.from_coords(x=middle_coords[i][j].x + offset.x / 2,
                                                   z=middle_coords[i][j].z - offset.z / 2)
                self.fields[i][j] = LocationLimit(lower_limit, upper_limit)

    def get_middle(self):
        return self.fields[FieldService.MAP_LENGTH // 2][FieldService.MAP_LENGTH // 2]

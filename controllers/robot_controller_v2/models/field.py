import numpy as np
from enum import Enum

class FieldState(Enum):
    NONE = 0,
    BLOCKED = 1,
    SCANNED = 2,
    SCANNING = 3

#   TODO 
#   her birinin loc limit hesaplanıp diziye atanacak.
#   sonra ortanca elemandan başaklyarak ve çevresinden. alanları sırasıyla genişleyerek tara. her birinde robot içeride mi kontrol et.
#   25 x offset kadar yukarı çıkınca sınırdan ilk eleman. sonra ona ekleye ekelye 50 tane sağa eklecek. sonra 50şer tane aşağı ekleyecek.

class Field:
    fields = [[0 for i in range(50)] for j in range(50)]
    
    def __init__(self, loc_limit):
        self.state = FieldState.NONE
        self.loc_limit = loc_limit

    @staticmethod
    def get_middle():
        return Field.fields[25][25]
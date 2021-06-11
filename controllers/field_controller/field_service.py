from models.message import MessageType
from models.field_service_i import IFieldService
import logging
from random import uniform

TIME_STEP = 64

logger = logging.getLogger()


class FieldService(IFieldService):
    map_start = None

    def __init__(self):
        super().__init__()
        self.draw_fields = False
        self.fields_count = 0
        self.limit_z = None
        self.drawed_mine = False
        self.draw_mine()

    def run(self):
        logger.debug("Start robot")
        self.draw_mine()
        while self.step(TIME_STEP) != -1:
            self._listen_message()

    def _listen_message(self):
        self.get_message(self._process_message)

    def _process_message(self, message):
        if message.type == MessageType.NEW_AVAIBLE_FIELDS:
            self.draw_avaible_fields(message.content)

    def draw_avaible_fields(self, available_fields):
        if self.fields_count >= len(available_fields):
            return
        self.fields_count = len(available_fields)
        if available_fields:
            for field in available_fields:
                loc_limit = field.loc_limit
                self.drawLimits(loc_limit.upper_limit.x,
                                loc_limit.upper_limit.z)
                self.drawLimits(loc_limit.upper_limit.x-2,
                                loc_limit.upper_limit.z)
                self.drawLimits(loc_limit.lower_limit.x,
                                loc_limit.lower_limit.z)
                self.drawLimits(loc_limit.lower_limit.x+2,
                                loc_limit.lower_limit.z)

    def set_limit(self, value):
        if self.limit_z is None:
            self.limit_z = value
        else:
            if self.limit_z > value:
                self.limit_z = value

    def drawLimits(self, x, z):
        """ Oluşturulan alanların sınırlarını harita üzerine çizer """
        field = self.root_node.getField("children")
        field.importMFNodeFromString(-1,
                                     "Transform { children [ Shape { appearance PBRAppearance { } geometry Sphere { radius 0.1 subdivision 3 } } ] }")
        node = field.getMFNode(-1)
        transField = node.getField("translation")
        transField.setSFVec3f([x, 0, z])

    def draw_mine(self):
        """ Harita üzerine belirtilen alanlar içerisinde rastgele olarak mayınlar çizer  """
        if self.drawed_mine:
            return
        randomMineCount = 10
        for x in range(randomMineCount):
            field = self.root_node.getField("children")
            field.importMFNodeFromString(-1,
                                         "DEF mine%d Robot { children [ Shape { appearance PBRAppearance { baseColor 1 0 0 roughness 1 metalness 0 } geometry Cylinder { height 0.08 radius 0.05 } } ] }" % (
                                             x + 1))
            node = field.getMFNode(-1)
            transField = node.getField("translation")
            random_loc = [
                uniform(-7, 3), 0, uniform(-8, 1)]
            transField.setSFVec3f(random_loc)
        self.drawed_mine = True

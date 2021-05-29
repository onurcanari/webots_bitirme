from models.field import FieldService
from models.location import Location
from models.message import Message, MessageType

from models.ground_robot_i import IGroundRobot
from random import randrange
import logging
from random import randrange, uniform

TIME_STEP = 64

logger = logging.getLogger()


class GroundRobot(IGroundRobot):
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
        while self.step(TIME_STEP) != -1:
            self._listen_message()

    def _listen_message(self):
        self.get_message(self._process_message)

    def _process_message(self, message):

        if message.type == MessageType.NEW_AVAIBLE_FIELDS:
            self.draw_avaible_fields(message.content)
            # self.save_robot_location(
            #     message.robot_id, Location.from_coords(**vars(message.content)))

    def draw_avaible_fields(self, available_fields):
        if self.fields_count >= len(available_fields):
            return
        self.fields_count = len(available_fields)
        if available_fields:
            # self.draw_fields = True
            for field in available_fields:
                loc_limit = field.loc_limit
                # self.set_limit(loc_limit.lower_limit.z)
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

    # TODO Alanlar mine0 a göre oluşuyor mine0 ı en alttaki robotun konumu yapmamız gerekiyor
    def drawLimits(self, x, z):
        field = self.root_node.getField("children")
        field.importMFNodeFromString(-1,
                                     "Transform { children [ Shape { appearance PBRAppearance { } geometry Sphere { radius 0.1 subdivision 3 } } ] }")
        node = field.getMFNode(-1)
        transField = node.getField("translation")
        transField.setSFVec3f([x, 0, z])

    def draw_mine(self):
        if self.drawed_mine:
            return
        randomMineCount = 5
        for x in range(randomMineCount):
            field = self.root_node.getField("children")
            field.importMFNodeFromString(-1,
                                         "DEF mine%d Robot { children [ Shape { appearance PBRAppearance { baseColor 1 0 0 roughness 1 metalness 0 } geometry Cylinder { height 0.08 radius 0.05 } } ] }" % (
                                             x + 1))
            node = field.getMFNode(-1)
            transField = node.getField("translation")
            random_loc = [
                uniform(-3, 4), 0, uniform(-2, 4)]
            transField.setSFVec3f(random_loc)
        self.drawed_mine = True

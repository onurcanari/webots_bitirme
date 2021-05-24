from models.field import FieldService
from models.location import Location
from models.message import Message, MessageType

from models.ground_robot_i import IGroundRobot
import logging
from random import randrange, uniform

TIME_STEP = 64

logger = logging.getLogger()


class GroundRobot(IGroundRobot):
    map_start = None

    def __init__(self):
        super().__init__()
        self.draw_fields = False
        self.robot_locations = {}
        self.field_service: FieldService = None

    def run(self):
        logger.debug("Start robot")
        self.draw_mine()
        while self.step(TIME_STEP) != -1:
            self._listen_message()
            if len(self.robot_locations) == 4:
                self.select_area()

    def save_robot_location(self, robot_id, location):
        self.robot_locations[robot_id] = location

    def send_message(self, message_type, content):
        if content is None:
            return
        self._send_message(Message(self.robot_id, content,
                                   message_type))

    def _listen_message(self):
        self.get_message(self._process_message)

    def _process_message(self, message):
        if message.type == MessageType.NEW_ROBOT_LOCATION:
            self.save_robot_location(
                message.robot_id, Location.from_coords(**vars(message.content)))

    def select_area(self):
        comparing_location = Location.from_coords(
            0, 0, 0) if GroundRobot.map_start is None else GroundRobot.map_start

        robot_ids = sorted(self.robot_locations.items(),
                           key=lambda kv: comparing_location.compare(kv[1]))
        if GroundRobot.map_start is None:
            GroundRobot.map_start = robot_ids[0][1]
            logger.debug("MAP START : {}".format(GroundRobot.map_start))
            self.field_service = FieldService(
                middle_loc=GroundRobot.map_start, offset=Location.from_coords(x=2, z=2), log=logger)

        if self.field_service.available_fields and not self.draw_fields:
            self.draw_fields = True
            for x in range(len(self.field_service.available_fields)):
                field = self.root_node.getField("children")
                field.importMFNodeFromString(-1,
                                             "Transform { children [ Shape { appearance PBRAppearance { } geometry Sphere { radius 0.1 subdivision 3 } } ] }")
                node = field.getMFNode(-1)
                transField = node.getField("translation")
                loc_upper = self.field_service.available_fields[x].loc_limit.upper_limit
                transField.setSFVec3f([loc_upper.x, 0, loc_upper.z])

                field = self.root_node.getField("children")
                field.importMFNodeFromString(-1,
                                             "Transform { children [ Shape { appearance PBRAppearance { } geometry Sphere { radius 0.1 subdivision 3 } } ] }")
                node = field.getMFNode(-1)
                transField = node.getField("translation")
                loc_lower = self.field_service.available_fields[x].loc_limit.lower_limit

                transField.setSFVec3f([loc_lower.x, 0, loc_lower.z])

    def draw_mine(self):
        randomMineCount = 10
        for x in range(randomMineCount):
            field = self.root_node.getField("children")
            field.importMFNodeFromString(-1,
                                         "DEF mine%d Robot { children [ Shape { appearance PBRAppearance { baseColor 1 0 0 } geometry Cylinder { height 0.5 radius 0.05 } } ] }" % (
                                                     x + 1))
            node = field.getMFNode(-1)
            transField = node.getField("translation")
            random_loc = [uniform(-5, 6), 0, uniform(-5, 6)]
            transField.setSFVec3f(random_loc)

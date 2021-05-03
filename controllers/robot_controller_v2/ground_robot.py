from models.field import FieldService, Field, FieldState
from models.location import Location
from models.location_limit import LocationLimit
import util
from models.message import Message, MessageType
from models.state import RobotState
from models.state import State
from models.state import Status
from models.ground_robot_i import IGroundRobot
import logging

TIME_STEP = 64

logger = logging.getLogger('something')


class GroundRobot(IGroundRobot):
    map_start = None

    def __init__(self, robot_id: str):
        super().__init__(robot_id)
        self._robot_state = RobotState(State.IDLE)
        self._robot_state.complete()
        self.turn = False
        self.robot_locations = {}
        self.target_rotation = None
        self.target_location = None
        self.went_first_area = False
        self.target_field: Field = None
        self.field_service: FieldService = None
        self.first_test = False

        myFormatter = logging.Formatter(
            'RobotId: {} - %(message)s'.format(str(robot_id)))
        handler = logging.StreamHandler()
        handler.setFormatter(myFormatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logger.debug("Setup ground robot with id: {}".format(self.robot_id))

    def run(self):
        logger.debug("Start robot")
        while self.step(TIME_STEP) != -1:
            self.update_fields()
            self.send_message(MessageType.NEW_ROBOT_LOCATION,
                              self.robot_location)
            self._listen_message()
            if len(self.robot_locations) == 3:
                self.discover_and_run()

    def clear_target(self):
        self.target_rotation = None
        self.target_location = None
        self.went_first_area = False
        self.target_field: Field = None

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
        if message.type == MessageType.FIELD_UPDATE:
            self.field_service.change_field_state(message.content)
            pass
        elif message.type == MessageType.NEW_ROBOT_LOCATION:
            self.save_robot_location(
                message.robot_id, Location.from_coords(**vars(message.content)))

    def go_coverage(self):
        if self._robot_state.status is Status.COMPLETED or self.go_to(self.target_location):
            target = self.robot_location.calculate_target_location(
                self.target_field.loc_limit, self.turn)
            if target is not None:
                logger.debug(target)
                self.turn = not self.turn
                self.target_location = target
                self.go_to(target)
            else:
                self.target_field.state = FieldState.SCANNED
                logger.debug("FİELD STATE : {}".format(self.target_field))
                self.send_message(MessageType.FIELD_UPDATE, self.target_field)
                self.clear_target()
                self.first_test = True
                logger.debug("Go coverage finished")
        else:
            self.go_to(self.target_location)

    def turn_with_degree(self, degree, delta=1):
        self.change_state(State.CHANGE_ROTATION)
        if self._robot_state.state is not State.CHANGE_ROTATION:
            return
        if not self.target_rotation:
            self.target_rotation = degree
        else:
            if util.is_close(self.robot_rotation.angle, self.target_rotation, delta):
                self.target_rotation = None
                self._robot_state.complete()
                self.stop_engine()
            else:
                self._robot_state.continue_pls()
                if self.robot_location.x < self.target_location.x:
                    if self.robot_rotation.angle > self.target_rotation:
                        if (self.robot_rotation.angle - self.target_rotation) < 180:
                            self.move_right()
                        else:
                            self.move_left()
                    else:
                        self.move_left()
                else:
                    if self.robot_rotation.angle < self.target_rotation:
                        if (self.target_rotation - self.robot_rotation.angle) < 180:
                            self.move_left()
                        else:
                            self.move_right()
                    else:
                        self.move_right()

    def calculate_area_to_discover(self):
        available_fields = self.field_service.available_fields
        if self.target_field is not None:
            return

        for field in available_fields:
            if self.is_closest_to_field(field):
                self.target_field = field
                self.target_field.scanner = self.robot_id
                self.target_field.state = FieldState.SCANNING
                self.target_location = self.target_field.loc_limit.lower_limit

                self.send_message(MessageType.FIELD_UPDATE, self.target_field)
                break

    def is_closest_to_field(self, target: Field):
        distance_to_field = self.robot_location.distance_to_other_loc(
            target.loc_limit.lower_limit)
        for robot_id, loc in self.robot_locations.items():
            temp_dist = loc.distance_to_other_loc(target.loc_limit.lower_limit)
            if distance_to_field < temp_dist:
                # logger.debug("{} closer to {}.".format(str(robot_id), str(loc)))
                return False

        logger.info("This robot is closes to field: {}".format(target))
        return True

    def select_area(self):
        # logger.debug("Selecting area...")
        comparing_location = Location.from_coords(
            0, 0, 0) if GroundRobot.map_start is None else GroundRobot.map_start

        robot_ids = sorted(self.robot_locations.items(),
                           key=lambda kv: comparing_location.compare(kv[1]))
        if GroundRobot.map_start is None:
            GroundRobot.map_start = robot_ids[0][1]
            logger.debug("MAP START : {}".format(GroundRobot.map_start))
            self.field_service = FieldService(
                middle_loc=GroundRobot.map_start, offset=Location.from_coords(x=2, z=2), log=logger)

        if self.field_service.available_fields and self.robot_id == 0:
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

        self.calculate_area_to_discover()

    def discover_and_run(self):
        if self.first_test:
            self.stop_engine()
            return
        if self.target_field is None:
            self.select_area()
        elif not self.went_first_area:
            self.went_first_area = self.go_to(
                self.target_field.loc_limit.lower_limit)
            if self.went_first_area:
                logger.debug("ROBOT GO TO FİRST AREA FİNİSHED")
        else:
            self.go_coverage()

    def go_to(self, location):
        turning_degree = self.robot_location.calculate_degree_between(
            location) % 360
        self.turn_with_degree(turning_degree)

        self.change_state(State.GO_TO_LOCATION)
        if self._robot_state.state is State.GO_TO_LOCATION:
            self.move_forward()
            if self.robot_location.is_close(location):
                self._robot_state.complete()
                return True
        return False

    def change_state(self, new_state, force=False):
        if self._robot_state.status is Status.COMPLETED:
            if self._robot_state.state is not new_state or force:
                self._robot_state = RobotState(new_state)


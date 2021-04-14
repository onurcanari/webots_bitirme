from models.field import FieldService
from models.location import Location
from models.location_limit import LocationLimit
import util
from models.message import Message, MessageType
from models.state import RobotState
from models.state import State
from models.state import Status
from models.ground_robot_i import IGroundRobot

TIME_STEP = 64


class GroundRobot(IGroundRobot):
    map_start = None

    def __init__(self, robot_id: str):
        super().__init__(robot_id)
        self._robot_state = RobotState(State.IDLE)
        self._robot_state.complete()
        self.discovered_area = False
        self.turn = False
        self.robot_locations = {}
        self.target_rotation = None
        self.target_location = None
        self.first_area = False
        self.second_area = False
        self.loc_limit = None
        self.save_robot_location(self.robot_id, self.robot_location)
        self.field_service = None
        print("Setup ground robot with id:", self.robot_id)

    def save_robot_location(self, robot_id, location):
        self.robot_locations[robot_id] = location

    def send_location(self):
        location = self.robot_location

        if location is None:
            return

        self.send_message(Message(self.robot_id, location, MessageType.NEW_ROBOT_LOCATION))

    def _listen_message(self):
        self.get_message(self._process_message)

    def _process_message(self, message):
        if message.type == MessageType.FIELD_UPDATE:
            self.save_robot_location(message.robot_id, message.content)
        elif message.type == MessageType.NEW_ROBOT_LOCATION:
            pass

    def run(self):
        print("Start robot")
        while self.step(TIME_STEP) != -1:
            self.update_fields()
            self.send_location()
            self._listen_message()
            self.discover_and_run()

    def go_coverage(self):
        if self._robot_state.status is Status.COMPLETED or self.go_to(self.target_location):
            target = self.robot_location.calculate_target_location(
                self.loc_limit, self.turn)
            if target is not None:
                self.turn = not self.turn
                self.target_location = target
                self.go_to(self.target_location)
            else:
                if not self.second_area:
                    GroundRobot.map_start = GroundRobot.map_start.add(
                        Location.from_coords(0, 0, 6))
                    self.discovered_area = False
                    self.first_area = False
                    self.second_area = True
                else:
                    self.stop_engine()
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

    def calculate_area_to_discover(self, turn):
        print("Calculating area to discover...")
        offset = Location.from_coords(0, 0, -1.5 * turn)
        self.location_lower = GroundRobot.map_start.add(offset)
        temp_upper = self.location_lower.add(
            Location.from_coords(0, 0, -1.0))
        new_upper = temp_upper.add(Location.from_coords(1, 0, 0))
        self.loc_limit = LocationLimit(self.location_lower, new_upper)
        self.discovered_area = True
        print("Robot ID : ", self.robot_id, "Location Limit :", self.loc_limit)

    def select_area(self):
        print("Selecting area...")
        comparing_location = Location.from_coords(
            0, 0, 0) if GroundRobot.map_start is None else GroundRobot.map_start

        robot_ids = sorted(self.robot_locations.items(),
                           key=lambda kv: comparing_location.compare(kv[1]))
        if GroundRobot.map_start is None:
            GroundRobot.map_start = robot_ids[0][1]
            self.field_service = FieldService(middle_loc=GroundRobot.map_start, offset=Location.from_coords(x=2, z=2))
            if self.robot_id == 0:
                for x in range(20):
                    for y in range(20):
                        field = self.root_node.getField("children")
                        field.importMFNodeFromString(-1,
                                                     "Transform { children [ Shape { appearance PBRAppearance { } geometry Sphere { radius 0.1 subdivision 3 } } ] }")
                        node = field.getMFNode(-1)
                        transField = node.getField("translation")
                        loc = self.field_service.fields[x][y].loc_limit.lower_limit
                        transField.setSFVec3f([loc.x, 0, loc.z])
                        print("{} x {},".format(x, y), self.field_service.fields[x][y], )

        self.calculate_area_to_discover(
            list(map(lambda x: x[0], robot_ids)).index(self.robot_id))
        self.target_location = self.loc_limit.lower_limit
        self.robot_locations.clear()
        self.went_first_area = False
        GroundRobot.map_start = GroundRobot.map_start.add(
            Location.from_coords(0, 0, 6))

    def discover_and_run(self):
        if self.loc_limit is None:
            if len(self.robot_locations) == 4:
                self.select_area()
        elif not self.went_first_area:
            self.went_first_area = self.go_to(self.loc_limit.lower_limit)
        else:
            self.go_coverage()

    def go_to(self, location):
        turning_degree = self.robot_location.calculate_degree_between(location) % 360
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

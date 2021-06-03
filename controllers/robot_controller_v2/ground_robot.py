from models.obstacle import ObstacleSide, ObstacleState

from models.field import FieldService, Field, FieldState
from models.location import Location
import util
from models.message import Message, MessageType
from models.state import RobotState
from models.state import State
from models.state import Status
from models.state import RobotStatus
from models.ground_robot_i import IGroundRobot
import logging

from models.enums import SearchAlgorithms
from services import mine_search_service
from services.searchers import SearchService

TIME_STEP = 64

LEFT = 0
RIGHT = 1

PS_RIGHT_00 = 0
PS_RIGHT_45 = 1
PS_RIGHT_90 = 2
PS_RIGHT_REAR = 3
PS_LEFT_REAR = 4
PS_LEFT_90 = 5
PS_LEFT_45 = 6
PS_LEFT_00 = 7

OAM_OBST_THRESHOLD = 100

OAM_FORWARD_SPEED = 150
OAM_K_PS_90 = 0.2
OAM_K_PS_45 = 0.9
OAM_K_PS_00 = 1.2
OAM_K_MAX_DELTAS = 600

OFM_DELTA_SPEED = 150
log = logging.getLogger()


# import sys
# logging.disable(sys.maxsize)

class GroundRobot(IGroundRobot):
    map_start = None

    def __init__(self, robot_id: str):
        super().__init__(robot_id)
        self._robot_state = RobotState(State.IDLE)
        self._robot_state.complete()
        self.status = RobotStatus.IDLE
        self.robot_status = {
            0: RobotStatus.IDLE, 1: RobotStatus.IDLE, 2: RobotStatus.IDLE, 3: RobotStatus.IDLE}
        self.robot_locations = {}
        self.target_rotation = None
        self.target_location = None
        self.went_first_area = False
        self.target_field: Field = None
        self.field_service: FieldService = None

        myFormatter = logging.Formatter(
            'RobotId: {} - %(message)s'.format(str(robot_id)))
        self.mine_service = mine_search_service.MineService(robot_id, self)
        self.search_service = SearchService(SearchAlgorithms.SEARCH_WITH_STEP)
        myFormatter = logging.Formatter(
            'RobotId: {} - %(message)s'.format(str(robot_id)))
        handler = logging.StreamHandler()
        handler.setFormatter(myFormatter)
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)

        log.debug("Setup ground robot with id: {}".format(self.robot_id))

    def run(self):
        log.debug("Start robot")
        while self.step(TIME_STEP) != -1:
            self.update_fields()
            self._listen_message()
            if len(self.robot_locations) == 3:
                self.discover_and_run()
            self.mine_service.search_for_mine(self.robot_location,
                                              lambda mine_info: self.send_message(MessageType.MINE_FOUND, mine_info))

    def clear_target(self):
        self.target_rotation = None
        self.target_location = None
        self.went_first_area = False
        self.target_field = None

    def save_robot_location(self, robot_id, location):
        self.robot_locations[robot_id] = location

    def save_robot_status(self, robot_id, status):
        self.robot_status[robot_id] = status

    def send_message(self, message_type, content):
        if content is None:
            log.debug("Sending message is none. Returning...")
            return
        msg = Message(self.robot_id, content, message_type)
        self._send_message(msg)

    def _listen_message(self):
        self.get_message(self._process_message)

    def _process_message(self, message):
        if message.type == MessageType.FIELD_UPDATE:
            field = message.content
            self.field_service.change_field_state(field)
            self.save_robot_status(
                field.scanner, RobotStatus.SCANNING if field._state == FieldState.SCANNING else RobotStatus.IDLE)
            pass
        elif message.type == MessageType.NEW_ROBOT_LOCATION:
            self.save_robot_location(
                message.robot_id, Location.from_coords(**vars(message.content)))
        elif message.type == MessageType.MINE_FOUND:
            self.mine_service.process_found_mine(message)

    def go_coverage(self):
        if self._robot_state and self._robot_state.status is Status.COMPLETED or self.go_to(self.target_location):
            target_loc = self.search_service.calculate_target_location(
                self.robot_location)
            if target_loc is not None:
                self.target_location = target_loc
                self.go_to(target_loc)
            else:
                self.target_field.state = FieldState.SCANNED
                self.send_message(MessageType.FIELD_UPDATE, self.target_field)
                self.clear_target()
                log.debug("Go coverage finished.")
        else:
            # print("Target location {}".format(self.target_location))
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
            log.debug("Already exist target field. Returning.")
            return
        temp_target_field = None
        distance = None
        for field in available_fields:
            temp_distance = self.robot_location.distance_to_other_loc(
                field.loc_limit.lower_limit)
            if distance is None:
                temp_target_field = field
                distance = temp_distance
            else:
                if distance is not None and temp_distance < distance:
                    temp_target_field = field
                    distance = temp_distance

        for robot_id, status in self.robot_status.items():
            if robot_id < self.robot_id and status == RobotStatus.IDLE:
                return

        self.target_field = temp_target_field
        self.target_field.scanner = self.robot_id
        self.target_field.state = FieldState.SCANNING
        self.target_location = self.target_field.loc_limit.lower_limit
        # log.debug("New target : {} selected.".format(self.target_field))
        self.send_message(MessageType.FIELD_UPDATE, self.target_field)
        self.send_message(MessageType.NEW_AVAIBLE_FIELDS, available_fields)
        self.search_service.create_subdivisions(self.target_field.loc_limit)

    # def is_closest_to_field(self, target: Field):
    #     target_field = None
    #
    #     my_distance = target[0]
    #     for item in target[1]:
    #         target_field = item
    #
    #     for robot_id, loc in self.robot_locations.items():
    #         other_robot_dist = loc.distance_to_other_loc(
    #             target_field.loc_limit.lower_limit)
    #         if other_robot_dist < my_distance:
    #             return None
    #
    #     return target_field

    def select_area(self):
        log.info("Selecting area..")
        if GroundRobot.map_start is None:
            log.info("Initialize map start..")
            comparing_location = Location.from_coords(
                0, 0, 0) if GroundRobot.map_start is None else GroundRobot.map_start

            comparing_dict = dict(self.robot_locations)
            comparing_dict[self.robot_id] = self.robot_location
            robot_ids = sorted(comparing_dict.items(),
                               key=lambda kv: comparing_location.compare(kv[1]))
            GroundRobot.map_start = robot_ids[0][1]
            self.field_service = FieldService(middle_loc=GroundRobot.map_start, offset=Location.from_coords(x=2, z=2),
                                              robot_locations=self.robot_locations)
            log.debug("MAP START : {}".format(GroundRobot.map_start))

        self.calculate_area_to_discover()

    # def clear_rotation(self):
    #     self.target_rotation = None
    #     self._robot_state.complete()

    # def myround(self, x, base=5):
    #     return base * round(x / base)

    # def turn_degree(self, degree):
    #     if self.temp_angle is None:
    #         self.temp_angle = self.robot_rotation.angle
    #     if degree < 0:
    #         self.move_left()
    #     else:
    #         self.move_right()
    #
    #     angle = abs(self.robot_rotation.angle - self.temp_angle)
    #
    #     degree = abs(degree)
    #     if degree - 1 <= angle <= degree + 1:
    #         self.temp_angle = None
    #         return True
    #     return False

    def avoid_obstacle(self):

        if self.obstacle_module.detected_location is None:
            self.obstacle_module.detected_location = self.robot_location
            end_loc = self.robot_location.calculate_end_of_circle(self.robot_rotation.angle, 0.4)
            self.obstacle_module.end_location = end_loc
            print("Obstacle detected : \n detected loc : {} \n end_loc : {}".format(
                self.obstacle_module.detected_location, self.obstacle_module.end_location))
            self.search_service.target_point.blocked = True

        FL = BL = FR = BR = 0
        self.stop_engine()
        self.ObstacleAvoidanceModule()
        self.ObstacleFollowingModule(self.obstacle_module.oam_side)
        oam_ofm_speed = [0, 0]
        oam_ofm_speed[LEFT] = self.obstacle_module.oam_speed[LEFT] + \
                              self.obstacle_module.ofm_speed[LEFT]
        oam_ofm_speed[RIGHT] = self.obstacle_module.oam_speed[RIGHT] + \
                               self.obstacle_module.ofm_speed[RIGHT]

        if self.obstacle_module.oam_active or self.obstacle_module.ofm_active:
            FL = BL = oam_ofm_speed[LEFT]
            FR = BR = oam_ofm_speed[RIGHT]

        self.set_speeds(FL, FR, BL, BR)

        if self.obstacle_module.is_avoid(self.robot_location):
            print("SUCCESSFULY AVOİD OBSTACLE")
            self._robot_state = None
            self.target_rotation = None
            # self.search_service.set_next_target(self.robot_location)
            target_loc = self.search_service.calculate_target_location(
                self.robot_location)
            self.target_location = target_loc
            print(self.search_service.target_point)
            self.obstacle_module.reset()
            self.stop_engine()

    def discover_and_run(self):
        if self.obstacle_module.state is not ObstacleState.IDLE:
            self.avoid_obstacle()
            return
        if self.target_field is None:
            self.select_area()
        elif not self.went_first_area:
            self.went_first_area = self.go_to(
                self.target_field.loc_limit.lower_limit)
            if self.went_first_area:
                log.debug("Robot went to area. Now it can start to scan..")
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
        if self._robot_state is None:
            self._robot_state = RobotState(new_state)
            return
        if self._robot_state.status is Status.COMPLETED:
            if self._robot_state.state is not new_state or force:
                self._robot_state = RobotState(new_state)

    def ObstacleAvoidanceModule(self):
        Activation = [0, 0]

        if self.obstacle_module.oam_reset:
            self.obstacle_module.oam_active = False
            self.obstacle_module.oam_side = ObstacleSide.NO_SIDE

        self.obstacle_module.oam_reset = 0

        max_ds_value = 0
        for i in range(PS_RIGHT_00, PS_RIGHT_45):
            if max_ds_value < self.ps_value[i]:
                max_ds_value = self.ps_value[i]
            Activation[RIGHT] += self.ps_value[i]

        for i in range(PS_LEFT_45, PS_LEFT_00):
            if max_ds_value < self.ps_value[i]:
                max_ds_value = self.ps_value[i]
            Activation[LEFT] += self.ps_value[i]

        if max_ds_value > OAM_OBST_THRESHOLD:
            self.obstacle_module.oam_active = True

        if self.obstacle_module.oam_active and self.obstacle_module.oam_side is ObstacleSide.NO_SIDE:
            if Activation[RIGHT] > Activation[LEFT]:
                self.obstacle_module.oam_side = ObstacleSide.RIGHT
            else:
                self.obstacle_module.oam_side = ObstacleSide.LEFT

        self.obstacle_module.oam_speed[LEFT] = OAM_FORWARD_SPEED
        self.obstacle_module.oam_speed[RIGHT] = OAM_FORWARD_SPEED

        if self.obstacle_module.oam_active:
            DeltaS = 0
            if self.obstacle_module.oam_side is ObstacleSide.LEFT:
                DeltaS -= int((OAM_K_PS_90 * self.ps_value[PS_LEFT_90]))
                DeltaS -= int((OAM_K_PS_45 * self.ps_value[PS_LEFT_45]))
                DeltaS -= int((OAM_K_PS_00 * self.ps_value[PS_LEFT_00]))
            else:
                DeltaS += int((OAM_K_PS_90 * self.ps_value[PS_RIGHT_90]))
                DeltaS += int((OAM_K_PS_45 * self.ps_value[PS_RIGHT_45]))
                DeltaS += int((OAM_K_PS_00 * self.ps_value[PS_RIGHT_00]))

            if DeltaS > OAM_K_MAX_DELTAS:
                DeltaS = OAM_K_MAX_DELTAS
            if DeltaS < -OAM_K_MAX_DELTAS:
                DeltaS = -OAM_K_MAX_DELTAS

            self.obstacle_module.oam_speed[LEFT] -= DeltaS
            self.obstacle_module.oam_speed[RIGHT] += DeltaS

    def ObstacleFollowingModule(self, side):
        if side is not ObstacleSide.NO_SIDE:
            self.obstacle_module.ofm_active = True
            if side is ObstacleSide.LEFT:
                self.obstacle_module.ofm_speed[LEFT] = -OFM_DELTA_SPEED
                self.obstacle_module.ofm_speed[RIGHT] = OFM_DELTA_SPEED
            else:
                self.obstacle_module.ofm_speed[LEFT] = OFM_DELTA_SPEED
                self.obstacle_module.ofm_speed[RIGHT] = -OFM_DELTA_SPEED

        else:
            self.obstacle_module.ofm_active = False
            self.obstacle_module.ofm_speed[LEFT] = 0
            self.obstacle_module.ofm_speed[RIGHT] = 0

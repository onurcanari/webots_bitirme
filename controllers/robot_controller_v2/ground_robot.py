from models.field import FieldService, Field, FieldState
from models.location import Location
import util
from models.message import Message, MessageType
from models.state import RobotState
from models.state import State
from models.state import Status
from models.state import RobotStatus
from models.state import ObstacleState
from models.ground_robot_i import IGroundRobot
import logging

import mine_search_service

TIME_STEP = 64

log = logging.getLogger()


class GroundRobot(IGroundRobot):
    map_start = None

    def __init__(self, robot_id: str):
        super().__init__(robot_id)
        self._robot_state = RobotState(State.IDLE)
        self._robot_state.complete()
        self.status = RobotStatus.IDLE
        self.robot_status = {
            0: RobotStatus.IDLE, 1: RobotStatus.IDLE, 2: RobotStatus.IDLE, 3: RobotStatus.IDLE}
        self.turn = False
        self.robot_locations = {}
        self.target_rotation = None
        self.target_location = None
        self.went_first_area = False
        self.target_field: Field = None
        self.field_service: FieldService = None
        # silebiliriz
        self.force_move = False
        self.select_degree = False
        self.temp_angle = None

        self.obstacle_target = None
        myFormatter = logging.Formatter(
            'RobotId: {} - %(message)s'.format(str(robot_id)))
        self.mine_service = mine_search_service.MineService(robot_id, self)

        myFormatter = logging.Formatter('RobotId: {} - %(message)s'.format(str(robot_id)))
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
            log.debug("Robot:{}, found a new mine: {}".format(self.robot_id, message.content.mine_name))
            self.mine_service.process_founded_mine(message)
        else:
            log.debug("Message received with unknown type: {}".format(message))

    def go_coverage(self):
        if self._robot_state.status is Status.COMPLETED or self.go_to(self.target_location):
            target = self.robot_location.calculate_target_location(
                self.target_field.loc_limit, self.turn)
            if target is not None:
                self.turn = not self.turn
                self.target_location = target
                self.go_to(target)
            else:
                self.target_field.state = FieldState.SCANNED
                self.send_message(MessageType.FIELD_UPDATE, self.target_field)
                self.clear_target()
                log.debug("Go coverage finished.")
        else:
            self.go_to(self.target_location)

    def turn_with_degree(self, degree, delta=1):
        self.change_state(State.CHANGE_ROTATION)
        if self._robot_state.state is not State.CHANGE_ROTATION:
            return
        if not self.target_rotation:
            print("return with deggree {}".format(degree))
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
        # log.debug("Calculating area to discover...")
        available_fields = self.field_service.available_fields
        print("Avaible fields length : {}".format(len(available_fields)))

        # log.debug("{} available field exist. Selecting one.".format(
        #     len(available_fields)))

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
                log.debug("I am waiting...")
                return

        self.target_field = temp_target_field
        self.target_field.scanner = self.robot_id
        self.target_field.state = FieldState.SCANNING
        self.target_location = self.target_field.loc_limit.lower_limit
        log.debug("New target : {} selected.".format(self.target_field))
        self.send_message(MessageType.FIELD_UPDATE, self.target_field)
        self.send_message(MessageType.NEW_AVAIBLE_FIELDS, available_fields)

    def is_closest_to_field(self, target: Field):
        target_field = None

        my_distance = target[0]
        for item in target[1]:
            target_field = item

        for robot_id, loc in self.robot_locations.items():
            other_robot_dist = loc.distance_to_other_loc(
                target_field.loc_limit.lower_limit)
            if other_robot_dist < my_distance:
                return None

        return target_field

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
            self.field_service = FieldService(
                middle_loc=GroundRobot.map_start, offset=Location.from_coords(x=2, z=2), log=log)
            log.debug("MAP START : {}".format(GroundRobot.map_start))

        self.calculate_area_to_discover()

    def next_obstacle_state(self):
        index = self.obstacle_state.value
        print(index)
        if index is 4:
            index = 0
        else:
            index = index + 1
        self.obstacle_state = ObstacleState(index)

    def clear_rotation(self):
        self.target_rotation = None
        self._robot_state.complete()

    
    def myround(self,x, base=5):
        return base * round(x/base)

    #TODO Robot ters durumdan engel ile karşılaştığında derece yanlış oluyor
    def turn_degree(self, degree):
        if self.temp_angle is None:
            self.temp_angle = self.robot_rotation.angle
        if degree < 0:
            self.move_left()
        else:
            self.move_right()

        angle = abs(self.robot_rotation.angle - self.temp_angle)

        degree = abs(degree)
        if angle >= degree-1 and angle <= degree+1:
            self.temp_angle = None
            return True
        return False

    def avoid_obstacle(self):
        if not self.select_degree:
            self.clear_rotation()
            self.select_degree = True
        # SAĞ --> SOL --> SOL
        if self.obstacle_state is ObstacleState.DETECTED:
            
            if self.turn_degree(90):
                self.select_degree = False
                self.next_obstacle_state()

            pass
        elif self.obstacle_state is ObstacleState.AVOID_1 or self.obstacle_state is ObstacleState.AVOID_2:
            sensor = self.distance_sensors[2]
            distance = sensor.getValue()
            if distance >= 1000 and self.force_move:
                
                if self.turn_degree(-90):
                    self.select_degree = False
                    self.force_move = False
                    self.next_obstacle_state()
            else:
                if distance < 1000:
                    self.force_move = True
                self.move_forward()
        else:
            if util.is_close(self.target_location.x, self.robot_location.x, 0.2):
                if self.go_to(self.target_location):
                    self.select_degree = False
                    self.force_move = False
                    self.next_obstacle_state()
                print("AVOİD OBSTACLE  ---------------")
            else:
                self.move_forward()
                    

    def discover_and_run(self):
        if self.obstacle_state is not ObstacleState.IDLE:
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
        if self._robot_state.status is Status.COMPLETED:
            if self._robot_state.state is not new_state or force:
                self._robot_state = RobotState(new_state)


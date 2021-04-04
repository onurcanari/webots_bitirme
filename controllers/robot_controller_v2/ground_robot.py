from models.location import Location
from models.location_limit import LocationLimit
from models.rotation import Rotation
import util
from models.state import RobotState
from models.state import State
from models.state import Status
from models.ground_robot_i import IGroundRobot

from random import random
import struct
import json

TIME_STEP = 64


class GroundRobot(IGroundRobot):
    map_start = Location.from_coords(0, 0, 2)

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
        self.saveRobotLocation(self.robot_id, self.robot_location)
        print("Setup ground robot with id:", self.robot_id)

    def saveRobotLocation(self, robot_id, location):
        if robot_id not in self.robot_locations:
            self.robot_locations[robot_id] = location

    def sendLocation(self):
        location = self.robot_location
        if location == None:
            return

        message = {
            "robot_id": self.robot_id,
            **vars(location)
        }

        json_message = json.dumps(message)
        my_str_as_bytes = str.encode(json_message)
        self.emitter.send(my_str_as_bytes)

    def listenLocationData(self):
        if self.receiver.getQueueLength() > 0:
            message = self.receiver.getData()
            my_decoded_str = message.decode()
            data = json.loads(my_decoded_str)
            self.saveRobotLocation(data['robot_id'], Location.from_coords(
                data['x'], data['y'], data['z']))
            self.receiver.nextPacket()

    def run(self):
        print("Start robot")
        while self.step(TIME_STEP) != -1:
            self.update_fields()
            self.sendLocation()
            self.listenLocationData()
            self.discover_and_run()

    def go_coverage(self):
        if self._robot_state.status is Status.COMPLETED:
            target = self.robot_location.calculate_target_location(
                self.loc_limit, self.turn)
            if target is not None:
                self.turn = not self.turn
                self.target_location = target
                self.go_to(self.target_location)
            else:
                self.stop_engine()
            # print("-------------------\nRobot ID : {} \n Target Location : {}\n----------------".format(
            #     self.robot_id, self.target_location))
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
                # print("Finish turning")
                self._robot_state.complete()
                self.stop_engine()
            else:
                # print("Robot is turning...")
                self._robot_state.continue_pls()
                if(self.robot_rotation.angle > self.target_rotation):
                    if(self.robot_rotation.angle < 270):
                        self.move_right()
                    else:
                        self.move_left()
                else:
                    self.move_left()
        # print("------------------------------------")
        # print("Robot ID : {}".format(self.robot_id))
        # print("Robot angle : {}".format(self.robot_rotation.angle))
        # print("Robot target degree : {}".format(self.target_rotation))
        # print("------------------------------------")

    def calculate_area_to_discover(self, turn):
        print("Calculating area to discover...")
        offset = Location.from_coords(0, 0, 1.0 * turn)
        self.location_lower = GroundRobot.map_start.subtract(offset)
        temp_upper = self.location_lower.subtract(
            Location.from_coords(0, 0, 1.0))
        self.loc_limit = LocationLimit(temp_upper, self.location_lower)
        self.discovered_area = True
        print("Robot ID : ", self.robot_id, "Location Limit :", self.loc_limit)

    def select_area(self):
        print("Selecting area...")
        robot_ids = sorted(self.robot_locations.items(),
                           key=lambda kv: GroundRobot.map_start.compare(kv[1]))
        self.calculate_area_to_discover(
            list(map(lambda x: x[0], robot_ids)).index(self.robot_id))
        self.target_location = self.loc_limit.lower_limit

    def discover_and_run(self):
        if not self.discovered_area:
            if len(self.robot_locations) == 4:
                self.select_area()
        elif not self.first_area:
            self.go_to(self.loc_limit.lower_limit)
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
                # self.stop_engine()
                self.first_area = True
                self._robot_state.complete()
                print("FİNİSHED PROCCESS")

    def change_state(self, new_state, force=False):
        if self._robot_state.status is Status.COMPLETED:
            if self._robot_state.state is not new_state or force:
                self._robot_state = RobotState(new_state)

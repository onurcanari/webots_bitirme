from controller import Supervisor
from models.location import Location
from models.location_limit import LocationLimit
from models.rotation import Rotation
import util
from models.state import RobotState
from models.state import State
from models.state import Status

from random import random
import struct
import json

TIME_STEP = 64
ROBOT_SPEED = 5.0


class GroundRobot(Supervisor):
    map_start = Location.from_coords(0, 0, 2)

    def __init__(self, robot_id: str):
        super().__init__()
        self._robot_state = RobotState(State.IDLE)
        self._robot_state.complete()
        self.robot_id = int(robot_id)
        self.distance_sensors = []
        self.wheels = []
        self.device_direction = True
        self.direction_counter = 0
        self.avoid_obstacle_counter = 0
        self.discovered_area = False
        self.turn = True
        self.robot_locations = {}
        self.target_rotation = None
        self.target_location = None
        self.first_area = False
        print("Setup ground robot with id:", self.robot_id)
        self.setup()

    def setup(self):
        self.root_node = self.getFromDef("robot"+str(self.robot_id))
        self.translation_field = self.root_node.getField("translation")
        self.rotation_field = self.root_node.getField("rotation")
        print("Getting distance sensors and enable them...")
        ds_names = ["ds_right", "ds_left"]

        for name in ds_names:
            distance_sensor = self.getDistanceSensor(name)
            distance_sensor.enable(TIME_STEP)
            self.distance_sensors.append(distance_sensor)

        print("Get and reposition motors..")
        wheels_names = ["wheel1", "wheel2", "wheel3", "wheel4"]

        for wheels_name in wheels_names:
            wheel = self.getMotor(wheels_name)
            wheel.setPosition(float('+inf'))
            wheel.setVelocity(0.0)
            self.wheels.append(wheel)

        print("Get and Set Emitter")
        self.emitter = self.getEmitter("emitter")
        self.emitter.setChannel(-1)
        print("Get and set Receiver")
        self.receiver = self.getReceiver("receiver")
        self.receiver.setChannel(-1)
        self.receiver.enable(TIME_STEP)
        self.updateFields()
        self.saveRobotLocation(self.robot_id, self.robot_location)
        print("Setup Passed")

    def updateFields(self):
        self._robot_location = Location(self.translation_field.getSFVec3f())
        self._robot_rotation = Rotation(self.rotation_field.getSFRotation())

    @property
    def robot_location(self):
        return self._robot_location

    @property
    def robot_rotation(self):
        return self._robot_rotation

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
            self.updateFields()
            self.sendLocation()
            self.listenLocationData()
            self.discover_and_run()

    def go_coverage(self):
        if self.turn:
            self.state = State
            self.turn_with_degree(90)
        else:
            self.move_forward()

    def turn_with_degree(self, degree, delta=1):
        self.change_state(State.CHANGE_ROTATION)
        if self._robot_state.state is not State.CHANGE_ROTATION:
            return
        if not self.target_rotation:
            self.target_rotation = degree
        else:
            if util.is_close(self.robot_rotation.angle, self.target_rotation, delta):
                self.turn = False
                self.target_rotation = None
                print("Finish turning")
                self._robot_state.complete()
                self.stop_engine()
            else:
                print("Robot is turning...")
                self._robot_state.continue_pls()
                if(self.robot_rotation.angle > self.target_rotation):
                    if(self.robot_rotation.angle < 270):
                        self.move_right()
                    else:
                        self.move_left()
                else:
                    self.move_left()
        print("------------------------------------")
        print("Robot ID : {}".format(self.robot_id))
        print("Robot angle : {}".format(self.robot_rotation.angle))
        print("Robot target degree : {}".format(self.target_rotation))
        print("------------------------------------")

    def get_message(self):
        if self.loc_limit.lower_limit.z < self.robot_location.z < self.loc_limit.upper_limit.z:
            return 1
        else:
            return 0

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

    def discover_and_run(self):
        if not self.discovered_area:
            if len(self.robot_locations) == 4:
                self.select_area()
        elif not self.first_area:
            self.go_to(self.loc_limit.lower_limit)
        else:
            print("STOP ENGİNE")
            self.stop_engine()

    def _set_motor_speeds(self, FL=None, FR=None, BL=None, BR=None):
        self.wheels[0].setVelocity(ROBOT_SPEED * FL)
        self.wheels[1].setVelocity(ROBOT_SPEED * FR)
        self.wheels[2].setVelocity(ROBOT_SPEED * BL)
        self.wheels[3].setVelocity(ROBOT_SPEED * BR)

    def move_forward(self):
        self._set_motor_speeds(1.0, 1.0, 1.0, 1.0)

    def stop_engine(self):
        self._set_motor_speeds(0.0, 0.0, 0.0, 0.0)

    def move_right(self):
        self._set_motor_speeds(0.2, -0.2, 0.2, -0.2)

    def move_left(self):
        self._set_motor_speeds(-0.2, 0.2, -0.2, 0.2)

    def go_to(self, location):
        turning_degree = self.robot_location.calculate_degree_between(
            location) % 360
        self.turn_with_degree(turning_degree)

        self.change_state(State.GO_TO_LOCATION)
        if self._robot_state.state is State.GO_TO_LOCATION:
            self.move_forward()

        if self.robot_location.is_close(location):
            self.stop_engine()
            self._robot_state.complete()
            print("FİNİSHED PROCCESS")
            self.first_area = True

    def change_state(self, new_state, force=False):
        if self._robot_state.status is Status.COMPLETED:
            if self._robot_state.state is not new_state or force:
                self._robot_state = RobotState(new_state)

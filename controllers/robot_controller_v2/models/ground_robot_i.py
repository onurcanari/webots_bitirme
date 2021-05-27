import logging
import sys

from controller import Supervisor
from models.location import Location
from models.rotation import Rotation
from models.message import Message, MessageType
from models.state import ObstacleState

import json
from types import SimpleNamespace

ROBOT_SPEED = 5.0
TIME_STEP = 64


class IGroundRobot(Supervisor):
    def __init__(self, robot_id):
        super().__init__()
        self.robot_id = int(robot_id)
        self.distance_sensors = []
        self.wheels = []
        self.location_last_updated_time_in_sec = -sys.maxsize
        self.setup()

    def setup(self):
        self.root_node = self.getFromDef("robot" + str(self.robot_id))
        self.translation_field = self.root_node.getField("translation")
        self.rotation_field = self.root_node.getField("rotation")
        print("Getting distance sensors and enable them...")
        ds_names = ["ds_right", "ds_left", "ds_back_left"]
        self.obstacle_state = ObstacleState.IDLE
        for name in ds_names:
            distance_sensor = self.getDevice(name)
            distance_sensor.enable(TIME_STEP)
            self.distance_sensors.append(distance_sensor)

        print("Get and reposition motors..")
        wheels_names = ["wheel1", "wheel2", "wheel3", "wheel4"]

        for wheels_name in wheels_names:
            wheel = self.getDevice(wheels_name)
            wheel.setPosition(float('+inf'))
            wheel.setVelocity(0.0)
            self.wheels.append(wheel)

        print("Get and Set Emitter")
        self.emitter = self.getDevice("emitter")
        self.emitter.setChannel(-1)
        print("Get and set Receiver")
        self.receiver = self.getDevice("receiver")
        self.receiver.setChannel(-1)
        self.receiver.enable(TIME_STEP)
        self.update_fields()
        print("Setup Completed")

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

    def update_fields(self):
        self._robot_location = Location(self.translation_field.getSFVec3f())
        self._robot_rotation = Rotation(self.rotation_field.getSFRotation())
        if self.getTime() - self.location_last_updated_time_in_sec > 1:
            self.send_message(MessageType.NEW_ROBOT_LOCATION, self.robot_location)
            self.location_last_updated_time_in_sec = self.getTime()
        self.control_obstacle()

    def control_obstacle(self):
        for i in range(2):
            sensor = self.distance_sensors[i]
            distance = sensor.getValue()
            if distance < 900:
                self.obstacle_state = ObstacleState.DETECTED

    @property
    def robot_location(self):
        return self._robot_location

    @property
    def robot_rotation(self):
        return self._robot_rotation

    def _send_message(self, message):
        try:
            json_data = json.dumps(message, default=lambda o: o.__dict__, indent=4)
            my_str_as_bytes = str.encode(json_data)
            # if message.type == MessageType.FIELD_UPDATE:
            #     logging.debug("Inside of send message: ".format(my_str_as_bytes))
            self.emitter.send(my_str_as_bytes)
        except Exception as e:
            logging.debug("Exception occurred.", e)

    def get_message(self, callback):
        if self.receiver.getQueueLength() > 0:
            message = self.receiver.getData()
            my_decoded_str = message.decode()
            response = json.loads(
                my_decoded_str, object_hook=lambda d: SimpleNamespace(**d))
            callback(response)
            self.receiver.nextPacket()

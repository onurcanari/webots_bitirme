from controller import Supervisor
from models.location import Location
from random import random
import struct
import json
TIME_STEP = 64


class GroundRobot(Supervisor):
    robot_locations = {}

    def __init__(self, robot_id: str):
        super().__init__()
        self.robot_id = int(robot_id)
        self.distance_sensors = []
        self.wheels = []
        print("Setup ground robot with id:", self.robot_id)
        self.setup()

    def setup(self):
        self.root_node = self.getFromDef("robot"+str(self.robot_id))
        self.translation_field = self.root_node.getField("translation")

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
        print("Setup Passed")

    def updateLocation(self):
        self._robot_location = Location(self.translation_field.getSFVec3f())

    @property
    def robot_location(self):
        return self._robot_location

    def saveRobotLocation(self):
        pass

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
            print(data)
            self.receiver.nextPacket()

    def run(self):
        print("Start robot")
        while self.step(TIME_STEP) != -1:
            self.updateLocation()
            self.sendLocation()
            self.listenLocationData()

    def GoCoverage(self):
        left_speed = 5.0
        right_speed = 5.0

        if self.avoid_obstacle_counter > 0:
            self.avoid_obstacle_counter -= 1
            if (device_direction)
            left_speed = -1.0
            right_speed = 1.0
            else
            left_speed = 1.0
            right_speed = -1.0
        else:
            if direction_counter > 0:
                direction_counter -= 1
            else:
                if turn:
                    # TODO burayı derece olarak döndür. random sayı olmasın
                     self.avoid_obstacle_counter = 57
                    turn = False
                else
                   for i in range(2):
                        if GetMessage():
                            self.avoid_obstacle_counter = 57
                            direction_counter = 10
                            turn = True

                    if self.avoid_obstacle_counter > 0:
                        device_direction = not device_direction

    def GetMessage(self):
        if getLowerZ() < self.robot_location.z < getUpperZ():
            return 1
        else:
            return 0
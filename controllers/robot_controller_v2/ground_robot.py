from controller import Supervisor
from models.location import Location
from models.location_limit import LocationLimit
from models.rotation import Rotation

from random import random
import struct
import json

TIME_STEP = 64
ROBOT_SPEED = 20

class GroundRobot(Supervisor):
    map_start = Location.from_coords(2, 0, 2)
    def __init__(self, robot_id: str):
        super().__init__()
        self.robot_id = int(robot_id)
        self.distance_sensors = []
        self.wheels = []
        self.device_direction = True
        self.direction_counter = 0
        self.avoid_obstacle_counter = 0
        self.discovered_area = False
        self.turn = False
        self.robot_locations = {}
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
        self.saveRobotLocation(self.robot_id,self.robot_location)
        print("Setup Passed")

    def updateFields(self):
        self._robot_location = Location(self.translation_field.getSFVec3f())
        self._robot_rotation = Rotation(self.rotation_field.getSFRotation())
        print(self._robot_rotation)

    @property
    def robot_location(self):
        return self._robot_location

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
            #print(data)
            self.saveRobotLocation(data['robot_id'],Location.from_coords(data['x'],data['y'],data['z']))
            self.receiver.nextPacket()

    def run(self):
        print("Start robot")
        while self.step(TIME_STEP) != -1:
            self.updateFields()
            self.sendLocation()
            self.listenLocationData()
            self.dicoverAndRun()

    def goCoverage(self):
        left_speed = 5.0
        right_speed = 5.0

        if self.avoid_obstacle_counter > 0:
            self.avoid_obstacle_counter -= 1
            if self.device_direction:
                left_speed = -1.0
                right_speed = 1.0
            else:
                left_speed = 1.0
                right_speed = -1.0
        else:
            if self.direction_counter > 0:
                self.direction_counter -= 1
            else:
                if self.turn:
                    # TODO burayı derece olarak döndür. random sayı olmasın
                    self.avoid_obstacle_counter = 57
                    self.turn = False
                else:
                    for i in range(2):
                        if self.getMessage():
                            self.avoid_obstacle_counter = 57
                            self.direction_counter = 10
                            self.turn = True
                    if self.avoid_obstacle_counter > 0:
                        self.device_direction = not self.device_direction
    
    def turnWithDegree(self):
        pass

    def getMessage(self):
        if self.loc_limit.lower_limit.z < self.robot_location.z < self.loc_limit.upper_limit.z:
            return 1
        else:
            return 0

    def calculateAreaToDiscover(self, turn):
        print("Calculating area to discover...")
        offset = Location.from_coords(0, 0, 1.0 * turn)
        self.location_lower = GroundRobot.map_start.subtract(offset)
        temp_upper = self.location_lower.subtract(Location.from_coords(0, 0, 1.0))
        self.loc_limit = LocationLimit(temp_upper, self.location_lower)
        self.discovered_area = True
        print("Robot ID : ",self.robot_id,"Location Limit :",self.loc_limit)

    def selectArea(self):
        print("Selecting area...")
        robot_ids = sorted(self.robot_locations.items(),
                           key=lambda kv: GroundRobot.map_start.compare(kv[1]))
        self.calculateAreaToDiscover(list(map(lambda x: x[0], robot_ids)).index(self.robot_id))

    def dicoverAndRun(self):
        if self.discovered_area:
            self.goCoverage()
        else:
            if len(self.robot_locations) == 4:
                self.selectArea()

    def _set_motor_speeds(self, FL = None, FR = None, BL = None, BR=None):
        if FL:
            self.wheels[0].setVelocity(ROBOT_SPEED * FL)
        if FR:
            self.wheels[1].setVelocity(ROBOT_SPEED * FR)
        if BL:
            self.wheels[2].setVelocity(ROBOT_SPEED * BL)
        if BR:
            self.wheels[3].setVelocity(ROBOT_SPEED * BR)
    
    def move_forward(self, speed):
        self._set_motor_speeds(1, 1, 1, 1)
    
    def go_to(self, location):
        pass
        
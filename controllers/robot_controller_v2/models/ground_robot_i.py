import logging
import sys

from controller import Supervisor
from models.location import Location
from models.rotation import Rotation
from models.message import Message, MessageType
from models.obstacle import Obstacle, ObstacleState

import numpy as np
import json
from types import SimpleNamespace

NB_DIST_SENS = 8

ROBOT_SPEED = 5.0
TIME_STEP = 64

log = logging.getLogger()

class IGroundRobot(Supervisor):
    """Bu sınıf robotun en temel hareketlerini tanımlar. Örneğin ileri git, mesaj gönder vb..."""
    def __init__(self, robot_id):
        super().__init__()
        self.robot_id = int(robot_id)
        self.distance_sensors = []
        self.wheels = []
        self.location_last_updated_time_in_sec = -sys.maxsize
        self.setup()

    def setup(self):
        """Robotun ilk değerlerini ve sensörlerini kurar."""
        self.root_node = self.getFromDef("robot" + str(self.robot_id))
        self.translation_field = self.root_node.getField("translation")
        self.rotation_field = self.root_node.getField("rotation")
        log.debug("Getting distance sensors and enable them...")
        ds_names = ["PS_RIGHT_00", "PS_RIGHT_45", "PS_RIGHT_90",
                    "PS_RIGHT_REAR", "PS_LEFT_REAR", "PS_LEFT_90", "PS_LEFT_45", "PS_LEFT_00"]
        self.ps_value = [0, 0, 0, 0, 0, 0, 0, 0]
        self.ps_offset = [300, 300, 300, 300, 300, 300, 300, 300]
        self.obstacle_module = Obstacle()
        for name in ds_names:
            distance_sensor = self.getDevice(name)
            if distance_sensor:
                distance_sensor.enable(TIME_STEP)
                self.distance_sensors.append(distance_sensor)

        log.debug("Get and reposition motors..")
        wheels_names = ["wheel1", "wheel2", "wheel3", "wheel4"]

        for wheels_name in wheels_names:
            wheel = self.getDevice(wheels_name)
            wheel.setPosition(float('+inf'))
            wheel.setVelocity(0.0)
            self.wheels.append(wheel)

        log.debug("Get and Set Emitter")
        self.emitter = self.getDevice("emitter")
        self.emitter.setChannel(-1)
        log.debug("Get and set Receiver")
        self.receiver = self.getDevice("receiver")
        self.receiver.setChannel(-1)
        self.receiver.enable(TIME_STEP)
        self.update_fields()
        log.debug("Setup Completed")

    def set_motor_speeds(self, FL=None, FR=None, BL=None, BR=None, multiplier=1):
        self.wheels[0].setVelocity(ROBOT_SPEED * FL)
        self.wheels[1].setVelocity(ROBOT_SPEED * FR)
        self.wheels[2].setVelocity(ROBOT_SPEED * BL)
        self.wheels[3].setVelocity(ROBOT_SPEED * BR)

    def set_speeds(self, FL=None, FR=None, BL=None, BR=None):
        # print("FL : {}, FR : {}, BL : {}, BR : {}".format(FL, FR, BL, BR))
        if FL == FR == BL == BR == 0:
            # Normal mode 1
            # Random mode 100
            FL = FR = BL = BR = 100
        self.set_motor_speeds(FL, FR, BL, BR, 0.00628)

    def move_forward(self):
        self.set_motor_speeds(1.0, 1.0, 1.0, 1.0)

    def stop_engine(self):
        self.set_motor_speeds(0.0, 0.0, 0.0, 0.0)

    def move_right(self):
        self.set_motor_speeds(0.2, -0.2, 0.2, -0.2)

    def move_left(self):
        self.set_motor_speeds(-0.2, 0.2, -0.2, 0.2)


    def update_fields(self):
        """Robotun konumunu, lokasyonunu günceller. Her 1sn'de bir diğer robotlara konumunu gönderir."""
        self._robot_location = Location(self.translation_field.getSFVec3f())
        self._robot_rotation = Rotation(self.rotation_field.getSFRotation())
        if self.getTime() - self.location_last_updated_time_in_sec > 1:
            self.send_message(MessageType.NEW_ROBOT_LOCATION,
                              self.robot_location)
            self.location_last_updated_time_in_sec = self.getTime()
        self.control_obstacle()

    def control_obstacle(self):
        """Sensörlerden gelen verileri kontrol eder. Eğer bir engelle karşılaşırsa durumunu günceller."""
        for i in range(NB_DIST_SENS):
            sensor = self.distance_sensors[i]
            distance = sensor.getValue()
            if np.isnan(distance):
                return
            distance = int(distance)
            if distance > 700:
                self.ps_value[i] = 0
            else:
                self.ps_value[i] = distance
            if i in [0, 7] and self.ps_value[i] > 0:
                self.obstacle_module.state = ObstacleState.DETECTED

    def get_sensors(self):
        sensors = [False, False, False, False, False, False]
        if self.robot_id == 3:
            for i in range(6):
                sensor = self.distance_sensors[i]
                distance = sensor.getValue()
                if distance < 1000:
                    sensors[i] = True
        return sensors

    @property
    def robot_location(self):
        return self._robot_location

    @property
    def robot_rotation(self):
        return self._robot_rotation

    def _send_message(self, message):
        """Diğer robotlara mesaj göndermek için oluşturulmuş utility metodu."""
        try:
            json_data = json.dumps(
                message, default=lambda o: o.__dict__, indent=4)
            my_str_as_bytes = str.encode(json_data)
            self.emitter.send(my_str_as_bytes)
        except Exception as e:
            logging.debug("Exception occurred.", e)

    def get_message(self, callback):
        """Diğer robotlardan gelen mesajı işlemek için kullanılır. Gelen paket üzerinde callback çalıştırılır."""
        if self.receiver.getQueueLength() > 0:
            message = self.receiver.getData()
            my_decoded_str = message.decode()
            response = json.loads(
                my_decoded_str, object_hook=lambda d: SimpleNamespace(**d))
            callback(response)
            self.receiver.nextPacket()

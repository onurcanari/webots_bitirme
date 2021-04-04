from controller import Supervisor
from models.location import Location
from models.rotation import Rotation

ROBOT_SPEED = 5.0
TIME_STEP = 64


class IGroundRobot(Supervisor):
    def __init__(self, robot_id):
        super().__init__()
        self.robot_id = int(robot_id)
        self.distance_sensors = []
        self.wheels = []

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

    @property
    def robot_location(self):
        return self._robot_location

    @property
    def robot_rotation(self):
        return self._robot_rotation

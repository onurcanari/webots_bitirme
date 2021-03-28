from controller import Supervisor


class GroundRobot(Supervisor):

    def __init__(self, robot_name: str):
        self.robot_name = robot_name
        self.robot_id = robot_name[5]
        print("Setup ground robot:", name, "Robot ID:", robot_id)
        self.setup()

    def setup(self):
        self.translation_field = getSelf().getField("translation")

        print("Getting distance sensors and enable them...")
        ds_names = ["ds_right", "ds_left"]

        for i in range(3):
            distance_sensors[i] = getDistanceSensor(ds_names[i])
            distance_sensors[i].enable(TIME_STEP)

        print("Get and reposition motors..")
        wheels_names = {"wheel1", "wheel2", "wheel3", "wheel4"}

        for i in range(5):
            wheels[i] = getMotor(wheels_names[i])
            wheels[i].setPosition(INFINITY)
            wheels[i].setVelocity(0.0)

        print("Get and Set Emitter")
        emitter = getEmitter("emitter")
        emitter.setChannel(-1)
        print("Get and set Receiver")
        receiver = getReceiver("receiver")
        receiver.setChannel(-1)
        receiver.enable(TIME_STEP)
        print("Setup Passed")

    def updateLocation():
        self._robot_location = Location(self.translation_field.getSFVec3f())

    @property
    def robot_location():
        return _robot_location;

    def saveRobotLocation():
        pass;

    def run():
        print("Start robot")
        while step(TIME_STEP)!= -1:
            updateLocation();
        

from controller import Supervisor
from models.location import Location
from models.rotation import Rotation
from models.message import Message, MessageType

import json
from types import SimpleNamespace

ROBOT_SPEED = 5.0
TIME_STEP = 64


class IGroundRobot(Supervisor):
    def __init__(self):
        super().__init__()
        self.setup()

    def setup(self):
        self.root_node = self.getFromDef("mine0")
        self.translation_field = self.root_node.getField("translation")
        self.rotation_field = self.root_node.getField("rotation")
        self.emitter = self.getDevice("emitter")
        self.emitter.setChannel(-1)
        print("Get and set Receiver")
        self.receiver = self.getDevice("receiver")
        self.receiver.setChannel(-1)
        self.receiver.enable(TIME_STEP)

    def _send_message(self, message):
        try:
            json_data = json.dumps(message, default=lambda o: o.__dict__, indent=4)
            my_str_as_bytes = str.encode(json_data)
            # if message.type == MessageType.FIELD_UPDATE:
            #     logging.debug("Inside of send message: ".format(my_str_as_bytes))
            self.emitter.send(my_str_as_bytes)
        except Exception as e:
            print("Exception occurred.", e)

    def get_message(self, callback):
        if self.receiver.getQueueLength() > 0:
            message = self.receiver.getData()
            my_decoded_str = message.decode()
            response = json.loads(
                my_decoded_str, object_hook=lambda d: SimpleNamespace(**d))
            callback(response)
            self.receiver.nextPacket()

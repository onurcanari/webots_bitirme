from enum import Enum


class MessageType(Enum):
    NEW_ROBOT_LOCATION = 0,
    FIELD_UPDATE = 1


class Message:
    def __init__(self, robot_id: int, content: object, message_type: MessageType):
        self.robot_id = robot_id
        self.message = content
        self.type = message_type

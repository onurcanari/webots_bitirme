from enum import Enum


class MessageType(str, Enum):
    NEW_ROBOT_LOCATION = "NEW_ROBOT_LOCATION",
    FIELD_UPDATE = "FIELD_UPDATE",
    NEW_AVAIBLE_FIELDS = "NEW_AVAIBLE_FIELDS"

class Message:
    def __init__(self, robot_id: int, content: object, message_type: MessageType):
        self.robot_id = robot_id
        self.content = content
        self.type = message_type

from enum import Enum

class Status(Enum):
    STARTED = 0,
    CONTINUING = 1,
    COMPLETED = 2

class State(Enum):
    IDLE = 0,
    GO_TO_LOCATION = 1,
    CHANGE_ROTATION = 2,
    GO_COVERAGE = 3


class RobotState:
    def __init__(self, state, status = None):
        self.state=state
        if not status:
            self.status = Status.STARTED

    def complete(self):
        self.status = Status.COMPLETED
    
    def continue_pls(self):
        self.status = Status.CONTINUING
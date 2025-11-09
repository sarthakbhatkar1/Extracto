from enum import Enum

class TaskStatumEnum(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    SUCCESS = "Success"
    FAILURE = "Failure"
    
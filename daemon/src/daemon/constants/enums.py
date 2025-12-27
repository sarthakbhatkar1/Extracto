from enum import Enum


class TaskStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class StepMethod(str, Enum):
    INGESTING = "INGESTING"
    PARSING = "PARSING"
    EXTRACTING = "EXTRACTING"
    SUMMARIZING = "SUMMARIZING"

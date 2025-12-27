
from datetime import datetime
from pydantic import BaseModel, Field

from daemon.constants.enums import TaskStatus, StepMethod
from daemon.utils.util import get_current_datetime


class StepModel(BaseModel):
    method: str
    status: str
    started_at: datetime
    completed_at: datetime
    error: str = Field(default=str)


class StatusModel(BaseModel):
    status: str
    metadata: list[StepModel] = Field(default=list)


def init_task_status():
    return StatusModel(
        status=TaskStatus.NOT_STARTED.value,
    )


def start_step(task, method: StepMethod):
    task.STATUS["status"] = TaskStatus.IN_PROGRESS.value
    task.STATUS["metadata"].append(
        StepMethod(
            method=method.value,
            status=TaskStatus.IN_PROGRESS.value,
            started_at=get_current_datetime(),
            completed_at=None,
            error=None
        )
    )


    task.STATUS["metadata"].append({
        "method": method.value,
        "status": TaskStatus.IN_PROGRESS.value,
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "error": None
    })


def complete_step(task, method: StepMethod):
    for step in task.STATUS["metadata"]:
        if (
            step["method"] == method.value
            and step["status"] == TaskStatus.IN_PROGRESS.value
        ):
            step["status"] = TaskStatus.SUCCESS.value
            step["completed_at"] = datetime.utcnow().isoformat()
            break

    if all(s["status"] == TaskStatus.SUCCESS.value for s in task.STATUS["metadata"]):
        task.STATUS["status"] = TaskStatus.SUCCESS.value


def fail_step(task, method: StepMethod, error: str):
    for step in task.STATUS["metadata"]:
        if (
            step["method"] == method.value
            and step["status"] == TaskStatus.IN_PROGRESS.value
        ):
            step["status"] = TaskStatus.FAILURE.value
            step["completed_at"] = datetime.utcnow().isoformat()
            step["error"] = error
            break

    task.STATUS["status"] = TaskStatus.FAILURE.value

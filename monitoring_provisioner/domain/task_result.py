from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from common.domain import Domain


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

@dataclass
class TaskResult(Domain):
    """
    TaskResult 도메인 객체
    """
    FIELD_ID           = "id"
    FIELD_TASK_ID      = "task_id"
    FIELD_TASK_NAME    = "task_name"
    FIELD_STATUS       = "status"
    FIELD_RESULT       = "result"
    FIELD_DATE_CREATED = "date_created"
    FIELD_DATE_STARTED = "date_started"
    FIELD_DATE_DONE    = "date_done"
    FIELD_TRACEBACK    = "traceback"
    FIELD_RETRIES      = "retries"

    id: str
    task_id: str
    task_name: str
    status: TaskStatus
    result: Any
    date_created: str
    date_started: str | None
    date_done: str | None
    traceback: str | None
    retries: int
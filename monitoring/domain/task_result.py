from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from pyparsing import C

from common.domain import Domain


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class MonitoringDashboardTaskName(StrEnum):
    CREATE_DASHBOARD_USER_FOLDER = "create_dashboard_user_folder"
    CREATE_DASHBOARD_SERVICE_ACCOUNT = "create_dashboard_service_account"

    CREATE_DASHBOARD_SERVICE_TOKEN = "create_dashboard_service_token"
    WRAP_CREATE_DASHBOARD_SERVICE_TOKEN = "wrap_create_dashboard_service_token"

    SET_FOLDER_PERMISSIONS = "set_folder_permissions"
    WRAP_SET_FOLDER_PERMISSIONS = "wrap_set_folder_permissions"

    CREATE_DASHBOARD = "create_dashboard"
    WRAP_CREATE_DASHBOARD = "wrap_create_dashboard"

    CREATE_PUBLIC_DASHBOARD = "create_public_dashboard"
    WRAP_CREATE_PUBLIC_DASHBOARD = "wrap_create_public_dashboard"

    GET_GRAFANA_DASHBOARD = "get_grafana_dashboard"
    GET_GRAFANA_FOLDERS = "get_grafana_folders"


@dataclass
class TaskResult(Domain):
    """
    TaskResult 도메인 객체
    """

    FIELD_ID = "id"
    FIELD_TASK_NAME = "task_name"
    FIELD_STATUS = "status"
    FIELD_RESULT = "result"
    FIELD_DATE_CREATED = "date_created"
    FIELD_DATE_STARTED = "date_started"
    FIELD_DATE_DONE = "date_done"
    FIELD_TRACEBACK = "traceback"
    FIELD_RETRIES = "retries"

    id: str
    task_name: str
    status: TaskStatus
    date_created: str | None = None
    result: Any | None = None
    date_started: str | None = None
    date_done: str | None = None
    traceback: str | None = None
    retries: int = 0

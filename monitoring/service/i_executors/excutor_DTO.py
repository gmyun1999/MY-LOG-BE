from dataclasses import dataclass
from typing import Any

from user.domain.user import User


@dataclass
class BaseProvisionDTO:
    user: User
    project_id: str
    folder_task_id: str
    account_task_id: str
    token_task_id: str
    perm_task_id: str
    folder_name: str
    account_name: str
    token_name: str


@dataclass
class DashboardProvisionDTO:
    user: User
    dashboard_task_id: str
    public_dashboard_task_id: str
    dashboard_title: str
    dashboard_json_config: dict[str, Any]
    project_id: str
    finalize_task_id: str

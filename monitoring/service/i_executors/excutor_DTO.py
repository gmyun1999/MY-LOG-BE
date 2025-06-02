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


# ── 각 태스크 전용 DTO ─────────────────────────────────────────
@dataclass
class CreateUserFolderDTO:
    task_id: str
    user_id: str
    folder_name: str


@dataclass
class CreateServiceAccountDTO:
    task_id: str
    project_id: str
    account_name: str
    user_id: str


@dataclass
class CreateServiceTokenDTO:
    task_id: str
    project_id: str
    token_name: str


@dataclass
class SetFolderPermissionsDTO:
    task_id: str
    user_id: str
    project_id: str


@dataclass
class CreateDashboardDTO:
    task_id: str
    user_id: str
    project_id: str
    dashboard_title: str
    dashboard_config: dict[str, Any]


@dataclass
class CreatePublicDashboardDTO:
    task_id: str
    project_id: str


@dataclass
class FinalizeDashboardDTO:
    task_id: str
    user_id: str
    project_id: str


@dataclass
class ProvisionFailureDTO:
    task_id: str
    project_id: str

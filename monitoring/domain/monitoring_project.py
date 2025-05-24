from dataclasses import dataclass
from enum import StrEnum

from common.domain import Domain
from monitoring.domain.log_agent.agent_provision_context import AgentProvisioningContext
from monitoring.domain.visualization_platform import service_account
from monitoring.domain.visualization_platform.dashboard import (
    Dashboard,
    PublicDashboard,
)


class MonitoringType(StrEnum):
    LOG = "LOG"
    METRIC = "METRIC"


class ProjectStatus(StrEnum):
    INITIATED = "INITIATED"  # 프로젝트 생성 요청이 들어온 직후 (아직 작업 시작 전)
    IN_PROGRESS = "IN_PROGRESS"  # Celery 태스크들이 실행 중인 상태
    READY = "READY"  # 모든 프로비저닝 태스크 완료, 사용 가능
    FAILED = "FAILED"  # 하나 이상의 태스크 실패


@dataclass
class MonitoringProject(Domain):

    FIELD_ID = "id"
    FIELD_USER_ID = "user_id"
    FIELD_NAME = "name"
    FIELD_PROJECT_TYPE = "project_type"
    FIELD_STATUS = "status"
    FIELD_SERVICE_ACCOUNT_ID = "service_account_id"
    FIELD_DESCRIPTION = "description"
    FIELD_DASHBOARD_ID = "dashboard_id"
    FIELD_PUBLIC_DASHBOARD_ID = "public_dashboard_id"
    FIELD_USER_FOLDER_ID = "user_folder_id"
    FIELD_AGENT_CONTEXT = "agent_context"

    id: str
    user_id: str
    name: str
    project_type: MonitoringType
    status: ProjectStatus = ProjectStatus.INITIATED
    service_account_id: str | None = None
    description: str | None = None
    dashboard_id: str | None = None
    public_dashboard_id: str | None = None
    user_folder_id: str | None = None
    agent_context: AgentProvisioningContext | None = None


@dataclass
class MonitoringProjectWithDashboardDto(Domain):
    FIELD_ID = "id"
    FIELD_USER_ID = "user_id"
    FIELD_NAME = "name"
    FIELD_PROJECT_TYPE = "project_type"
    FIELD_STATUS = "status"
    FIELD_SERVICE_ACCOUNT_ID = "service_account_id"
    FIELD_DASHBOARD = "dashboard"
    FIELD_PUBLIC_DASHBOARD_ID = "public_dashboard_id"
    FIELD_USER_FOLDER_ID = "user_folder_id"
    FIELD_AGENT_CONTEXT = "agent_context"
    FIELD_DESCRIPTION = "description"

    id: str
    user_id: str
    name: str
    project_type: MonitoringType
    status: ProjectStatus
    service_account_id: str | None = None
    description: str | None = None
    user_folder_id: str | None = None
    dashboard: Dashboard | None = None
    public_dashboard_id: str | None = None
    agent_context: AgentProvisioningContext | None = None


@dataclass
class MonitoringProjectWithPublicDashboardDto(Domain):
    FIELD_ID = "id"
    FIELD_USER_ID = "user_id"
    FIELD_NAME = "name"
    FIELD_PROJECT_TYPE = "project_type"
    FIELD_STATUS = "status"
    FIELD_SERVICE_ACCOUNT_ID = "service_account_id"
    FIELD_DASHBOARD = "dashboard"
    FIELD_PUBLIC_DASHBOARD = "public_dashboard"
    FIELD_USER_FOLDER_ID = "user_folder_id"
    FIELD_AGENT_CONTEXT = "agent_context"
    FIELD_DESCRIPTION = "description"

    id: str
    user_id: str
    name: str
    project_type: MonitoringType
    status: ProjectStatus
    service_account_id: str | None = None
    description: str | None = None
    user_folder_id: str | None = None
    dashboard_id: str | None = None
    agent_context: AgentProvisioningContext | None = None
    public_dashboard: PublicDashboard | None = None


@dataclass
class MonitoringProjectWithBothDashboardsDto(Domain):
    FIELD_ID = "id"
    FIELD_USER_ID = "user_id"
    FIELD_NAME = "name"
    FIELD_PROJECT_TYPE = "project_type"
    FIELD_STATUS = "status"
    FIELD_SERVICE_ACCOUNT_ID = "service_account_id"
    FIELD_DASHBOARD = "dashboard"
    FIELD_PUBLIC_DASHBOARD = "public_dashboard"
    FIELD_USER_FOLDER_ID = "user_folder_id"
    FIELD_AGENT_CONTEXT = "agent_context"
    FIELD_DESCRIPTION = "description"

    id: str
    user_id: str
    name: str
    project_type: MonitoringType
    status: ProjectStatus
    service_account_id: str | None = None
    description: str | None = None
    user_folder_id: str | None = None
    dashboard: Dashboard | None = None
    agent_context: AgentProvisioningContext | None = None
    public_dashboard: PublicDashboard | None = None

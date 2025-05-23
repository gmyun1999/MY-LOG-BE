from dataclasses import dataclass
from enum import StrEnum

from common.domain import Domain
from monitoring.domain.log_agent.agent_provision_context import AgentProvisioningContext


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
    id: str
    user_id: str
    name: str
    project_type: MonitoringType
    status: ProjectStatus = ProjectStatus.INITIATED
    description: str | None = None
    dashboard_id: str | None = None
    user_folder_id: str | None = None
    agent_context: AgentProvisioningContext | None = None

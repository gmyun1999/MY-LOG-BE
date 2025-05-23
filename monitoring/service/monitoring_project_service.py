import uuid

from django.db import transaction

from common.domain import PagedResult
from common.service.paging import Paginator
from monitoring.domain.i_repo.i_monitoring_project_repo import IMonitoringProjectRepo
from monitoring.domain.log_agent.agent_provision_context import (
    AgentProvisioningContext,
    PlatformType,
)
from monitoring.domain.log_agent.log_collector import LogCollectorConfigContext
from monitoring.domain.log_agent.log_router import LogRouterConfigContext
from monitoring.domain.monitoring_project import (
    MonitoringProject,
    MonitoringProjectWithDashboardDto,
    MonitoringType,
    ProjectStatus,
)
from monitoring.infra.repo.monitoring_project_repo import MonitoringProjectRepo
from monitoring.service.exceptions import (
    AlreadyExistException,
    AlreadyProvisioningException,
    NotExistException,
    NotImplementedException,
    PermissionException,
)
from monitoring.service.harvester_agent_service import HarvesterAgentService
from monitoring.service.monitoring_provision_service import MonitoringProvisionService
from user.domain.user import User


class MonitoringProjectService:
    def __init__(self):
        # TODO: DI
        self.project_repo: IMonitoringProjectRepo = MonitoringProjectRepo()
        self.harvester_agent_service = HarvesterAgentService()
        self.monitoring_provision_service = MonitoringProvisionService()

    def create_project(
        self,
        project_id: str,
        user_id: str,
        name: str,
        project_type: MonitoringType,
        description: str | None = None,
        dashboard_id: str | None = None,
        user_folder_id: str | None = None,
        service_account_id: str | None = None,
        agent_context: AgentProvisioningContext | None = None,
    ) -> MonitoringProject:
        project = MonitoringProject(
            id=project_id,
            user_id=user_id,
            name=name,
            project_type=project_type,
            description=description,
            dashboard_id=dashboard_id,
            user_folder_id=user_folder_id,
            agent_context=agent_context,
            service_account_id=service_account_id,
        )
        self.project_repo.save(project)
        return project

    def get_project_detail(self, project_id: str) -> MonitoringProjectWithDashboardDto:
        project_with_dashboard = self.project_repo.find_with_dashboard_dto(project_id)
        if not project_with_dashboard:
            raise NotExistException()
        return project_with_dashboard

    def get_my_projects_detail(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> PagedResult[MonitoringProjectWithDashboardDto]:
        all_dtos = self.project_repo.find_all_with_dashboard_dto_by_user(user_id)
        return Paginator.paginate(all_dtos, page=page, page_size=page_size)

    def start_log_project_step1(
        self,
        user: User,
        project_name: str,
        project_description: str,
        log_collector_ctx: LogCollectorConfigContext,
        log_router_ctx: LogRouterConfigContext,
        platform: PlatformType = PlatformType.WINDOWS,
    ):
        """
        create_project 호출 및 프로젝트 생성
        harvester_agent_service.download_agent_set_up_script 호출 및 다운로드
        다운로드 링크 반환
        """
        with transaction.atomic():
            project_id = str(uuid.uuid4())
            agent_ctx = self.harvester_agent_service.download_log_agent_set_up_script(
                resource_id=project_id,
                log_collector_ctx=log_collector_ctx,
                log_router_ctx=log_router_ctx,
                platform=platform,
            )

            project = self.create_project(
                project_id=project_id,
                user_id=user.id,
                name=project_name,
                project_type=MonitoringType.LOG,
                description=project_description,
                dashboard_id=None,
                service_account_id=None,
                user_folder_id=None,
                agent_context=agent_ctx,
            )
            return project

    def check_permission(self, user: User, project_id: str) -> bool:
        """
        프로젝트에 대한 권한 체크
        """
        is_exist = self.project_repo.exists_by_id_and_user_id(
            project_id=project_id, user_id=user.id
        )
        if not is_exist:
            raise PermissionException()
        return True

    def start_log_project_step2(self, user, project_id: str) -> None:
        """
        provision_dashboard 호출 및 대시보드 생성 (근데 이건 비동기잖아?)
        """
        project = self.project_repo.find_by_id(project_id)
        if not project:
            raise NotExistException()

        self.check_permission(user, project_id)
        if project.status == ProjectStatus.FAILED:
            raise NotImplementedException()

        if project.status == ProjectStatus.READY:
            raise AlreadyExistException()

        if project.status == ProjectStatus.IN_PROGRESS:
            raise AlreadyProvisioningException()

        need_base_provisioning = (
            self.monitoring_provision_service.check_if_need_base_provisioning(
                user, project_id
            )
        )

        # 로그 대시보드 프로비저닝
        self.monitoring_provision_service.provision_log_dashboard(
            user=user,
            monitoring_project_id=project_id,
            skip_base_provisioning=not need_base_provisioning,
        )

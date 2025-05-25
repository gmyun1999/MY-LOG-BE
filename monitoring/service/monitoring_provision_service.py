import uuid
from typing import Any

from django.utils import timezone

from monitoring.domain.i_repo.i_monitoring_project_repo import IMonitoringProjectRepo
from monitoring.domain.i_repo.i_task_result_repo import ITaskResultRepo
from monitoring.domain.i_repo.i_visualization_platform_repo.i_dashbaord_repo import (
    IDashboardRepo,
    IPublicDashboardRepo,
)
from monitoring.domain.i_repo.i_visualization_platform_repo.i_folder_permission_repo import (
    IFolderPermissionRepo,
)
from monitoring.domain.i_repo.i_visualization_platform_repo.i_folder_repo import (
    IFolderRepo,
)
from monitoring.domain.i_repo.i_visualization_platform_repo.i_service_account_repo import (
    IServiceAccountRepo,
)
from monitoring.domain.monitoring_project import MonitoringProject
from monitoring.domain.task_result import (
    MonitoringDashboardTaskName,
    TaskResult,
    TaskStatus,
)
from monitoring.infra.celery.task_executor.grafana_executor import GrafanaTaskExecutor
from monitoring.infra.grafana.grafana_template_provider import GrafanaTemplateProvider
from monitoring.infra.repo.monitoring_project_repo import MonitoringProjectRepo
from monitoring.infra.repo.task_result_repo import TaskResultRepo
from monitoring.infra.repo.visualization_platform_repo.dashboard_repo import (
    DashboardRepo,
    PublicDashboardRepo,
)
from monitoring.infra.repo.visualization_platform_repo.folder_permission_repo import (
    FolderPermissionRepo,
)
from monitoring.infra.repo.visualization_platform_repo.folder_repo import FolderRepo
from monitoring.infra.repo.visualization_platform_repo.service_account_repo import (
    ServiceAccountRepo,
)
from monitoring.service.i_executors.excutor_DTO import (
    CreateDashboardDTO,
    CreatePublicDashboardDTO,
    CreateServiceAccountDTO,
    CreateServiceTokenDTO,
    CreateUserFolderDTO,
    FinalizeDashboardDTO,
    ProvisionFailureDTO,
    SetFolderPermissionsDTO,
)
from monitoring.service.i_executors.visualization_platform_executor import (
    VisualizationPlatformTaskExecutor,
)
from monitoring.service.i_visualization_platform.i_template_provider import (
    VisualizationPlatformTemplateProvider,
)
from user.domain.user import User


class MonitoringProvisionService:
    def __init__(self):
        # TODO: DI 적용 예정
        self.task_executor: VisualizationPlatformTaskExecutor = GrafanaTaskExecutor()
        self.task_result_repo: ITaskResultRepo = TaskResultRepo()
        self.template_provider: VisualizationPlatformTemplateProvider = (
            GrafanaTemplateProvider()
        )
        self.folder_repo: IFolderRepo = FolderRepo()
        self.account_repo: IServiceAccountRepo = ServiceAccountRepo()
        self.folder_permissions_repo: IFolderPermissionRepo = FolderPermissionRepo()
        self.dashboard_repo: IDashboardRepo = DashboardRepo()
        self.public_dashboard_repo: IPublicDashboardRepo = PublicDashboardRepo()
        self.monitoring_project_repo: IMonitoringProjectRepo = MonitoringProjectRepo()

    def _make_folder_name(self, user_id: str, user_name: str) -> str:
        return f"User_{user_id}_{user_name}'s Folder"

    def _make_account_name(self, user_id: str, project_id: str) -> str:
        return f"service-{user_id}-{project_id}"

    def _make_token_name(self, user_id: str, project_id: str) -> str:
        return f"token-{user_id}-{project_id}"

    def _make_dashboard_title(self, user: User, project_name: str) -> str:
        return f"{user.name}'s Logs Dashboard for {project_name}"

    def _save_task_pending(self, task_name: str) -> str:
        task_id = str(uuid.uuid4())
        self.task_result_repo.save(
            TaskResult(
                id=task_id,
                task_name=task_name,
                status=TaskStatus.PENDING,
                date_created=timezone.now().isoformat(),
            )
        )
        return task_id

    def create_logs_dashboard_template(
        self, user: User, project_name: str
    ) -> dict[str, Any]:
        return self.template_provider.render_logs_dashboard_json(
            user_id=user.id,
            dashboard_title=self._make_dashboard_title(user, project_name),
            dashboard_uid=str(uuid.uuid4()),
        )

    def provision_log_dashboard(
        self,
        user: User,
        project: MonitoringProject,
    ) -> str:
        # 1) DTO 생성 task 저장은 bulk로 처리함

        monitoring_project_id = project.id

        user_folder_dto = None
        if not self.folder_repo.find_by_user_id(user.id):
            folder_id = str(uuid.uuid4())
            user_folder_dto = CreateUserFolderDTO(
                task_id=folder_id,
                user_id=user.id,
                folder_name=self._make_folder_name(user.id, user.name),
            )

        service_account = self.account_repo.find_by_project_id(monitoring_project_id)
        service_account_dto = None
        if not service_account:
            account_id = str(uuid.uuid4())
            service_account_dto = CreateServiceAccountDTO(
                task_id=account_id,
                project_id=monitoring_project_id,
                account_name=self._make_account_name(user.id, monitoring_project_id),
                user_id=user.id,
            )

        service_token_dto = None
        if (service_account_dto or service_account) and not (
            service_account and service_account.token
        ):
            token_id = str(uuid.uuid4())
            service_token_dto = CreateServiceTokenDTO(
                task_id=token_id,
                project_id=monitoring_project_id,
                token_name=self._make_token_name(user.id, monitoring_project_id),
            )

        perm = None
        if service_account:
            perm = self.folder_permissions_repo.find_by_service_account_id(
                service_account.id
            )
        permissions_dto = None
        if not perm:
            perm_id = str(uuid.uuid4())
            permissions_dto = SetFolderPermissionsDTO(
                task_id=perm_id,
                user_id=user.id,
                project_id=monitoring_project_id,
            )

        # dashboard
        exists = self.dashboard_repo.find_by_project_id(
            project_id=monitoring_project_id
        )
        dashboard_dto = None
        if not exists:
            dash_id = str(uuid.uuid4())
            dashboard_dto = CreateDashboardDTO(
                task_id=dash_id,
                user_id=user.id,
                project_id=monitoring_project_id,
                dashboard_title=self._make_dashboard_title(user, project.name),
                dashboard_config=self.create_logs_dashboard_template(
                    user, project.name
                ),
            )

        # public dashboard
        exists_public = self.public_dashboard_repo.find_by_project_id(
            project_id=monitoring_project_id
        )
        public_dto = None
        if not exists_public:
            pub_id = str(uuid.uuid4())
            public_dto = CreatePublicDashboardDTO(
                task_id=pub_id,
                project_id=monitoring_project_id,
            )

        finalize_id = str(uuid.uuid4())
        finalize_dto = FinalizeDashboardDTO(
            task_id=finalize_id,
            user_id=user.id,
            project_id=monitoring_project_id,
        )
        failure_dto = ProvisionFailureDTO(
            task_id=finalize_id,
            project_id=monitoring_project_id,
        )

        # 2) bulk PENDING TaskResult 생성
        now = timezone.now().isoformat()
        to_upsert: list[TaskResult] = []
        for dto, name in [
            (user_folder_dto, MonitoringDashboardTaskName.CREATE_DASHBOARD_USER_FOLDER),
            (
                service_account_dto,
                MonitoringDashboardTaskName.CREATE_DASHBOARD_SERVICE_ACCOUNT,
            ),
            (
                service_token_dto,
                MonitoringDashboardTaskName.CREATE_DASHBOARD_SERVICE_TOKEN,
            ),
            (permissions_dto, MonitoringDashboardTaskName.SET_FOLDER_PERMISSIONS),
            (dashboard_dto, MonitoringDashboardTaskName.CREATE_DASHBOARD),
            (public_dto, MonitoringDashboardTaskName.CREATE_PUBLIC_DASHBOARD),
            (finalize_dto, MonitoringDashboardTaskName.FINALIZE_DASHBOARD),
        ]:
            if dto:
                to_upsert.append(
                    TaskResult(
                        id=dto.task_id,
                        task_name=name.value,
                        status=TaskStatus.PENDING,
                        date_created=now,
                    )
                )
        if to_upsert:
            self.task_result_repo.bulk_upsert(to_upsert)

        # 3) dispatch
        return self.task_executor.dispatch_provision_dashboard_workflow(
            user_folder=user_folder_dto,
            service_account=service_account_dto,
            service_token=service_token_dto,
            permissions=permissions_dto,
            dashboard=dashboard_dto,
            public_dashboard=public_dto,
            finalize_dashboard=finalize_dto,
            failure=failure_dto,
        )

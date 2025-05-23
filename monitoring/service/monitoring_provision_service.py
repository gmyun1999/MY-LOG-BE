import uuid
from typing import Any

from django.utils import timezone

from monitoring.domain.i_repo.i_task_result_repo import ITaskResultRepo
from monitoring.domain.i_repo.i_visualization_platform_repo.i_folder_permission_repo import (
    IFolderPermissionRepo,
)
from monitoring.domain.i_repo.i_visualization_platform_repo.i_folder_repo import (
    IFolderRepo,
)
from monitoring.domain.i_repo.i_visualization_platform_repo.i_service_account_repo import (
    IServiceAccountRepo,
)
from monitoring.domain.task_result import (
    MonitoringDashboardTaskName,
    TaskResult,
    TaskStatus,
)
from monitoring.infra.celery.task_executor.grafana_executor import GrafanaTaskExecutor
from monitoring.infra.grafana.grafana_template_provider import GrafanaTemplateProvider
from monitoring.infra.repo.task_result_repo import TaskResultRepo
from monitoring.infra.repo.visualization_platform_repo.folder_permission_repo import (
    FolderPermissionRepo,
)
from monitoring.infra.repo.visualization_platform_repo.folder_repo import FolderRepo
from monitoring.infra.repo.visualization_platform_repo.service_account_repo import (
    ServiceAccountRepo,
)
from monitoring.service.i_executors.excutor_DTO import (
    BaseProvisionDTO,
    DashboardProvisionDTO,
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

    def _make_folder_name(self, user_id: str, user_name: str) -> str:
        return f"User_{user_id}_{user_name}'s Folder"

    def _make_account_name(self, user_id: str) -> str:
        return f"service-{user_id}"

    def _make_token_name(self, user_id: str) -> str:
        return f"token-{user_id}"

    def _make_dashboard_title(self, user: User) -> str:
        return f"{user.name}'s Logs Dashboard"

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

    def create_logs_dashboard_template(self, user: User) -> dict[str, Any]:
        return self.template_provider.render_logs_dashboard_json(
            user_id=user.id,
            dashboard_title=self._make_dashboard_title(user),
            dashboard_uid=str(uuid.uuid4()),
        )

    def check_if_need_base_provisioning(self, user: User) -> bool:
        folder = self.folder_repo.find_by_user_id(user.id)
        if folder is None:
            return True

        service_account = self.account_repo.find_by_user_id(user.id)
        if service_account is None:
            return True

        permission = self.folder_permissions_repo.find_by_service_account_id(
            service_account.id
        )
        if permission is None:
            return True

        # base provisioning이 필요하지 않음
        return False

    def provision_base_resources(self, user: User) -> str:
        """
        기본 리소스 프로비저닝
        1) 사용자 폴더 생성
        2) 서비스 계정 생성
        3) 서비스 토큰 생성 (wrapper)
        4) 폴더 권한 설정 (wrapper)
        전체 단계를 하나의 chain 으로 묶어 실행
        """

        folder_task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_DASHBOARD_USER_FOLDER
        )
        account_task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_DASHBOARD_SERVICE_ACCOUNT
        )
        token_task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_DASHBOARD_SERVICE_TOKEN
        )
        perm_task_id = self._save_task_pending(
            MonitoringDashboardTaskName.SET_FOLDER_PERMISSIONS
        )
        folder_name = self._make_folder_name(user.id, user.name)
        account_name = self._make_account_name(user.id)
        token_name = self._make_token_name(user.id)

        base_dto = BaseProvisionDTO(
            user=user,
            folder_task_id=folder_task_id,
            account_task_id=account_task_id,
            token_task_id=token_task_id,
            perm_task_id=perm_task_id,
            folder_name=folder_name,
            account_name=account_name,
            token_name=token_name,
        )

        return self.task_executor.dispatch_provision_base_resources_workflow(
            base_dto=base_dto,
        )

    def provision_log_dashboard(
        self,
        user: User,
        monitoring_project_id: str,
        skip_base_provisioning: bool = False,  # 기본 리소스 스킵 여부
    ) -> str:
        """
        1) dashboard template 생성
        2) Task ID 생성 (skip 여부에 따라)
        3) BaseProvisionDTO / DashboardProvisionDTO 생성
        4) dispatch
        """

        dash_board_template = self.create_logs_dashboard_template(user)

        # Dashboard 관련 Task ID
        dash_task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_DASHBOARD
        )
        pub_task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_PUBLIC_DASHBOARD
        )
        finalize_task_id = self._save_task_pending(
            MonitoringDashboardTaskName.FINALIZE_DASHBOARD
        )
        # 기본 리소스 Task ID는 skip 여부에 따라 생성
        if not skip_base_provisioning:
            folder_task_id = self._save_task_pending(
                MonitoringDashboardTaskName.CREATE_DASHBOARD_USER_FOLDER
            )
            account_task_id = self._save_task_pending(
                MonitoringDashboardTaskName.CREATE_DASHBOARD_SERVICE_ACCOUNT
            )
            token_task_id = self._save_task_pending(
                MonitoringDashboardTaskName.CREATE_DASHBOARD_SERVICE_TOKEN
            )
            perm_task_id = self._save_task_pending(
                MonitoringDashboardTaskName.SET_FOLDER_PERMISSIONS
            )

            folder_name = self._make_folder_name(user.id, user.name)
            account_name = self._make_account_name(user.id)
            token_name = self._make_token_name(user.id)

            base_dto = BaseProvisionDTO(
                user=user,
                folder_task_id=folder_task_id,
                account_task_id=account_task_id,
                token_task_id=token_task_id,
                perm_task_id=perm_task_id,
                folder_name=folder_name,
                account_name=account_name,
                token_name=token_name,
            )
        else:
            base_dto = None

        dash_dto = DashboardProvisionDTO(
            user=user,
            dashboard_task_id=dash_task_id,
            public_dashboard_task_id=pub_task_id,
            dashboard_title=self._make_dashboard_title(user),
            dashboard_json_config=dash_board_template,
            project_id=monitoring_project_id,
            finalize_task_id=finalize_task_id,
        )

        return self.task_executor.dispatch_provision_dashboard_workflow(
            dash_dto=dash_dto,
            base_dto=base_dto,
        )

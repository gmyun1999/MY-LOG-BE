import uuid

from django.utils import timezone

from monitoring_provisioner.domain.i_repo.i_task_result_repo import ITaskResultRepo
from monitoring_provisioner.domain.task_result import (
    MonitoringDashboardTaskName,
    TaskResult,
    TaskStatus,
)
from monitoring_provisioner.infra.celery.task_executor.grafana_executor import (
    GrafanaTaskExecutor,
)
from monitoring_provisioner.infra.repo.task_result_repo import TaskResultRepo
from monitoring_provisioner.service.i_executors.monitoring_dashboard_executor import (
    MonitoringDashboardTaskExecutor,
)
from user.domain.user import User


class MonitoringDashboardService:
    def __init__(self):
        # TODO: DI 적용 예정
        self.task_executor: MonitoringDashboardTaskExecutor = GrafanaTaskExecutor()
        self.task_result_repo: ITaskResultRepo = TaskResultRepo()

    def _make_folder_name(self, user_id: str, user_name: str) -> str:
        return f"User_{user_id}_{user_name}'s Folder"

    def _make_account_name(self, user_id: str) -> str:
        return f"service-{user_id}"

    def _make_token_name(self, user_id: str) -> str:
        return f"token-{user_id}"

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

    def create_user_folder(self, user_id: str, user_name: str) -> str:
        folder_name = self._make_folder_name(user_id, user_name)
        task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_DASHBOARD_USER_FOLDER
        )
        self.task_executor.dispatch_create_user_folder(task_id, user_id, folder_name)
        return task_id

    def create_service_account(self, user_id: str, role: str = "Viewer") -> str:
        account_name = self._make_account_name(user_id)
        task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_DASHBOARD_SERVICE_ACCOUNT
        )
        self.task_executor.dispatch_create_service_account(
            task_id, account_name, user_id, role
        )
        return task_id

    def create_service_token(self, service_account_id: int, user_id: str) -> str:
        token_name = self._make_token_name(user_id)
        task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_DASHBOARD_SERVICE_TOKEN
        )
        self.task_executor.dispatch_create_service_token(
            task_id, service_account_id, token_name
        )
        return task_id

    def set_folder_permissions(self, folder_uid: str, service_account_id: int) -> str:
        task_id = self._save_task_pending(
            MonitoringDashboardTaskName.SET_GRAFANA_FOLDER_PERMISSIONS
        )
        self.task_executor.dispatch_set_folder_permissions(
            task_id, folder_uid, service_account_id
        )
        return task_id

    def create_public_dashboard(self, dashboard_uid: str) -> str:
        task_id = self._save_task_pending(
            MonitoringDashboardTaskName.CREATE_PUBLIC_DASHBOARD
        )
        self.task_executor.dispatch_create_public_dashboard(task_id, dashboard_uid)
        return task_id

    # 체인
    def provision_user_folder(self, user: User) -> str:
        """
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
            MonitoringDashboardTaskName.SET_GRAFANA_FOLDER_PERMISSIONS
        )

        folder_name = self._make_folder_name(user.id, user.name)
        account_name = self._make_account_name(user.id)
        token_name = self._make_token_name(user.id)

        return self.task_executor.dispatch_provision_user_folder(
            user=user,
            folder_task_id=folder_task_id,
            account_task_id=account_task_id,
            token_task_id=token_task_id,
            perm_task_id=perm_task_id,
            folder_name=folder_name,
            account_name=account_name,
            token_name=token_name,
        )

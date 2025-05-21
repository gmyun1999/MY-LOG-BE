from celery import chain
from typing_extensions import override

from monitoring_provisioner.infra.celery.tasks.grafana_tasks import (
    task_create_grafana_folder,
    task_create_grafana_public_dashboard,
    task_create_grafana_service_account,
    task_create_grafana_service_token,
    task_get_grafana_dashboard,
    task_get_grafana_folders,
    task_set_grafana_folder_permissions,
    wrap_create_service_token,
    wrap_set_folder_permissions,
)
from monitoring_provisioner.service.i_executors.monitoring_dashboard_executor import (
    MonitoringDashboardTaskExecutor,
)
from user.domain.user import User


class GrafanaTaskExecutor(MonitoringDashboardTaskExecutor):
    # ─────────────────────────────────────────────────────────────────────────────
    # Signature generators
    # ─────────────────────────────────────────────────────────────────────────────
    def get_create_user_folder_sig(self, task_id: str, user_id: str, folder_name: str):
        return task_create_grafana_folder.si(task_id, user_id, folder_name).set(
            task_id=task_id
        )

    def get_create_service_account_sig(
        self, task_id: str, account_name: str, user_id: str, role: str = "Viewer"
    ):
        return task_create_grafana_service_account.si(
            task_id, account_name, user_id, role
        ).set(task_id=task_id)

    def get_create_service_token_sig(
        self, task_id: str, service_account_id: int, token_name: str
    ):
        return task_create_grafana_service_token.si(
            task_id, service_account_id, token_name
        ).set(task_id=task_id)

    def get_set_folder_permissions_sig(
        self, task_id: str, folder_uid: str, service_account_id: int
    ):
        return task_set_grafana_folder_permissions.si(
            task_id, folder_uid, service_account_id
        ).set(task_id=task_id)

    def get_create_public_dashboard_sig(self, task_id: str, dashboard_uid: str):
        return task_create_grafana_public_dashboard.si(task_id, dashboard_uid).set(
            task_id=task_id
        )

    def get_get_dashboard_by_uid_sig(self, task_id: str, dashboard_uid: str):
        return task_get_grafana_dashboard.si(task_id, dashboard_uid).set(
            task_id=task_id
        )

    def get_get_grafana_folders_sig(self, task_id: str):
        return task_get_grafana_folders.si(task_id).set(task_id=task_id)

    # ─────────────────────────────────────────────────────────────────────────────
    # Dispatchers
    # ─────────────────────────────────────────────────────────────────────────────
    @override
    def dispatch_create_user_folder(
        self, task_id: str, user_id: str, folder_name: str
    ) -> str:
        self.get_create_user_folder_sig(task_id, user_id, folder_name).apply_async()
        return task_id

    @override
    def dispatch_create_service_account(
        self, task_id: str, account_name: str, user_id: str, role: str = "Viewer"
    ) -> str:
        self.get_create_service_account_sig(
            task_id, account_name, user_id, role
        ).apply_async()
        return task_id

    @override
    def dispatch_create_service_token(
        self, task_id: str, service_account_id: int, token_name: str
    ) -> str:
        self.get_create_service_token_sig(
            task_id, service_account_id, token_name
        ).apply_async()
        return task_id

    @override
    def dispatch_set_folder_permissions(
        self, task_id: str, folder_uid: str, service_account_id: int
    ) -> str:
        self.get_set_folder_permissions_sig(
            task_id, folder_uid, service_account_id
        ).apply_async()
        return task_id

    @override
    def dispatch_create_public_dashboard(self, task_id: str, dashboard_uid: str) -> str:
        self.get_create_public_dashboard_sig(task_id, dashboard_uid).apply_async()
        return task_id

    @override
    def dispatch_get_dashboard_by_uid(self, task_id: str, dashboard_uid: str) -> str:
        self.get_get_dashboard_by_uid_sig(task_id, dashboard_uid).apply_async()
        return task_id

    @override
    def dispatch_get_grafana_folders(self, task_id: str) -> str:
        self.get_get_grafana_folders_sig(task_id).apply_async()
        return task_id

    # ─────────────────────────────────────────────────────────────────────────────
    # Provision chain
    # ─────────────────────────────────────────────────────────────────────────────
    @override
    def dispatch_provision_user_folder(
        self,
        user: User,
        folder_task_id: str,
        account_task_id: str,
        token_task_id: str,
        perm_task_id: str,
        folder_name: str,
        account_name: str,
        token_name: str,
    ) -> str:
        """
        유저 폴더 만들고 서비스 계정과 토큰을 생성한다음 권한 주는 태스크 체인
        1) Create user folder
        2) Create service account
        3) Create service token (wrapper)
        4) Set folder permissions (wrapper)
        """

        workflow = chain(
            self.get_create_user_folder_sig(
                task_id=folder_task_id, user_id=user.id, folder_name=folder_name
            ),
            self.get_create_service_account_sig(
                task_id=account_task_id, account_name=account_name, user_id=user.id
            ),
            wrap_create_service_token.si(token_task_id, user.id, token_name).set(
                task_id=token_task_id
            ),
            wrap_set_folder_permissions.si(perm_task_id, user.id).set(
                task_id=perm_task_id
            ),
        )

        result = workflow.apply_async()
        return result.id

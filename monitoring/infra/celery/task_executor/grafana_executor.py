from celery import chain
from typing_extensions import override

from monitoring.domain.visualization_platform import dashboard
from monitoring.infra.celery.tasks.grafana_tasks import (
    task_create_grafana_dashboard,
    task_create_grafana_folder,
    task_create_grafana_public_dashboard,
    task_create_grafana_service_account,
    task_create_grafana_service_token,
    task_get_grafana_dashboard,
    task_get_grafana_folders,
    task_set_grafana_folder_permissions,
)
from monitoring.infra.celery.tasks.monitoring_project_tasks import (
    finalize_monitoring_project,
    handle_monitoring_project_failure,
)
from monitoring.service.i_executors.excutor_DTO import (
    BaseProvisionDTO,
    DashboardProvisionDTO,
)
from monitoring.service.i_executors.visualization_platform_executor import (
    VisualizationPlatformTaskExecutor,
)


class GrafanaTaskExecutor(VisualizationPlatformTaskExecutor):
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

    def get_create_service_token_sig(self, task_id: str, user_id: str, token_name: str):
        return task_create_grafana_service_token.si(task_id, user_id, token_name).set(
            task_id=task_id
        )

    def get_set_folder_permissions_sig(self, task_id: str, user_id: str):
        return task_set_grafana_folder_permissions.si(task_id, user_id).set(
            task_id=task_id
        )

    def get_create_dashboard_sig(
        self,
        task_id: str,
        user_id: str,
        project_id: str,
        dashboard_title: str,
        dashboard_config: dict,
    ):
        return task_create_grafana_dashboard.si(
            task_id, user_id, project_id, dashboard_title, dashboard_config
        ).set(task_id=task_id)

    def get_create_public_dashboard_sig(self, task_id: str, user_id: str):
        return task_create_grafana_public_dashboard.si(task_id, user_id).set(
            task_id=task_id
        )

    def get_finalize_monitoring_project_sig(
        self, task_id: str, user_id: str, project_id: str
    ):
        return finalize_monitoring_project.si(task_id, user_id, project_id).set(
            task_id=task_id
        )

    def get_get_dashboard_by_uid_sig(self, task_id: str, dashboard_uid: str):
        return task_get_grafana_dashboard.si(task_id, dashboard_uid).set(
            task_id=task_id
        )

    def get_get_grafana_folders_sig(self, task_id: str):
        return task_get_grafana_folders.si(task_id).set(task_id=task_id)

    def build_base_resources_chain(
        self,
        dto: BaseProvisionDTO,
    ):
        """
        유저 폴더 생성 → 서비스 계정 생성 → 토큰 생성(wrapper) → 권한 설정(wrapper)
        """
        return chain(
            self.get_create_user_folder_sig(
                task_id=dto.folder_task_id,
                user_id=dto.user.id,
                folder_name=dto.folder_name,
            ),
            self.get_create_service_account_sig(
                task_id=dto.account_task_id,
                account_name=dto.account_name,
                user_id=dto.user.id,
            ),
            self.get_create_service_token_sig(
                task_id=dto.token_task_id,
                user_id=dto.user.id,
                token_name=dto.token_name,
            ),
            self.get_set_folder_permissions_sig(
                task_id=dto.perm_task_id,
                user_id=dto.user.id,
            ),
        )

    def build_dashboard_provision_chain(
        self,
        dash_dto: DashboardProvisionDTO,
        base_dto: BaseProvisionDTO | None = None,
    ):
        """
        기본 리소스 체인 이후 → 대시보드 생성 → 퍼블릭 대시보드 생성
        base_dto가 None이면 기본 리소스 체인은 제외
        """
        tasks = []

        if base_dto is not None:
            base_chain = self.build_base_resources_chain(base_dto)
            tasks.append(base_chain)

        tasks.append(
            self.get_create_dashboard_sig(
                task_id=dash_dto.dashboard_task_id,
                user_id=dash_dto.user.id,
                project_id=dash_dto.project_id,
                dashboard_title=dash_dto.dashboard_title,
                dashboard_config=dash_dto.dashboard_json_config,
            )
        )

        tasks.append(
            self.get_create_public_dashboard_sig(
                task_id=dash_dto.public_dashboard_task_id, user_id=dash_dto.user.id
            )
        )
        tasks.append(
            self.get_finalize_monitoring_project_sig(
                task_id=dash_dto.finalize_task_id,
                user_id=dash_dto.user.id,
                project_id=dash_dto.project_id,
            )
        )

        return chain(*tasks)

    # ─────────────────────────────────────────────────────────────────────────────
    # Provision chain
    # ─────────────────────────────────────────────────────────────────────────────
    @override
    def dispatch_provision_base_resources_workflow(
        self,
        dto: BaseProvisionDTO,
    ) -> str:
        """
        유저 폴더 만들고 서비스 계정과 토큰을 생성한다음 권한 주는 태스크 체인
        1) Create user folder
        2) Create service account
        3) Create service token (wrapper)
        4) Set folder permissions (wrapper)
        """

        workflow_chain = self.build_base_resources_chain(
            dto=dto,
        )
        result = workflow_chain.apply_async()
        return result.id

    @override
    def dispatch_provision_dashboard_workflow(
        self,
        dash_dto: DashboardProvisionDTO,
        base_dto: BaseProvisionDTO | None = None,
    ) -> str:
        """
        build_dashboard_provision_chain를 실행하여 비동기로 디스패치, 루트 task_id 반환
        """
        dashboard_chain = self.build_dashboard_provision_chain(
            dash_dto=dash_dto,
            base_dto=base_dto,
        )

        dashboard_chain.apply_async(
            link_error=handle_monitoring_project_failure.si(
                dash_dto.finalize_task_id, dash_dto.project_id
            )
        )

        return dash_dto.project_id

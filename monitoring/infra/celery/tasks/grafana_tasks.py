import uuid
from typing import Any

from django.db import transaction
from django.utils import timezone

from monitoring.domain.i_repo.i_task_result_repo import ITaskResultRepo
from monitoring.domain.i_repo.i_visualization_platform_repo.i_dashbaord_repo import (
    IDashboardRepo,
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
from monitoring.domain.task_result import TaskStatus
from monitoring.domain.visualization_platform.dashboard import Dashboard
from monitoring.domain.visualization_platform.folder import (
    FolderPermission,
    FolderPermissionLevel,
    UserFolder,
)
from monitoring.domain.visualization_platform.service_account import ServiceAccount
from monitoring.infra.celery.tasks.utils import locking_task
from monitoring.infra.grafana.grafana_api import GrafanaAPI
from monitoring.infra.repo.task_result_repo import TaskResultRepo
from monitoring.infra.repo.visualization_platform_repo.dashboard_repo import (
    DashboardRepo,
)
from monitoring.infra.repo.visualization_platform_repo.folder_permission_repo import (
    FolderPermissionRepo,
)
from monitoring.infra.repo.visualization_platform_repo.folder_repo import FolderRepo
from monitoring.infra.repo.visualization_platform_repo.service_account_repo import (
    ServiceAccountRepo,
)
from monitoring.service.i_visualization_platform.i_visualization_platform_provider import (
    VisualizationPlatformProvider,
)

# TODO: DI 적용 예정
grafana_api: VisualizationPlatformProvider = GrafanaAPI()
task_result_repo: ITaskResultRepo = TaskResultRepo()
folder_repo: IFolderRepo = FolderRepo()
service_account_repo: IServiceAccountRepo = ServiceAccountRepo()
folder_permission_repo: IFolderPermissionRepo = FolderPermissionRepo()
dashboard_repo: IDashboardRepo = DashboardRepo()


def update_task_success(task_result_id: str, result: Any):
    task_result_repo.update_fields(
        task_id=task_result_id,
        status=TaskStatus.SUCCESS,
        result=result,
        date_done=timezone.now(),
    )


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_folder(self, task_id: str, user_id: str, folder_name: str):
    """
    그라파나 유저 전용 폴더 생성 태스크
    """
    # 그라파나 API 호출
    result = grafana_api.create_folder(folder_name)

    folder = UserFolder(
        id=str(uuid.uuid4()),
        user_id=user_id,
        uid=result["uid"],
        name=result["title"],
        org_id=str(result.get("orgId")) if result.get("orgId") else None,
        created_by_task=task_id,
    )

    with transaction.atomic():
        folder_repo.save(folder)
        update_task_success(task_id, result)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_service_account(
    self, task_id: str, name: str, user_id: str, role: str = "Viewer"
):
    """
    그라파나 서비스 계정 생성 태스크
    """
    result = grafana_api.create_service_account(name, role)
    account = ServiceAccount(
        id=str(uuid.uuid4()),
        account_id=result["id"],
        user_id=user_id,
        name=result["name"],
        role=result["role"],
        is_disabled=result["isDisabled"],
    )
    with transaction.atomic():
        service_account_repo.save(account)
        update_task_success(task_id, result)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_service_token(
    self, task_id: str, service_account_id: int, token_name: str
):
    """
    그라파나 서비스 토큰 생성 태스크
    """
    result = grafana_api.create_service_token(service_account_id, token_name)

    with transaction.atomic():
        service_account_repo.update_token(
            account_id=int(service_account_id), token=result["key"]
        )
        update_task_success(task_id, result)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_set_grafana_folder_permissions(
    self, task_id: str, folder_uid: str, service_account_id: str
):
    """
    그라파나 폴더 권한 설정 태스크
    """
    result = grafana_api.set_folder_permissions(folder_uid, service_account_id)

    permission = FolderPermission(
        id=str(uuid.uuid4()),
        folder_uid=folder_uid,
        service_account_id=int(service_account_id),
        permission=FolderPermissionLevel.VIEW,
    )
    with transaction.atomic():
        folder_permission_repo.save(permission)
        update_task_success(task_id, result)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_dashboard(
    self,
    task_id: str,
    user_id: str,
    dashboard_title: str,
    dashboard_json_config: dict,
    folder_uid: str,
):
    """
    그라파나 대시보드 생성 태스크
    """
    result = grafana_api.create_dashboard(dashboard_json_config, folder_uid)

    dashboard = Dashboard(
        id=str(uuid.uuid4()),
        uid=result.get("uid"),
        title=dashboard_title,
        user_id=user_id,
        org_id=None,
        folder_uid=folder_uid,
        url=result.get("url"),
        config_json=dashboard_json_config,
        panels=[],
        tags=[],
        data_sources=[],
    )

    with transaction.atomic():
        dashboard_repo.save(dashboard)
        update_task_success(task_id, result)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_public_dashboard(self, task_id: str, dashboard_uid: str):
    """
    그라파나 퍼블릭 대시보드 생성 태스크
    """
    result = grafana_api.create_public_dashboard(dashboard_uid)

    # 성공 시 상태 업데이트
    update_task_success(task_id, result)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_get_grafana_dashboard(self, task_id: str, dashboard_uid: str):
    """
    그라파나 대시보드 조회 태스크
    """
    result = grafana_api.get_dashboard(dashboard_uid)

    # 성공 시 상태 업데이트
    update_task_success(task_id, result)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_get_grafana_folders(self, task_id: str):
    """
    view 권한을 가진 그라파나 폴더 목록 조회 태스크
    """
    result = grafana_api.get_folders()

    # 성공 시 상태 업데이트
    update_task_success(task_id, result)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def wrap_create_grafana_dashboard(
    self,
    task_id: str,
    dashboard_task_id: str,
    user_id: str,
    dashboard_title: str,
    dashboard_json_config: dict[str, Any],
):
    """
    user_id 로 Folder 엔티티를 조회해 folder_uid 를 얻고,
    dashboard_data 와 함께 실제 대시보드 생성 태스크를 호출
    """
    folder = folder_repo.find_by_user_id(user_id)
    if folder is None:
        raise RuntimeError(f"No Grafana folder for user {user_id}")

    async_res = task_create_grafana_dashboard.apply_async(
        args=(
            dashboard_task_id,
            user_id,
            dashboard_title,
            dashboard_json_config,
            folder.uid,
        ),
        task_id=dashboard_task_id,
    )
    return async_res.id


@locking_task(max_retries=3, default_retry_delay=2)
def wrap_create_grafana_public_dashboard(
    self,
    task_id: str,
    public_dashboard_task_id: str,
    user_id: str,
):
    """
    user_id 로 Dashboard 엔티티를 조회해 dashboard_uid 를 얻고,
    실제 퍼블릭 대시보드 생성 태스크를 호출
    """
    dashboard = dashboard_repo.find_by_user_id(user_id)
    if dashboard is None:
        raise RuntimeError(f"No Grafana dashboard for user {user_id}")

    async_res = task_create_grafana_public_dashboard.apply_async(
        args=(public_dashboard_task_id, dashboard.uid),
        task_id=public_dashboard_task_id,
    )
    return async_res.id


@locking_task(max_retries=3, default_retry_delay=2)
def wrap_create_service_token(
    self, task_id: str, token_task_id: str, user_id: str, token_name: str
):
    """
    user_id 로 ServiceAccount를 조회해 account_id를 얻고,
    token_name과 함께 실제 Celery 태스크를 호출
    """
    sa = service_account_repo.find_by_user_id(user_id)
    if sa is None:
        raise RuntimeError(f"No ServiceAccount for user {user_id}")

    async_res = task_create_grafana_service_token.apply_async(
        args=(token_task_id, sa.account_id, token_name), task_id=token_task_id
    )
    return async_res.id


@locking_task(max_retries=3, default_retry_delay=2)
def wrap_set_folder_permissions(self, task_id: str, perm_task_id: str, user_id: str):
    """
    user_id 로 UserFolder와 ServiceAccount를 조회해
    folder_uid, account_id를 얻고 실제 권한설정 태스크를 호출
    """
    folder = folder_repo.find_by_user_id(user_id)
    if folder is None:
        raise RuntimeError(f"No UserFolder for user {user_id}")

    sa = service_account_repo.find_by_user_id(user_id)
    if sa is None:
        raise RuntimeError(f"No ServiceAccount for user {user_id}")

    async_res = task_set_grafana_folder_permissions.apply_async(
        args=(perm_task_id, folder.uid, sa.account_id), task_id=perm_task_id
    )
    return async_res.id

import uuid
from typing import Any

from django.db import transaction

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
from monitoring.domain.visualization_platform.dashboard import (
    Dashboard,
    PublicDashboard,
)
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
    PublicDashboardRepo,
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
public_dashboard_repo: IPublicDashboardRepo = PublicDashboardRepo()


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

    folder_repo.save(folder)
    print(
        f"create folder for user {user_id}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    )
    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_service_account(
    self, task_id: str, project_id: str, name: str, user_id: str, role: str = "Viewer"
):
    """
    그라파나 서비스 계정 생성 태스크
    """
    result = grafana_api.create_service_account(name, role)
    account = ServiceAccount(
        id=str(uuid.uuid4()),
        account_id=str(result["id"]),
        project_id=project_id,
        user_id=user_id,
        name=result["name"],
        role=result["role"],
        is_disabled=result["isDisabled"],
    )
    service_account_repo.save(account)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_service_token(
    self, task_id: str, project_id: str, token_name: str
):
    """
    그라파나 서비스 토큰 생성 태스크
    """
    sa = service_account_repo.find_by_project_id(project_id)
    if sa is None:
        raise RuntimeError(f"No ServiceAccount for project {project_id}")
    result = grafana_api.create_service_token(sa.account_id, token_name)

    service_account_repo.update_token(
        account_id=str(sa.account_id), token=result["key"]
    )

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_set_grafana_folder_permissions(
    self, task_id: str, user_id: str, project_id: str
):
    """
    그라파나 폴더 권한 설정 태스크
    """
    folder = folder_repo.find_by_user_id(user_id)
    if folder is None:
        raise RuntimeError(f"No UserFolder for user {user_id}")

    sa = service_account_repo.find_by_project_id(project_id)
    if sa is None:
        raise RuntimeError(f"No ServiceAccount for project {project_id}")
    result = grafana_api.set_folder_permissions(folder.uid, sa.account_id)

    permission = FolderPermission(
        id=str(uuid.uuid4()),
        folder_uid=folder.uid,
        service_account_id=sa.account_id,
        permission=FolderPermissionLevel.VIEW,
    )

    folder_permission_repo.save(permission)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_dashboard(
    self,
    task_id: str,
    user_id: str,
    project_id: str,
    dashboard_title: str,
    dashboard_json_config: dict,
):
    """
    그라파나 대시보드 생성 태스크
    """
    folder = folder_repo.find_by_user_id(user_id)
    if folder is None:
        raise RuntimeError(f"No Grafana folder for user {user_id}")
    result = grafana_api.create_dashboard(dashboard_json_config, folder.uid)

    dashboard = Dashboard(
        id=str(uuid.uuid4()),
        uid=result.get("uid"),
        title=dashboard_title,
        user_id=user_id,
        org_id=None,
        folder_uid=folder.uid,
        url=result.get("url"),
        project_id=project_id,
        config_json=dashboard_json_config,
        panels=[
            {
                "id": 1,
                "type": "graph",
                "title": "CPU Usage",
                "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
            }
        ],
        tags=[],
        data_sources=[],
    )

    dashboard_repo.save(dashboard)
    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_create_grafana_public_dashboard(self, task_id: str, project_id: str):
    """
    그라파나 퍼블릭 대시보드 생성 태스크
    """
    dashboard = dashboard_repo.find_by_project_id(project_id)
    if dashboard is None:
        raise RuntimeError(f"No Grafana dashboard for project {project_id}")
    if dashboard.uid is None:
        raise RuntimeError(f"Dashboard UID is None for project {project_id}")

    result = grafana_api.create_public_dashboard(dashboard.uid)
    public_uid = result["uid"]
    public_url = result["publicUrl"]

    public_dashboard = PublicDashboard(
        id=str(uuid.uuid4()),
        uid=public_uid,
        dashboard_id=dashboard.id,
        project_id=project_id,
        public_url=public_url,
    )
    public_dashboard_repo.save(public_dashboard)
    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_get_grafana_dashboard(self, task_id: str, dashboard_uid: str):
    """
    그라파나 대시보드 조회 태스크
    """
    result = grafana_api.get_dashboard(dashboard_uid)

    return result


@locking_task(max_retries=3, default_retry_delay=2)
def task_get_grafana_folders(self, task_id: str):
    """
    view 권한을 가진 그라파나 폴더 목록 조회 태스크
    """
    result = grafana_api.get_folders()
    return result

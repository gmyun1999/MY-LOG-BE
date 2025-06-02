import logging

from django.db import transaction

from monitoring.domain.i_repo.i_monitoring_project_repo import IMonitoringProjectRepo
from monitoring.domain.i_repo.i_visualization_platform_repo.i_folder_repo import (
    IFolderRepo,
)
from monitoring.domain.monitoring_project import ProjectStatus
from monitoring.infra.celery.tasks.utils import locking_task
from monitoring.infra.repo.monitoring_project_repo import MonitoringProjectRepo
from monitoring.infra.repo.visualization_platform_repo.folder_repo import FolderRepo

logger = logging.getLogger(__name__)
project_repo: IMonitoringProjectRepo = MonitoringProjectRepo()
folder_repo: IFolderRepo = FolderRepo()


@locking_task(max_retries=0, default_retry_delay=0)
def finalize_monitoring_project(
    self, task_id: str, user_id: str, monitoring_project_id: str
):
    with transaction.atomic():
        user_folder = folder_repo.find_by_user_id(user_id)

        user_folder_id = None
        if user_folder:
            user_folder_id = user_folder.id

        project_repo.update_fields(
            project_id=monitoring_project_id,
            status=ProjectStatus.READY.value,
            user_folder_id=user_folder_id,
        )
    logger.info(f"[프로비저닝 완료] 프로젝트 {monitoring_project_id}")


@locking_task(max_retries=0, default_retry_delay=0)
def handle_monitoring_project_failure(self, task_id: str, monitoring_project_id: str):
    project_repo.update_fields(
        project_id=monitoring_project_id, status=ProjectStatus.FAILED.value
    )
    logger.error(f"[프로비저닝 실패] 프로젝트")

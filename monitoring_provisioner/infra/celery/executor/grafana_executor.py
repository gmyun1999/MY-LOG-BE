import uuid

from django.utils import timezone

from config.celery import TASK_QUEUE
from monitoring_provisioner.domain.task_result import TaskResult, TaskStatus
from monitoring_provisioner.infra.celery.tasks.grafana_tasks import (
    send_dashboard_creation_request,
)
from monitoring_provisioner.infra.repository.task_result_repo import (
    TaskResultRepository,
)
from monitoring_provisioner.service.i_executors.monitoring_dashboard_executor import (
    MonitoringDashboardExecutor,
)


class GrafanaExecutor(MonitoringDashboardExecutor):

    def __init__(self):
        self.task_result_repo = TaskResultRepository()

    def create_user_dir(self):
        # id, task_id, task_name, result, date_created, date_done, traceback, retries
        # TaskStatus.PENDING 등록
        # TaskResult 도메인 객체 생성
        # TaskResultRepository에 저장
        # grafana_tasks에서 send_user_dir_creation_request 호출
        pass

    def create_org_id(self):
        # 보류
        pass

    def create_dashboard(self) -> None:
        id = str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        now = timezone.now()

        task_result = TaskResult(
            id=id,
            task_id=task_id,
            task_name="send_dashboard_creation_request",
            status=TaskStatus.PENDING,
            result=None,
            date_created=now.isoformat(),
            date_started=None,
            date_done=None,
            traceback=None,
            retries=0,
        )
        saved_result = self.task_result_repo.save(task_result)

        send_dashboard_creation_request.apply_async(
            args=(saved_result.id,), task_id=saved_result.task_id
        )

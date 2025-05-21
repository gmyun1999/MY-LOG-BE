from celery.exceptions import Ignore
from celery.signals import task_failure, task_prerun
from django.utils import timezone

from monitoring_provisioner.domain.i_repo.i_task_result_repo import ITaskResultRepo
from monitoring_provisioner.domain.task_result import TaskStatus
from monitoring_provisioner.infra.repo.task_result_repo import TaskResultRepo

repo: ITaskResultRepo = TaskResultRepo()


@task_prerun.connect
def pre_task_handler(sender=None, task_id=None, task=None, args=None, **kwargs):
    task_result_id = args[0]

    print(f"task {task_id} started ")
    task_result = repo.find_by_task_id(task_result_id)
    if task_result is None:
        if task and hasattr(task.request, "acknowledge"):
            task.request.acknowledge()
        raise Ignore()

    if task_result.status == TaskStatus.SUCCESS:
        print(f"task {task_id} already succeeded")
        if task and hasattr(task.request, "acknowledge"):
            task.request.acknowledge()
        raise Ignore(f"{task_result_id} already succeeded")

    if task_result.status == TaskStatus.FAILURE:
        if task and hasattr(task.request, "acknowledge"):
            task.request.acknowledge()
        raise Ignore(f"{task_result_id} already failed")

    if task_result.status == TaskStatus.PENDING:
        task_result.status = TaskStatus.STARTED
        task_result.date_started = timezone.now()  # datetime 객체
        task_result.date_done = None
        repo.update(task_result)
        print(f"task {task_id} status updated to STARTED")
        return

    if task_result.status == TaskStatus.STARTED:
        return


@task_failure.connect  # task에서의 에러만 처리 (signal에서의 에러는 처리 안함)
def mark_failure(
    sender=None,
    task_id=None,
    args=None,
    kwargs=None,
    exception=None,
    traceback=None,
    einfo=None,
    **_kwargs,
):
    task_result_id = args[0]
    retries = getattr(sender.request, "retries", 0)
    print(f"task {task_id} failed with exception: {exception}")
    repo.update_fields(
        task_id=task_result_id,
        status=TaskStatus.FAILURE,
        traceback=str(exception),
        retries=retries,
        date_done=timezone.now(),
    )

from django.utils import timezone
from celery.signals import task_prerun, task_failure
from celery.exceptions import Ignore

from monitoring_provisioner.domain.task_result import  TaskStatus
from monitoring_provisioner.infra.models.task_result_model import TaskResultModel   

@task_prerun.connect
def pre_task_handler(sender=None, task_id=None, task=None, args=None, **kwargs):

    task_result_id = args[0]
    try:
        tr = TaskResultModel.objects.get(id=task_result_id)
    except TaskResultModel.DoesNotExist:
        # 결과 레코드가 없으면 논리 오류이므로 스킵
        if task and hasattr(task.request, "acknowledge"):
            task.request.acknowledge()
        raise Ignore()

    print("tr.status:", tr.status)
    # 1) 이미 성공한 작업: 중복 방지
    if tr.status == TaskStatus.SUCCESS:
        print("이미 성공한 작업")
        if task and hasattr(task.request, "acknowledge"):
            task.request.acknowledge()
        raise Ignore(f"{task_result_id} already succeeded")

    # 2) 이미 실패 처리된 작업: 재큐된 실패 재시도 무시
    if tr.status == TaskStatus.FAILURE:
        print("이미 실패한 작업")
        if task and hasattr(task.request, "acknowledge"):
            task.request.acknowledge()
        raise Ignore(f"{task_result_id} already failed")

    # 3) 최초 실행 대기 중인 작업: STARTED로 전환
    if tr.status == TaskStatus.PENDING:
        print("최초 대기중임.")
        tr.status = TaskStatus.STARTED
        tr.date_done = None
        tr.date_started = timezone.now()
        tr.save(update_fields=['status', 'date_started', 'date_done'])
        print("tr.status:", tr.status)
        return

    # 4) STARTED 상태(재시도 중 or 워커 크래시 후 재큐): 그대로 진행
    if tr.status == TaskStatus.STARTED:
        print("재시도 중 또는 워커 크래시 후 재큐")
        return


@task_failure.connect # task에서의 에러만 처리 (signal에서의 에러는 처리 안함)
def mark_failure(
    sender=None, task_id=None, args=None, kwargs=None,
    exception=None, traceback=None, einfo=None, **_kwargs
):
    task_result_id = args[0]
    retries = getattr(sender.request, "retries", 0)
    TaskResultModel.objects.filter(id=task_result_id).update(
        status=TaskStatus.FAILURE,
        traceback=str(exception),
        retries=retries,
        date_done=timezone.now(),
    )
    print("실패 처리 완료")
